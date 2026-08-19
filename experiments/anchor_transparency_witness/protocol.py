from __future__ import annotations
import hashlib, hmac, json, os, tempfile
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable

SCHEMA_VERSION = 1
class TransparencyError(RuntimeError): pass
class InvalidCheckpoint(TransparencyError): pass
class SplitViewDetected(TransparencyError): pass
class ConsistencyError(TransparencyError): pass
class StaleCheckpoint(TransparencyError): pass
class ReplayDetected(TransparencyError): pass
class WitnessThresholdError(TransparencyError): pass
class DuplicateWitness(TransparencyError): pass
class WrongLog(TransparencyError): pass

def _hash(data: bytes) -> bytes: return hashlib.sha256(data).digest()
def leaf_hash(data: bytes) -> bytes: return _hash(b'\x00' + data)
def node_hash(left: bytes, right: bytes) -> bytes: return _hash(b'\x01' + left + right)
def merkle_root(leaves: Iterable[bytes]) -> bytes:
    values=list(leaves)
    if not values: return _hash(b'')
    if len(values)==1: return leaf_hash(values[0])
    k=1 << ((len(values)-1).bit_length()-1)
    return node_hash(merkle_root(values[:k]), merkle_root(values[k:]))
def canonical(obj: dict) -> bytes: return json.dumps(obj,sort_keys=True,separators=(',',':')).encode()
def sign(key: bytes,obj: dict)->str: return hmac.new(key,canonical(obj),hashlib.sha256).hexdigest()

@dataclass(frozen=True)
class Checkpoint:
    schema_version:int; log_id:str; size:int; root_hash:str; sequence:int; signature:str
    def unsigned(self): return {'schema_version':self.schema_version,'log_id':self.log_id,'size':self.size,'root_hash':self.root_hash,'sequence':self.sequence}
    def identity(self): return hashlib.sha256(canonical(self.unsigned())).hexdigest()
@dataclass(frozen=True)
class ConsistencyProof:
    old_size:int; old_root:str; new_size:int; prior_leaves_hex:tuple[str,...]; appended_leaves_hex:tuple[str,...]
@dataclass(frozen=True)
class WitnessSignature:
    witness_id:str; checkpoint_id:str; signature:str

class ReferenceLog:
    def __init__(self,log_id,signing_key,leaves=()): self.log_id=log_id; self.signing_key=signing_key; self.leaves=list(leaves); self.sequence=len(self.leaves)
    def append(self,value:bytes): self.leaves.append(value); self.sequence+=1
    def checkpoint(self):
        u={'schema_version':SCHEMA_VERSION,'log_id':self.log_id,'size':len(self.leaves),'root_hash':merkle_root(self.leaves).hex(),'sequence':self.sequence}
        return Checkpoint(**u,signature=sign(self.signing_key,u))
    def consistency_from(self,old):
        if old.log_id!=self.log_id or old.size>len(self.leaves): raise ConsistencyError('incompatible prior checkpoint')
        return ConsistencyProof(old.size,old.root_hash,len(self.leaves),tuple(x.hex() for x in self.leaves[:old.size]),tuple(x.hex() for x in self.leaves[old.size:]))

class WitnessStore:
    def __init__(self,path): self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True)
    def save(self,checkpoint,accepted_at):
        fd,tmp=tempfile.mkstemp(prefix=self.path.name+'.',dir=str(self.path.parent))
        try:
            with os.fdopen(fd,'w',encoding='utf-8') as fh:
                json.dump({'checkpoint':asdict(checkpoint),'accepted_at':accepted_at},fh,sort_keys=True); fh.flush(); os.fsync(fh.fileno())
            os.replace(tmp,self.path)
        finally:
            if os.path.exists(tmp): os.unlink(tmp)
    def load_state(self):
        if not self.path.exists(): return None
        raw=json.loads(self.path.read_text(encoding='utf-8'))
        return Checkpoint(**raw['checkpoint']), int(raw['accepted_at'])
    def load(self):
        state=self.load_state(); return None if state is None else state[0]

