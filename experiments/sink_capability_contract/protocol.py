from __future__ import annotations
from dataclasses import asdict, dataclass
from typing import Literal
import hashlib, hmac, json
Policy = Literal['SAFE_RETRY_RECONCILE','SAFE_RETRY_IDEMPOTENT_ONLY','NO_AUTOMATIC_RETRY','READ_ONLY']
class ContractError(RuntimeError): pass
class StaleCapability(ContractError): pass
class RequestMismatch(ContractError): pass
class UnknownOutcome(ContractError): pass
class UnsafeRetryBlocked(ContractError): pass
class UntrustedCapability(ContractError): pass
class ClockRollback(ContractError): pass
def canon(o): return json.dumps(o,sort_keys=True,separators=(',',':')).encode()
def sha(o): return hashlib.sha256(canon(o)).hexdigest()
@dataclass(frozen=True)
class CapabilityClaim:
    sink_id:str; generation:int; mutating:bool; stable_idempotency_key:bool; request_bound_key:bool; reconcile_by_key:bool; retention_seconds:int|None; source:str
    def validate(self):
        if not self.sink_id or type(self.generation) is not int or self.generation<1: raise ContractError('identity')
        if type(self.mutating) is not bool: raise ContractError('mutating')
        for v in (self.stable_idempotency_key,self.request_bound_key,self.reconcile_by_key):
            if type(v) is not bool: raise ContractError('boolean capability')
        if self.retention_seconds is not None and (type(self.retention_seconds) is not int or self.retention_seconds<1): raise ContractError('retention')
        if not self.source: raise ContractError('source')
@dataclass(frozen=True)
class CapabilityAttestation:
    claim_digest:str; probe_generation:int; issuer_id:str; signature:str
@dataclass(frozen=True)
class VerifiedCapability:
    claim:CapabilityClaim; attestation:CapabilityAttestation
class SimulatedSink:
    def __init__(self,*,idempotent,request_bound,reconcile):
        self.idempotent=idempotent; self.request_bound=request_bound; self.reconcile_supported=reconcile; self.effects=[]; self.by_key={}
    def apply(self,key,request,*,timeout_after_commit=False):
        d=sha(request)
        if self.idempotent and key in self.by_key:
            od,r=self.by_key[key]
            if self.request_bound and od!=d: raise RequestMismatch()
            return r
        r=f'receipt-{len(self.effects)+1}'; self.effects.append((key,d,r))
        if self.idempotent: self.by_key[key]=(d,r)
        if timeout_after_commit: raise UnknownOutcome()
        return r
    def reconcile(self,key):
        if not self.reconcile_supported: raise UnsafeRetryBlocked()
        row=self.by_key.get(key); return None if row is None else row[1]
class ProbeAuthority:
    def __init__(self,*,issuer_id,key,generation):
        if not issuer_id or not key or type(generation) is not int or generation<1: raise ValueError('probe authority')
        self.issuer_id=issuer_id; self.__key=bytes(key); self.generation=generation
    @staticmethod
    def _probe(claim,sink):
        claim.validate()
        if not claim.mutating: return True
        key=f'probe:{claim.sink_id}:{claim.generation}'; request={'probe':'same'}; changed={'probe':'changed'}
        try:
            first=sink.apply(key,request); second=sink.apply(key,request)
        except Exception: return False
        observed=first==second and len(sink.effects)==1
        if claim.stable_idempotency_key and not observed: return False
        if claim.request_bound_key:
            try: sink.apply(key,changed)
            except RequestMismatch: pass
            else: return False
        if claim.reconcile_by_key:
            try:
                if sink.reconcile(key)!=first: return False
            except Exception: return False
        return True
    def attest(self,claim,sink):
        if not self._probe(claim,sink): raise UntrustedCapability('behavioral probe failed')
        d=sha(asdict(claim)); body={'claim_digest':d,'probe_generation':self.generation,'issuer_id':self.issuer_id}
        sig=hmac.new(self.__key,canon(body),hashlib.sha256).hexdigest()
        return CapabilityAttestation(d,self.generation,self.issuer_id,sig)
    def verify(self,capability):
        claim=capability.claim; claim.validate(); att=capability.attestation
        d=sha(asdict(claim)); body={'claim_digest':d,'probe_generation':att.probe_generation,'issuer_id':att.issuer_id}
        if att.issuer_id!=self.issuer_id or att.probe_generation!=self.generation: raise UntrustedCapability('stale/wrong probe authority')
        if att.claim_digest!=d: raise UntrustedCapability('claim substitution')
        expected=hmac.new(self.__key,canon(body),hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected,att.signature): raise UntrustedCapability('invalid probe attestation')
        return claim
