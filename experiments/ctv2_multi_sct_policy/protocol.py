from __future__ import annotations
import hashlib,hmac,json
from dataclasses import dataclass
from enum import Enum
class PolicyError(ValueError): pass
class StalePolicy(PolicyError): pass
class StaleTrust(PolicyError): pass
class ForgedEvidence(PolicyError): pass
class PromiseStatus(str,Enum):
 FULFILLED='FULFILLED'; NOT_YET_AUDITABLE='NOT_YET_AUDITABLE'; INCONCLUSIVE_AFTER_DEADLINE='INCONCLUSIVE_AFTER_DEADLINE'; MMD_VIOLATION='MMD_VIOLATION'
class ComplianceStatus(str,Enum):
 COMPLIANT='COMPLIANT'; PENDING='PENDING'; INCONCLUSIVE='INCONCLUSIVE'; VIOLATION='VIOLATION'; NONCOMPLIANT='NONCOMPLIANT'
@dataclass(frozen=True)
class Policy:
 schema_version:int; policy_generation:int; trust_generation:int; required_logs:int; required_operators:int=0
 def validate(self):
  vals=(self.schema_version,self.policy_generation,self.trust_generation,self.required_logs,self.required_operators)
  if any(type(v) is not int for v in vals): raise PolicyError('policy integers must be strict ints')
  if self.schema_version!=1: raise PolicyError('unsupported policy schema')
  if min(self.policy_generation,self.trust_generation,self.required_logs)<1 or self.required_operators<0: raise PolicyError('invalid policy values')
@dataclass(frozen=True)
class TrustedLog: log_id:str; operator_id:str; trust_generation:int; evidence_key:bytes
@dataclass(frozen=True)
class AuditEvidence: log_id:str; leaf_id:str; status:PromiseStatus; trust_generation:int; audit_id:str; authenticator:str
@dataclass(frozen=True)
class Decision:
 status:ComplianceStatus; fulfilled_logs:tuple[str,...]; fulfilled_operators:tuple[str,...]; pending_logs:tuple[str,...]; inconclusive_logs:tuple[str,...]; violation_logs:tuple[str,...]; ignored_unknown_logs:tuple[str,...]
def _payload(log_id,leaf_id,status,trust_generation,audit_id):
 return json.dumps({'audit_id':audit_id,'leaf_id':leaf_id,'log_id':log_id,'status':status.value,'trust_generation':trust_generation},sort_keys=True,separators=(',',':')).encode()
def issue_evidence(log,leaf_id,status,audit_id):
 p=_payload(log.log_id,leaf_id,status,log.trust_generation,audit_id); mac=hmac.new(log.evidence_key,p,hashlib.sha256).hexdigest(); return AuditEvidence(log.log_id,leaf_id,status,log.trust_generation,audit_id,mac)
def _verify(ev,log,leaf,tg):
 if ev.log_id!=log.log_id or ev.leaf_id!=leaf: raise ForgedEvidence('evidence binding mismatch')
 if ev.trust_generation!=tg or log.trust_generation!=tg: raise StaleTrust('stale evidence/log trust generation')
 p=_payload(ev.log_id,ev.leaf_id,ev.status,ev.trust_generation,ev.audit_id)
 if not hmac.compare_digest(ev.authenticator,hmac.new(log.evidence_key,p,hashlib.sha256).hexdigest()): raise ForgedEvidence('audit object is not authenticated')
def evaluate(policy,*,current_policy_generation,current_trust_generation,trusted_logs,expected_leaf_id,evidence):
 policy.validate()
 if policy.policy_generation!=current_policy_generation: raise StalePolicy('stale policy generation')
 if policy.trust_generation!=current_trust_generation: raise StaleTrust('stale policy trust generation')
 accepted={}; unknown=set()
 for ev in evidence:
  log=trusted_logs.get(ev.log_id)
  if log is None: unknown.add(ev.log_id); continue
  _verify(ev,log,expected_leaf_id,current_trust_generation)
  prev=accepted.get(ev.log_id)
  if prev is not None and (prev.audit_id!=ev.audit_id or prev.status!=ev.status): raise ForgedEvidence('conflicting authoritative evidence for one LogID')
  accepted[ev.log_id]=ev
 fulfilled=sorted(k for k,v in accepted.items() if v.status is PromiseStatus.FULFILLED); pending=sorted(k for k,v in accepted.items() if v.status is PromiseStatus.NOT_YET_AUDITABLE); inconclusive=sorted(k for k,v in accepted.items() if v.status is PromiseStatus.INCONCLUSIVE_AFTER_DEADLINE); violations=sorted(k for k,v in accepted.items() if v.status is PromiseStatus.MMD_VIOLATION); operators=sorted({trusted_logs[k].operator_id for k in fulfilled})
 enough=len(fulfilled)>=policy.required_logs and len(operators)>=policy.required_operators
 status=ComplianceStatus.VIOLATION if violations else ComplianceStatus.COMPLIANT if enough else ComplianceStatus.INCONCLUSIVE if inconclusive else ComplianceStatus.PENDING if pending else ComplianceStatus.NONCOMPLIANT
 return Decision(status,tuple(fulfilled),tuple(operators),tuple(pending),tuple(inconclusive),tuple(violations),tuple(sorted(unknown)))
def unsafe_count_claims(required,evidence): return sum(1 for x in evidence if x.get('status')=='FULFILLED')>=required
