from __future__ import annotations
import hashlib, json
from dataclasses import dataclass
from typing import Iterable
from experiments.ctv2_temporal_log_eligibility.protocol import AuthenticatedLifecycleHistory, Evidence, EvaluationMode, Policy, Decision as TrustDecision, FreezeOrRollback, evaluate as evaluate_trust
class PolicyError(ValueError): pass
class PolicyRollback(PolicyError): pass
class PolicySubstitution(PolicyError): pass
class PolicyIntervalConflict(PolicyError): pass
class PolicyCompatibilityError(PolicyError): pass
class ReplayMismatch(PolicyError): pass
def _pos(n,v):
    if type(v) is not int or v<1: raise PolicyError(f'invalid {n}')
@dataclass(frozen=True)
class PolicySnapshot:
    policy_id:str; version:int; generation:int; issued_at:int; expires_at:int; effective_from:int; effective_until:int|None
    required_logs:int; required_operators:int; mode:EvaluationMode; trust_generation_min:int; trust_generation_max:int|None
    def validate(self):
        if not self.policy_id: raise PolicyError('missing id')
        for n in ('version','generation','issued_at','expires_at','effective_from','required_logs','trust_generation_min'): _pos(n,getattr(self,n))
        if type(self.required_operators) is not int or self.required_operators<0: raise PolicyError('operators')
        if self.expires_at<=self.issued_at: raise PolicyError('expiry')
        if self.effective_until is not None and (type(self.effective_until) is not int or self.effective_until<=self.effective_from): raise PolicyError('interval')
        if self.trust_generation_max is not None and (type(self.trust_generation_max) is not int or self.trust_generation_max<self.trust_generation_min): raise PolicyError('trust range')
        if not isinstance(self.mode,EvaluationMode): raise PolicyError('mode')
    @property
    def content_digest(self):
        b={'policy_id':self.policy_id,'version':self.version,'generation':self.generation,'issued_at':self.issued_at,'expires_at':self.expires_at,'effective_from':self.effective_from,'effective_until':self.effective_until,'required_logs':self.required_logs,'required_operators':self.required_operators,'mode':self.mode.value,'trust_generation_min':self.trust_generation_min,'trust_generation_max':self.trust_generation_max}
        return hashlib.sha256(json.dumps(b,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    def active_at(self,t): return t>=self.effective_from and (self.effective_until is None or t<self.effective_until)
    def compatible(self,g): return g>=self.trust_generation_min and (self.trust_generation_max is None or g<=self.trust_generation_max)
@dataclass(frozen=True)
class ComplianceDecision:
    compliant:bool; policy_time:int; policy_snapshot_id:str; policy_version:int; policy_generation:int; policy_digest:str; policy_effective_from:int; policy_effective_until:int|None
    trust_snapshot_id:str; trust_version:int; trust_generation:int; fulfilled_logs:tuple[str,...]; fulfilled_operators:tuple[str,...]; ignored:tuple[tuple[str,str],...]; evidence_times:tuple[tuple[str,int],...]
class AuthenticatedPolicyHistory:
    def __init__(self): self._snapshots=[]
    @property
    def snapshots(self): return tuple(self._snapshots)
    def add_accepted(self,s):
        s.validate()
        if self._snapshots:
            c=self._snapshots[-1]
            if s.policy_id != c.policy_id: raise PolicySubstitution('policy lineage changed')
            if s.version<=c.version or s.generation<=c.generation or s.issued_at<=c.issued_at: raise PolicyRollback()
            if s.effective_from<c.effective_from: raise PolicyRollback()
            if c.effective_until is None or c.effective_until!=s.effective_from: raise PolicyIntervalConflict()
        self._snapshots.append(s)
    def authority_for(self,t):
        _pos('policy_time',t)
        c=[s for s in self._snapshots if s.issued_at<=t and s.active_at(t)]
        if not c: raise FreezeOrRollback()
        a=c[-1]
        if t>a.expires_at: raise FreezeOrRollback()
        return a
    def by_identity(self,pid,v,g,digest):
        c=[s for s in self._snapshots if s.policy_id==pid and s.version==v and s.generation==g]
        if len(c)!=1: raise ReplayMismatch('identity')
        if c[0].content_digest!=digest: raise PolicySubstitution()
        return c[0]
def evaluate(history,trust_history,*,policy_time,evidence):
    ps=history.authority_for(policy_time); ts=trust_history.authority_for(policy_time)
    if not ps.compatible(ts.generation): raise PolicyCompatibilityError()
    d=evaluate_trust(trust_history,Policy(ps.required_logs,ps.required_operators,ps.mode),policy_time=policy_time,evidence=tuple(evidence),requested_snapshot_id=ts.snapshot_id)
    return ComplianceDecision(d.compliant,policy_time,ps.policy_id,ps.version,ps.generation,ps.content_digest,ps.effective_from,ps.effective_until,d.authority_snapshot_id,d.authority_snapshot_version,d.authority_snapshot_generation,d.fulfilled_logs,d.fulfilled_operators,d.ignored,d.evidence_times)
def replay(decision,history,trust_history,evidence):
    ps=history.by_identity(decision.policy_snapshot_id,decision.policy_version,decision.policy_generation,decision.policy_digest)
    if not ps.active_at(decision.policy_time): raise ReplayMismatch('not effective')
    ts=trust_history.require_authority(decision.policy_time,decision.trust_snapshot_id)
    if (ts.version,ts.generation)!=(decision.trust_version,decision.trust_generation): raise ReplayMismatch('trust changed')
    fresh=evaluate(history,trust_history,policy_time=decision.policy_time,evidence=tuple(evidence))
    if fresh!=decision: raise ReplayMismatch('decision mismatch')
    return fresh
def unsafe_evaluate(caller_policy,trust_history,*,policy_time,evidence):
    return evaluate_trust(trust_history,caller_policy,policy_time=policy_time,evidence=tuple(evidence)).compliant
