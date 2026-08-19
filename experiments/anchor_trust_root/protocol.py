from __future__ import annotations
import hashlib,hmac,json
from dataclasses import dataclass
class TrustError(RuntimeError): pass
class UnknownKey(TrustError): pass
class StaleGeneration(TrustError): pass
class Rollback(TrustError): pass
class RevokedKey(TrustError): pass
class WrongProvider(TrustError): pass
class RecoveryEpochMismatch(TrustError): pass
class RotationAuthError(TrustError): pass
def kid(key:bytes)->str: return hashlib.sha256(key).hexdigest()[:16]
def mac(key:bytes,obj:dict)->str:
    raw=json.dumps(obj,sort_keys=True,separators=(",",":")).encode(); return hmac.new(key,raw,hashlib.sha256).hexdigest()
@dataclass(frozen=True)
class TrustState:
    store_version:int; authority_epoch:int; provider_id:str; generation:int; key_id:str; key:bytes; revoked:frozenset[str]=frozenset()
@dataclass(frozen=True)
class Rotation:
    provider_id:str; old_generation:int; new_generation:int; new_key_id:str; new_key:bytes; authority_epoch:int; signature:str
def rotation_payload(provider_id,old_generation,new_generation,new_key_id,authority_epoch):
    return {"provider_id":provider_id,"old_generation":old_generation,"new_generation":new_generation,"new_key_id":new_key_id,"authority_epoch":authority_epoch}
class TrustStore:
    def __init__(self,state:TrustState): self.state=state
    def apply_rotation(self,r:Rotation):
        s=self.state
        if r.provider_id!=s.provider_id: raise WrongProvider()
        if r.old_generation!=s.generation or r.new_generation!=s.generation+1: raise StaleGeneration()
        if r.authority_epoch!=s.authority_epoch: raise RecoveryEpochMismatch()
        if r.new_key_id!=kid(r.new_key): raise RotationAuthError("key id mismatch")
        p=rotation_payload(r.provider_id,r.old_generation,r.new_generation,r.new_key_id,r.authority_epoch)
        if not hmac.compare_digest(mac(s.key,p),r.signature): raise RotationAuthError()
        self.state=TrustState(s.store_version+1,s.authority_epoch,s.provider_id,r.new_generation,r.new_key_id,r.new_key,s.revoked|{s.key_id})
    def recover(self,new_key:bytes):
        s=self.state; self.state=TrustState(s.store_version+1,s.authority_epoch+1,s.provider_id,s.generation+1,kid(new_key),new_key,s.revoked|{s.key_id})
    def load_snapshot(self,candidate:TrustState):
        if candidate.store_version<self.state.store_version or candidate.authority_epoch<self.state.authority_epoch: raise Rollback()
        self.state=candidate
    def verify(self,provider_id,generation,key_id,payload,signature,receipt_epoch):
        s=self.state
        if provider_id!=s.provider_id: raise WrongProvider()
        if receipt_epoch!=s.authority_epoch: raise RecoveryEpochMismatch()
        if generation!=s.generation: raise StaleGeneration()
        if key_id in s.revoked: raise RevokedKey()
        if key_id!=s.key_id: raise UnknownKey()
        if not hmac.compare_digest(mac(s.key,payload),signature): raise TrustError("bad signature")
        return True
class UnsafeSelfAsserted:
    def verify(self,payload,signature,asserted_key): return hmac.compare_digest(mac(asserted_key,payload),signature)
