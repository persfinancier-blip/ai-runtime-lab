from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Iterable

class TemporalError(ValueError): pass
class Malformed(TemporalError): pass
class FreezeOrRollback(TemporalError): pass
class SnapshotCherryPick(TemporalError): pass
class HistoryConflict(TemporalError): pass

class LogState(str, Enum):
    ACTIVE='ACTIVE'; RETIRED='RETIRED'; DISTRUSTED='DISTRUSTED'

class EvaluationMode(str, Enum):
    HISTORICAL='HISTORICAL'; CURRENT_POLICY='CURRENT_POLICY'

@dataclass(frozen=True)
class SnapshotLog:
    log_id:str; verification_profile:str; operator_id:str; operator_since:int; state:LogState; state_since:int

@dataclass(frozen=True)
class AuthenticatedSnapshot:
    snapshot_id:str; version:int; generation:int; issued_at:int; expires_at:int; logs:tuple[SnapshotLog,...]

@dataclass(frozen=True)
class Evidence:
    log_id:str; status:str; evidence_time:int

@dataclass(frozen=True)
class Policy:
    required_logs:int; required_operators:int; mode:EvaluationMode
    def validate(self):
        if type(self.required_logs) is not int or type(self.required_operators) is not int:
            raise Malformed('strict integer thresholds required')
        if self.required_logs < 1 or self.required_operators < 0:
            raise Malformed('invalid thresholds')
        if not isinstance(self.mode, EvaluationMode):
            raise Malformed('invalid evaluation mode')

@dataclass(frozen=True)
class Interval:
    start_inclusive:int; end_exclusive:int|None; value:str
    def contains(self,t:int)->bool:
        return t >= self.start_inclusive and (self.end_exclusive is None or t < self.end_exclusive)

@dataclass(frozen=True)
class LogTemporalView:
    log_id:str; verification_profile:str; state_intervals:tuple[Interval,...]; operator_intervals:tuple[Interval,...]

@dataclass(frozen=True)
class Decision:
    compliant:bool; mode:str; policy_time:int; authority_snapshot_id:str; authority_snapshot_version:int; authority_snapshot_generation:int
    fulfilled_logs:tuple[str,...]; fulfilled_operators:tuple[str,...]; ignored:tuple[tuple[str,str],...]; evidence_times:tuple[tuple[str,int],...]

class AuthenticatedLifecycleHistory:
    def __init__(self): self._snapshots:list[AuthenticatedSnapshot]=[]
    @property
    def snapshots(self): return tuple(self._snapshots)
    def add_accepted(self,s:AuthenticatedSnapshot):
        self._validate_snapshot(s)
        if self._snapshots:
            cur=self._snapshots[-1]
            if s.version <= cur.version or s.generation <= cur.generation or s.issued_at <= cur.issued_at:
                raise FreezeOrRollback('accepted history coordinates must strictly advance')
            old={x.log_id:x for x in cur.logs}
            for item in s.logs:
                prev=old.get(item.log_id)
                if prev and prev.verification_profile != item.verification_profile:
                    raise HistoryConflict('immutable verification profile changed')
        self._snapshots.append(s)
    def _validate_snapshot(self,s):
        for name in ('version','generation','issued_at','expires_at'):
            v=getattr(s,name)
            if type(v) is not int or v < 1: raise Malformed(f'invalid {name}')
        if s.expires_at <= s.issued_at or not s.snapshot_id: raise Malformed('invalid snapshot')
        seen=set()
        for x in s.logs:
            if x.log_id in seen: raise Malformed('duplicate log')
            seen.add(x.log_id)
            if not x.log_id or not x.verification_profile or not x.operator_id: raise Malformed('bad log')
            if type(x.operator_since) is not int or x.operator_since < 1 or x.operator_since > s.issued_at: raise Malformed('bad operator timestamp')
            if type(x.state_since) is not int or x.state_since < 1 or x.state_since > s.issued_at: raise Malformed('bad state timestamp')
            if not isinstance(x.state,LogState): raise Malformed('bad state')
    def authority_for(self,policy_time:int)->AuthenticatedSnapshot:
        if type(policy_time) is not int or policy_time < 1: raise Malformed('policy_time must be strict positive int')
        candidates=[s for s in self._snapshots if s.issued_at <= policy_time]
        if not candidates: raise FreezeOrRollback('no authenticated trust snapshot by policy time')
        authority=candidates[-1]
        if policy_time > authority.expires_at: raise FreezeOrRollback('trust metadata frozen/expired at policy time')
        return authority
    def require_authority(self,policy_time:int,snapshot_id:str|None=None)->AuthenticatedSnapshot:
        authority=self.authority_for(policy_time)
        if snapshot_id is not None and snapshot_id != authority.snapshot_id:
            raise SnapshotCherryPick('caller attempted to select non-authoritative historical snapshot')
        return authority
    def _prefix(self,authority): return [s for s in self._snapshots if s.issued_at <= authority.issued_at]
    def compile_log(self,authority:AuthenticatedSnapshot,log_id:str)->LogTemporalView|None:
        observations=[]; profile=None
        for s in self._prefix(authority):
            item=next((x for x in s.logs if x.log_id==log_id),None)
            if not item: continue
            if profile is None: profile=item.verification_profile
            elif profile != item.verification_profile: raise HistoryConflict('profile changed')
            observations.append((s,item))
        if not observations: return None
        state_events={}
        for s,item in observations:
            existing=state_events.get(item.state_since); val=item.state.value
            if existing is not None and existing != val: raise HistoryConflict('conflicting lifecycle event at same timestamp')
            state_events[item.state_since]=val
        op_events={}
        for s,item in observations:
            existing=op_events.get(item.operator_since)
            if existing is not None and existing != item.operator_id: raise HistoryConflict('conflicting operator event at same timestamp')
            op_events[item.operator_since]=item.operator_id
        return LogTemporalView(log_id,profile,tuple(_intervals(state_events)),tuple(_intervals(op_events)))

