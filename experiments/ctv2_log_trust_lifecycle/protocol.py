from __future__ import annotations
import hashlib,hmac,json
from dataclasses import dataclass
from enum import Enum
from typing import Iterable
class TrustError(ValueError): pass
class SnapshotAuthError(TrustError): pass
class SnapshotRollback(TrustError): pass
class SnapshotSubstitution(TrustError): pass
class SnapshotMalformed(TrustError): pass
class SnapshotBindingError(TrustError): pass
class ImmutableProfileError(TrustError): pass
class LogState(str,Enum): ACTIVE='ACTIVE'; RETIRED='RETIRED'; DISTRUSTED='DISTRUSTED'
@dataclass(frozen=True)
class Operator: operator_id:str; name:str
@dataclass(frozen=True)
class LogEntry: log_id:str; verification_profile:str; operator_id:str; state:LogState; state_since:int
@dataclass(frozen=True)
class SignedSnapshot:
 schema_version:int; version:int; generation:int; issued_at:int; expires_at:int; operators:tuple[Operator,...]; logs:tuple[LogEntry,...]; signer_id:str; authenticator:str
 @property
 def snapshot_id(self): return hashlib.sha256(canonical_payload(self)).hexdigest()
@dataclass(frozen=True)
class Evidence: log_id:str; status:str
@dataclass(frozen=True)
class Policy:
 required_logs:int; required_operators:int
 def validate(self):
  if type(self.required_logs) is not int or type(self.required_operators) is not int: raise SnapshotMalformed('policy thresholds must be strict ints')
  if self.required_logs<1 or self.required_operators<0: raise SnapshotMalformed('invalid policy thresholds')
@dataclass(frozen=True)
class Decision:
 compliant:bool; snapshot_id:str; snapshot_version:int; snapshot_generation:int; fulfilled_logs:tuple[str,...]; fulfilled_operators:tuple[str,...]; ignored_logs:tuple[str,...]
def _operator_dict(o): return {'operator_id':o.operator_id,'name':o.name}
def _log_dict(l): return {'log_id':l.log_id,'verification_profile':l.verification_profile,'operator_id':l.operator_id,'state':l.state.value,'state_since':l.state_since}
def unsigned_dict(s): return {'schema_version':s.schema_version,'version':s.version,'generation':s.generation,'issued_at':s.issued_at,'expires_at':s.expires_at,'operators':[_operator_dict(x) for x in sorted(s.operators,key=lambda x:x.operator_id)],'logs':[_log_dict(x) for x in sorted(s.logs,key=lambda x:x.log_id)],'signer_id':s.signer_id}
def canonical_payload(s): return json.dumps(unsigned_dict(s),sort_keys=True,separators=(',',':')).encode()
def root_id(root_key): return hashlib.sha256(root_key).hexdigest()[:16]
def validate_structure(s):
 if type(s.schema_version) is not int or s.schema_version!=1: raise SnapshotMalformed('unsupported schema')
 for name in ('version','generation','issued_at','expires_at'):
  v=getattr(s,name)
  if type(v) is not int or v<1: raise SnapshotMalformed(f'invalid {name}')
 if s.expires_at<=s.issued_at: raise SnapshotMalformed('snapshot expiry must follow issue time')
 if not s.signer_id: raise SnapshotMalformed('missing signer')
 op_ids=[o.operator_id for o in s.operators]
 if len(op_ids)!=len(set(op_ids)): raise SnapshotMalformed('duplicate operator id')
 if any(not o.operator_id or not o.name for o in s.operators): raise SnapshotMalformed('malformed operator')
 known=set(op_ids); log_ids=[l.log_id for l in s.logs]
 if len(log_ids)!=len(set(log_ids)): raise SnapshotMalformed('duplicate LogID')
 for l in s.logs:
  if not l.log_id or not l.verification_profile: raise SnapshotMalformed('malformed log')
  if l.operator_id not in known: raise SnapshotMalformed('log references unknown operator')
  if type(l.state_since) is not int or l.state_since<1 or l.state_since>s.issued_at: raise SnapshotMalformed('invalid lifecycle timestamp')
  if not isinstance(l.state,LogState): raise SnapshotMalformed('invalid lifecycle state')