def derive_policy(capability,verifier,*,now,key_created_at=None):
    if type(now) is not int or (key_created_at is not None and type(key_created_at) is not int): raise ContractError('time')
    claim=verifier.verify(capability)
    if not claim.mutating: return 'READ_ONLY'
    if not (claim.stable_idempotency_key and claim.request_bound_key): return 'NO_AUTOMATIC_RETRY'
    if claim.retention_seconds is None: return 'NO_AUTOMATIC_RETRY'
    if key_created_at is not None:
        age=now-key_created_at
        if age<0: raise ClockRollback('now precedes key creation')
        if age>=claim.retention_seconds: return 'NO_AUTOMATIC_RETRY'
    return 'SAFE_RETRY_RECONCILE' if claim.reconcile_by_key else 'SAFE_RETRY_IDEMPOTENT_ONLY'
@dataclass(frozen=True)
class PlannedRequest:
    sink_id:str; capability_generation:int; probe_generation:int; request_id:str; request_digest:str; effect_key:str; key_created_at:int; policy:Policy
class Planner:
    def __init__(self,verifier): self.verifier=verifier
    def plan(self,capability,request,*,request_id,now):
        claim=self.verifier.verify(capability); policy=derive_policy(capability,self.verifier,now=now,key_created_at=now)
        return PlannedRequest(claim.sink_id,claim.generation,capability.attestation.probe_generation,request_id,sha(request),f'{claim.sink_id}:{request_id}',now,policy)
    def revalidate(self,plan,capability,request,*,now):
        claim=self.verifier.verify(capability)
        if claim.sink_id!=plan.sink_id or claim.generation!=plan.capability_generation or capability.attestation.probe_generation!=plan.probe_generation: raise StaleCapability()
        if sha(request)!=plan.request_digest: raise RequestMismatch()
        current=derive_policy(capability,self.verifier,now=now,key_created_at=plan.key_created_at)
        order={'READ_ONLY':0,'NO_AUTOMATIC_RETRY':1,'SAFE_RETRY_IDEMPOTENT_ONLY':2,'SAFE_RETRY_RECONCILE':3}
        return plan.policy if order[current]>order[plan.policy] else current
class BrokerAdapter:
    def __init__(self,verifier): self.planner=Planner(verifier)
    def execute(self,plan,capability,request,sink,*,now,timeout_after_commit=False):
        policy=self.planner.revalidate(plan,capability,request,now=now)
        if policy=='READ_ONLY': raise ContractError('read-only')
        if policy=='NO_AUTOMATIC_RETRY': raise UnsafeRetryBlocked('no current automatic-retry authority')
        try: return sink.apply(plan.effect_key,request,timeout_after_commit=timeout_after_commit)
        except UnknownOutcome:
            if policy=='SAFE_RETRY_RECONCILE':
                r=sink.reconcile(plan.effect_key)
                if r is not None: return r
            raise UnsafeRetryBlocked('UNKNOWN requires external reconciliation')
class UnsafeGenericRetry:
    def execute(self,request,sink):
        try: sink.apply('first',request,timeout_after_commit=True)
        except UnknownOutcome: return sink.apply('retry-new-key',request)
