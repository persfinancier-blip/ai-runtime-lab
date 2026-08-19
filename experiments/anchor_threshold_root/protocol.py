from __future__ import annotations
import hashlib,hmac,json,os,tempfile
from dataclasses import asdict,dataclass
from pathlib import Path
from typing import Iterable
class TrustError(RuntimeError): pass
class ThresholdError(TrustError): pass
class DuplicateSigner(TrustError): pass
class RevokedSigner(TrustError): pass
class WrongProvider(TrustError): pass
class StaleVersion(TrustError): pass
class EpochMismatch(TrustError): pass
class RecoveryError(TrustError): pass
class IntegrityError(TrustError): pass
def key_id(key:bytes)->str: return hashlib.sha256(key).hexdigest()[:16]
def canonical(obj:dict)->bytes: return json.dumps(obj,sort_keys=True,separators=(",",":")).encode()
def sign(key:bytes,obj:dict)->str: return hmac.new(key,canonical(obj),hashlib.sha256).hexdigest()
@dataclass(frozen=True)
class Signature:
    signer_id:str; signature:str
@dataclass(frozen=True)
class RootState:
    provider_id:str; version:int; authority_epoch:int; threshold:int; keys:dict[str,str]; revoked:tuple[str,...]=()
    def validate(self):
        if type(self.version) is not int or self.version<1: raise IntegrityError('invalid root version')
        if type(self.authority_epoch) is not int or self.authority_epoch<1: raise IntegrityError('invalid authority epoch')
        if type(self.threshold) is not int or self.threshold<1 or self.threshold>len(self.keys): raise IntegrityError('invalid threshold')
        for sid,hx in self.keys.items():
            key=bytes.fromhex(hx)
            if sid!=key_id(key): raise IntegrityError('signer id/key mismatch')
        if len(set(self.revoked))!=len(self.revoked): raise IntegrityError('duplicate revoked identity')
@dataclass(frozen=True)
class RecoveryAuthority:
    generation:int; threshold:int; keys:dict[str,str]; revoked:tuple[str,...]=()
    def validate(self):
        if type(self.generation) is not int or self.generation<1: raise IntegrityError('invalid recovery generation')
        if type(self.threshold) is not int or self.threshold<1 or self.threshold>len(self.keys): raise IntegrityError('invalid recovery threshold')
        for sid,hx in self.keys.items():
            key=bytes.fromhex(hx)
            if sid!=key_id(key): raise IntegrityError('recovery signer id/key mismatch')
def root_descriptor(s:RootState)->dict:
    return {'provider_id':s.provider_id,'version':s.version,'authority_epoch':s.authority_epoch,'threshold':s.threshold,'keys':dict(sorted(s.keys.items())),'revoked':sorted(s.revoked)}
def rotation_payload(old:RootState,new:RootState)->dict:
    return {'kind':'root_rotation','provider_id':old.provider_id,'old_version':old.version,'new_root':root_descriptor(new)}
def recovery_payload(old:RootState,new:RootState,recovery_generation:int)->dict:
    return {'kind':'break_glass_recovery','provider_id':old.provider_id,'old_version':old.version,'old_authority_epoch':old.authority_epoch,'recovery_generation':recovery_generation,'new_root':root_descriptor(new)}
def verify_threshold(keys:dict[str,str],threshold:int,revoked:Iterable[str],payload:dict,signatures:Iterable[Signature])->tuple[str,...]:
    revoked=set(revoked); seen=set(); valid=[]
    for item in signatures:
        if item.signer_id in seen: raise DuplicateSigner(item.signer_id)
        seen.add(item.signer_id)
        if item.signer_id in revoked: raise RevokedSigner(item.signer_id)
        hx=keys.get(item.signer_id)
        if hx is None: continue
        if hmac.compare_digest(sign(bytes.fromhex(hx),payload),item.signature): valid.append(item.signer_id)
    if len(valid)<threshold: raise ThresholdError(f'valid={len(valid)} threshold={threshold}')
    return tuple(sorted(valid))
class AtomicRootStore:
    def __init__(self,path): self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True)
    def save(self,state:RootState):
        state.validate(); fd,tmp=tempfile.mkstemp(prefix=self.path.name+'.',dir=str(self.path.parent))
        try:
            with os.fdopen(fd,'w',encoding='utf-8') as fh:
                json.dump(asdict(state),fh,sort_keys=True); fh.flush(); os.fsync(fh.fileno())
            os.replace(tmp,self.path)
        finally:
            if os.path.exists(tmp): os.unlink(tmp)
    def load(self)->RootState:
        raw=json.loads(self.path.read_text(encoding='utf-8'))
        s=RootState(raw['provider_id'],raw['version'],raw['authority_epoch'],raw['threshold'],dict(raw['keys']),tuple(raw.get('revoked',[]))); s.validate(); return s
class ThresholdTrustStore:
    def __init__(self,root:RootState,recovery:RecoveryAuthority,store:AtomicRootStore|None=None):
        root.validate(); recovery.validate(); self.root=root; self.recovery=recovery; self.store=store
        if store and not store.path.exists(): store.save(root)
    def _activate(self,state):
        state.validate()
        if self.store: self.store.save(state)
        self.root=state
    def rotate(self,new,old_signatures,new_signatures):
        old=self.root; new.validate()
        if new.provider_id!=old.provider_id: raise WrongProvider()
        if new.authority_epoch!=old.authority_epoch: raise EpochMismatch()
        if new.version!=old.version+1: raise StaleVersion()
        p=rotation_payload(old,new)
        old_valid=verify_threshold(old.keys,old.threshold,old.revoked,p,old_signatures)
        new_valid=verify_threshold(new.keys,new.threshold,new.revoked,p,new_signatures)
        self._activate(new)
        return {'kind':'rotation','provider_id':new.provider_id,'version':new.version,'authority_epoch':new.authority_epoch,'old_signers':old_valid,'new_signers':new_valid}
    def recover(self,new,recovery_signatures):
        old=self.root; new.validate()
        if new.provider_id!=old.provider_id: raise WrongProvider()
        if new.authority_epoch!=old.authority_epoch+1: raise EpochMismatch()
        if new.version!=old.version+1: raise StaleVersion()
        p=recovery_payload(old,new,self.recovery.generation)
        valid=verify_threshold(self.recovery.keys,self.recovery.threshold,self.recovery.revoked,p,recovery_signatures)
        self._activate(new)
        return {'kind':'recovery','provider_id':new.provider_id,'version':new.version,'authority_epoch':new.authority_epoch,'recovery_generation':self.recovery.generation,'recovery_signers':valid}
    def receipt_is_current(self,receipt_epoch,receipt_version): return receipt_epoch==self.root.authority_epoch and receipt_version==self.root.version
class UnsafeSingleSignerRecovery:
    def recover(self,new,asserted_key,signature):
        p={'new_root':root_descriptor(new)}; return hmac.compare_digest(sign(asserted_key,p),signature)
