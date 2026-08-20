from __future__ import annotations
import hashlib,hmac,json,os,tempfile
from dataclasses import dataclass
from pathlib import Path

class RegistryError(RuntimeError): pass
class AuthError(RegistryError): pass
class RollbackError(RegistryError): pass
class MembershipError(RegistryError): pass
class TamperError(RegistryError): pass

def canonical(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()
def digest(x): return hashlib.sha256(canonical(x)).hexdigest()
def sign(key,x): return hmac.new(key,canonical(x),hashlib.sha256).hexdigest()

@dataclass(frozen=True)
class RegistrySnapshot:
    registry_id:str; version:int; generation:int; threshold:int; observers:dict; previous_digest:str|None; signature:str
    @property
    def unsigned(self): return {"registry_id":self.registry_id,"version":self.version,"generation":self.generation,"threshold":self.threshold,"observers":self.observers,"previous_digest":self.previous_digest}
    @property
    def snapshot_id(self): return digest({**self.unsigned,"signature":self.signature})
    @classmethod
    def issue(cls,**kw):
        key=kw.pop("root_key"); u=dict(kw); return cls(**u,signature=sign(key,u))

@dataclass(frozen=True)
class ObserverEvidence:
    observer_id:str; observer_generation:int; registry_snapshot_id:str; payload_digest:str; signature:str
    @property
    def unsigned(self): return {"observer_id":self.observer_id,"observer_generation":self.observer_generation,"registry_snapshot_id":self.registry_snapshot_id,"payload_digest":self.payload_digest}
    @classmethod
    def issue(cls,**kw):
        key=kw.pop("key"); u=dict(kw); return cls(**u,signature=sign(key,u))

class RegistryStore:
    def __init__(self,path): self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True)
    def save(self,obj):
        fd,tmp=tempfile.mkstemp(dir=str(self.path.parent))
        try:
            with os.fdopen(fd,"w") as f: json.dump(obj,f,sort_keys=True,separators=(",",":")); f.flush(); os.fsync(f.fileno())
            os.replace(tmp,self.path)
        finally:
            if os.path.exists(tmp): os.unlink(tmp)
    def load(self): return json.loads(self.path.read_text())

class ObserverRegistry:
    def __init__(self,root_key,store=None):
        self.root_key=root_key; self.store=store; self.history={}; self.current_id=None
        if store and store.path.exists():
            raw=store.load(); self.history=raw["history"]; self.current_id=raw["current_id"]; self._verify_all()
    def _decode(self,r): return RegistrySnapshot(r["registry_id"],r["version"],r["generation"],r["threshold"],r["observers"],r["previous_digest"],r["signature"])
    def _encode(self,s): return {**s.unsigned,"signature":s.signature,"snapshot_id":s.snapshot_id}
    def _verify_snapshot(self,s):
        if type(s.version) is not int or type(s.generation) is not int or type(s.threshold) is not int: raise AuthError("strict ints")
        if min(s.version,s.generation,s.threshold)<1: raise AuthError("bad metadata")
        if not hmac.compare_digest(sign(self.root_key,s.unsigned),s.signature): raise AuthError("bad registry signature")
        active=0
        for oid,o in s.observers.items():
            if o.get("observer_id")!=oid: raise MembershipError("identity mismatch")
            if o.get("status") not in ("ACTIVE","REVOKED"): raise MembershipError("bad status")
            if type(o.get("generation")) is not int or o["generation"]<1: raise MembershipError("bad observer generation")
            bytes.fromhex(o["key_hex"]); active += o["status"]=="ACTIVE"
        if s.threshold>active: raise MembershipError("threshold exceeds active")
    def _verify_all(self):
        ordered=sorted((self._decode(x) for x in self.history.values()),key=lambda s:s.version); prev=None
        for i,s in enumerate(ordered,1):
            self._verify_snapshot(s)
            if s.version!=i: raise RollbackError("gap")
            if self.history[s.snapshot_id]["snapshot_id"]!=s.snapshot_id: raise TamperError("id mismatch")
            if prev is None:
                if s.previous_digest is not None: raise TamperError("bootstrap predecessor")
            else:
                if s.registry_id!=prev.registry_id or s.previous_digest!=prev.snapshot_id: raise TamperError("chain")
                if s.generation<=prev.generation: raise RollbackError("generation")
            prev=s
        if prev and self.current_id!=prev.snapshot_id: raise TamperError("pointer")
    def accept(self,s):
        self._verify_snapshot(s)
        if self.current_id is None:
            if s.version!=1 or s.previous_digest is not None: raise RollbackError("bootstrap")
        else:
            cur=self.current()
            if s.version!=cur.version+1 or s.generation<=cur.generation: raise RollbackError("stale")
            if s.registry_id!=cur.registry_id or s.previous_digest!=cur.snapshot_id: raise TamperError("predecessor")
        self.history[s.snapshot_id]=self._encode(s); self.current_id=s.snapshot_id
        if self.store: self.store.save({"history":self.history,"current_id":self.current_id})
        return s.snapshot_id
    def current(self): return self._decode(self.history[self.current_id])
    def snapshot(self,sid): return self._decode(self.history[sid])
    def verify_evidence(self,e,historical=False):
        s=self.snapshot(e.registry_snapshot_id) if historical else self.current()
        if not historical and e.registry_snapshot_id!=s.snapshot_id: raise MembershipError("stale registry evidence")
        m=s.observers.get(e.observer_id)
        if not m or m["status"]!="ACTIVE" or e.observer_generation!=m["generation"]: raise MembershipError("inactive/stale observer")
        if not hmac.compare_digest(sign(bytes.fromhex(m["key_hex"]),e.unsigned),e.signature): raise AuthError("bad evidence")
        return True
    def quorum(self,evidence,payload_digest,snapshot_id=None,historical=False):
        s=self.snapshot(snapshot_id) if historical else self.current(); seen=set()
        for e in evidence:
            if e.payload_digest!=payload_digest or e.registry_snapshot_id!=s.snapshot_id: continue
            try: self.verify_evidence(e,historical=historical)
            except RegistryError: continue
            seen.add(e.observer_id)
        return len(seen)>=s.threshold

class UnsafeSelfAssertedMembership:
    def quorum(self,evidence,threshold): return len({e.observer_id for e in evidence})>=threshold
