from __future__ import annotations
from dataclasses import dataclass
from typing import Literal
import hashlib, json
Policy=Literal['SAFE_RETRY_RECONCILE','SAFE_RETRY_IDEMPOTENT_ONLY','NO_AUTOMATIC_RETRY','READ_ONLY']
class ContractError(RuntimeError): pass
class StaleCapability(ContractError): pass
class RequestMismatch(ContractError): pass
class UnknownOutcome(ContractError): pass
class UnsafeRetryBlocked(ContractError): pass
def canon(o): return json.dumps(o,sort_keys=True,separators=(',',':')).encode()
def sha(o): return hashlib.sha256(canon(o)).hexdigest()
@dataclass(frozen=True)
class SinkCapability:
    sink_id:str; generation:int; mutating:bool; stable_idempotency_key:bool; request_bound_key:bool; reconcile_by_key:bool; retention_seconds:int|None; source:str; observed:bool=False; behavioral_probe_passed:bool=False
    def validate(self):
        if not self.sink_id or type(self.generation) is not int or self.generation<1: raise ContractError('identity')
        if self.retention_seconds is not None and (type(self.retention_seconds) is not int or self.retention_seconds<1): raise ContractError('retention')
        if not self.source: raise ContractError('source')
def derive_policy(cap:SinkCapability,*,now:int,key_created_at:int|None=None)->Policy:
    cap.validate()
    if not cap.mutating: return 'READ_ONLY'
    if not (cap.observed and cap.behavioral_probe_passed): return 'NO_AUTOMATIC_RETRY'
    if not (cap.stable_idempotency_key and cap.request_bound_key): return 'NO_AUTOMATIC_RETRY'
    if cap.retention_seconds is not None and key_created_at is not None and now-key_created_at>=cap.retention_seconds: return 'NO_AUTOMATIC_RETRY'
    return 'SAFE_RETRY_RECONCILE' if cap.reconcile_by_key else 'SAFE_RETRY_IDEMPOTENT_ONLY'
@dataclass(frozen=True)
class PlannedRequest:
    sink_id:str; capability_generation:int; request_id:str; request_digest:str; effect_key:str; key_created_at:int; policy:Policy
class Planner:
    def plan(self,cap,request,*,request_id,now):
        return PlannedRequest(cap.sink_id,cap.generation,request_id,sha(request),f'{cap.sink_id}:{request_id}',now,derive_policy(cap,now=now,key_created_at=now))
    def revalidate(self,plan,cap,request,*,now):
        if cap.sink_id!=plan.sink_id or cap.generation!=plan.capability_generation: raise StaleCapability()
        if sha(request)!=plan.request_digest: raise RequestMismatch()
        current=derive_policy(cap,now=now,key_created_at=plan.key_created_at)
        order={'READ_ONLY':0,'NO_AUTOMATIC_RETRY':1,'SAFE_RETRY_IDEMPOTENT_ONLY':2,'SAFE_RETRY_RECONCILE':3}
        return plan.policy if order[current]>order[plan.policy] else current
class SimulatedSink:
    def __init__(self,*,idempotent,request_bound,reconcile): self.idempotent=idempotent; self.request_bound=request_bound; self.reconcile_supported=reconcile; self.effects=[]; self.by_key={}
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
class BrokerAdapter:
    def execute(self,plan,cap,request,sink,*,now,timeout_after_commit=False):
        policy=Planner().revalidate(plan,cap,request,now=now)
        if policy=='READ_ONLY': raise ContractError('read-only')
        try: return sink.apply(plan.effect_key,request,timeout_after_commit=timeout_after_commit)
        except UnknownOutcome:
            if policy=='SAFE_RETRY_RECONCILE':
                r=sink.reconcile(plan.effect_key)
                if r is not None: return r
            raise UnsafeRetryBlocked()
class UnsafeGenericRetry:
    def execute(self,request,sink):
        try: sink.apply('first',request,timeout_after_commit=True)
        except UnknownOutcome: return sink.apply('retry-new-key',request)