def _intervals(events:dict[int,str])->list[Interval]:
    ordered=sorted(events.items()); out=[]
    for i,(start,value) in enumerate(ordered):
        end=ordered[i+1][0] if i+1<len(ordered) else None
        if end is not None and end <= start: raise HistoryConflict('non increasing interval')
        out.append(Interval(start,end,value))
    return out

def _at(intervals:Iterable[Interval],t:int)->str|None:
    for x in intervals:
        if x.contains(t): return x.value
    return None

def evaluate(history:AuthenticatedLifecycleHistory,policy:Policy,*,policy_time:int,evidence:Iterable[Evidence],requested_snapshot_id:str|None=None)->Decision:
    policy.validate(); authority=history.require_authority(policy_time,requested_snapshot_id)
    fulfilled={}; operators=set(); ignored=[]; evidence_times=[]
    for ev in evidence:
        if type(ev.evidence_time) is not int or ev.evidence_time < 1: raise Malformed('invalid evidence time')
        if ev.evidence_time > policy_time: raise Malformed('evidence_time cannot be after policy_time')
        evidence_times.append((ev.log_id,ev.evidence_time))
        if ev.status != 'FULFILLED': ignored.append((ev.log_id,'status_not_fulfilled')); continue
        view=history.compile_log(authority,ev.log_id)
        if view is None: ignored.append((ev.log_id,'unknown_log')); continue
        lifecycle_time=ev.evidence_time if policy.mode is EvaluationMode.HISTORICAL else policy_time
        state=_at(view.state_intervals,lifecycle_time)
        if state != LogState.ACTIVE.value: ignored.append((ev.log_id,f'ineligible_at_{lifecycle_time}')); continue
        operator=_at(view.operator_intervals,ev.evidence_time)
        if operator is None: ignored.append((ev.log_id,'operator_unknown_at_evidence_time')); continue
        fulfilled[ev.log_id]=ev; operators.add(operator)
    logs=tuple(sorted(fulfilled)); ops=tuple(sorted(operators))
    return Decision(len(logs)>=policy.required_logs and len(ops)>=policy.required_operators,policy.mode.value,policy_time,authority.snapshot_id,authority.version,authority.generation,logs,ops,tuple(sorted(ignored)),tuple(sorted(evidence_times)))

def unsafe_current_snapshot_evaluate(snapshot:AuthenticatedSnapshot,required_logs:int,evidence:Iterable[Evidence])->bool:
    current={x.log_id:x for x in snapshot.logs}
    good={ev.log_id for ev in evidence if ev.status=='FULFILLED' and ev.log_id in current and current[ev.log_id].state is LogState.ACTIVE}
    return len(good)>=required_logs