def sign_snapshot(root_key,*,version,generation,issued_at,expires_at,operators,logs):
 d=SignedSnapshot(1,version,generation,issued_at,expires_at,tuple(operators),tuple(logs),root_id(root_key),''); validate_structure(d)
 return SignedSnapshot(**{**d.__dict__,'authenticator':hmac.new(root_key,canonical_payload(d),hashlib.sha256).hexdigest()})
def verify_snapshot(s,root_key):
 validate_structure(s)
 if s.signer_id!=root_id(root_key): raise SnapshotAuthError('wrong trust root')
 exp=hmac.new(root_key,canonical_payload(s),hashlib.sha256).hexdigest()
 if not hmac.compare_digest(exp,s.authenticator): raise SnapshotAuthError('snapshot authentication failed')
class TrustLifecycle:
 def __init__(self,root_key): self.root_key=root_key; self.current=None; self.history={}
 def accept(self,s,*,now=None):
  verify_snapshot(s,self.root_key)
  if now is not None:
   if type(now) is not int: raise SnapshotMalformed('now must be strict int')
   if now>s.expires_at: raise SnapshotRollback('expired/frozen trust snapshot')
  cur=self.current
  if cur is not None:
   if s.version<cur.version or s.generation<cur.generation or s.issued_at<cur.issued_at: raise SnapshotRollback('stale trust snapshot')
   same=(s.version==cur.version and s.generation==cur.generation and s.issued_at==cur.issued_at)
   if same:
    if s.snapshot_id!=cur.snapshot_id: raise SnapshotSubstitution('same coordinates, different authenticated content')
    return cur
   if s.version<=cur.version or s.generation<=cur.generation: raise SnapshotRollback('version/generation must advance together')
   old={x.log_id:x for x in cur.logs}
   for new in s.logs:
    prev=old.get(new.log_id)
    if prev is not None and prev.verification_profile!=new.verification_profile: raise ImmutableProfileError('LogID verification profile changed')
    if prev is not None and prev.state is not LogState.ACTIVE and new.state is LogState.ACTIVE: raise SnapshotMalformed('inactive log cannot silently reactivate')
  self.current=s; self.history[s.snapshot_id]=s; return s
 def get(self,snapshot_id):
  if snapshot_id not in self.history: raise SnapshotBindingError('unknown historical snapshot')
  return self.history[snapshot_id]
def evaluate(policy,snapshot,*,expected_snapshot_id,evidence):
 policy.validate()
 if snapshot.snapshot_id!=expected_snapshot_id: raise SnapshotBindingError('policy evaluation is not bound to exact trust snapshot')
 logs={l.log_id:l for l in snapshot.logs}; accepted={}; ignored=set()
 for ev in evidence:
  entry=logs.get(ev.log_id)
  if entry is None or entry.state is not LogState.ACTIVE: ignored.add(ev.log_id); continue
  if ev.status!='FULFILLED': continue
  accepted[ev.log_id]=ev
 fulfilled=tuple(sorted(accepted)); operators=tuple(sorted({logs[x].operator_id for x in fulfilled}))
 return Decision(len(fulfilled)>=policy.required_logs and len(operators)>=policy.required_operators,snapshot.snapshot_id,snapshot.version,snapshot.generation,fulfilled,operators,tuple(sorted(ignored)))
def unsafe_evaluate(required_logs,required_operators,caller_claims):
 fulfilled=[x for x in caller_claims if x.get('trusted') and x.get('status')=='FULFILLED']
 return len({x['log_id'] for x in fulfilled})>=required_logs and len({x['operator_id'] for x in fulfilled})>=required_operators