class Witness:
    def __init__(self,witness_id,key,log_id,log_key,store): self.witness_id=witness_id; self.key=key; self.log_id=log_id; self.log_key=log_key; self.store=store
    def verify_checkpoint(self,cp):
        if cp.schema_version!=SCHEMA_VERSION: raise InvalidCheckpoint('schema')
        if cp.log_id!=self.log_id: raise WrongLog(cp.log_id)
        if not hmac.compare_digest(sign(self.log_key,cp.unsigned()),cp.signature): raise InvalidCheckpoint('signature')
    def observe(self,cp,proof=None,accepted_at=0):
        self.verify_checkpoint(cp); prev=self.store.load()
        if prev is None:
            self.store.save(cp,accepted_at); return self._cosign(cp)
        self.verify_checkpoint(prev)
        if cp.size<prev.size or cp.sequence<prev.sequence: raise ReplayDetected('older than watermark')
        if cp.size==prev.size:
            if cp.root_hash!=prev.root_hash: raise SplitViewDetected('same size, different root')
            if cp.sequence==prev.sequence: raise StaleCheckpoint('no advancement')
            raise ConsistencyError('same tree size with advancing sequence')
        if proof is None: raise ConsistencyError('extension requires proof')
        if proof.old_size!=prev.size or proof.old_root!=prev.root_hash or proof.new_size!=cp.size: raise ConsistencyError('proof binding mismatch')
        prior=[bytes.fromhex(x) for x in proof.prior_leaves_hex]
        if len(prior)!=prev.size or merkle_root(prior).hex()!=prev.root_hash: raise ConsistencyError('prior material mismatch')
        appended=[bytes.fromhex(x) for x in proof.appended_leaves_hex]
        if len(prior)+len(appended)!=cp.size: raise ConsistencyError('proof size mismatch')
        if merkle_root(prior+appended).hex()!=cp.root_hash: raise SplitViewDetected('extension root inconsistent with witnessed history')
        self.store.save(cp,accepted_at); return self._cosign(cp)
    def freshness(self,now,max_age):
        state=self.store.load_state()
        if state is None: raise StaleCheckpoint('no witnessed checkpoint')
        _,accepted_at=state
        if now < accepted_at: raise InvalidCheckpoint('trusted clock moved backwards')
        return 'CURRENT' if now-accepted_at <= max_age else 'STALE'
    def _cosign(self,cp):
        obj={'witness_id':self.witness_id,'checkpoint_id':cp.identity()}
        return WitnessSignature(self.witness_id,cp.identity(),sign(self.key,obj))

class WitnessPolicy:
    def __init__(self,keys,threshold): self.keys=keys; self.threshold=threshold
    def verify(self,cp,signatures):
        seen=set(); valid=[]
        for s in signatures:
            if s.witness_id in seen: continue
            seen.add(s.witness_id); key=self.keys.get(s.witness_id)
            if key is None or s.checkpoint_id!=cp.identity(): continue
            obj={'witness_id':s.witness_id,'checkpoint_id':s.checkpoint_id}
            if hmac.compare_digest(sign(key,obj),s.signature): valid.append(s.witness_id)
        if len(valid)<self.threshold: raise WitnessThresholdError(f'valid={len(valid)} threshold={self.threshold}')
        return tuple(sorted(valid))

class CheckpointObserver:
    """Compares independently obtained checkpoint views; detects equivocation once views meet."""
    def __init__(self): self.by_log_size={}
    def observe(self,cp):
        key=(cp.log_id,cp.size)
        prior=self.by_log_size.get(key)
        if prior is not None and prior.root_hash!=cp.root_hash:
            raise SplitViewDetected('observer saw conflicting roots for same log/size')
        self.by_log_size[key]=cp
        return cp

class UnsafeSelfPresentedClient:
    def __init__(self,log_key): self.log_key=log_key
    def accept(self,cp): return hmac.compare_digest(sign(self.log_key,cp.unsigned()),cp.signature)
