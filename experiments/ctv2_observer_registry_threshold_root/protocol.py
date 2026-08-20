from __future__ import annotations
import hashlib,hmac,json,os,tempfile
from dataclasses import asdict,dataclass
from pathlib import Path

class RegistryTrustError(RuntimeError): pass
class IntegrityError(RegistryTrustError): pass
class ThresholdError(RegistryTrustError): pass
class RollbackError(RegistryTrustError): pass
class SubstitutionError(RegistryTrustError): pass
class EpochError(RegistryTrustError): pass
class MembershipError(RegistryTrustError): pass
class EvidenceError(RegistryTrustError): pass

def canonical(obj): return json.dumps(obj,sort_keys=True,separators=(",",":")).encode()
def digest(obj): return hashlib.sha256(canonical(obj)).hexdigest()
def sign(key,obj): return hmac.new(key,canonical(obj),hashlib.sha256).hexdigest()
def key_id(key): return hashlib.sha256(key).hexdigest()[:16]

@dataclass(frozen=True)
class Signature:
    signer_id:str
    signature:str

@dataclass(frozen=True)
class RootState:
    registry_id:str
    version:int
    authority_epoch:int
    threshold:int
    keys:dict[str,str]
    revoked:tuple[str,...]=()
    @property
    def descriptor(self):
        return {"registry_id":self.registry_id,"version":self.version,"authority_epoch":self.authority_epoch,
                "threshold":self.threshold,"keys":dict(sorted(self.keys.items())),"revoked":sorted(self.revoked)}
    @property
    def root_id(self): return digest(self.descriptor)
    def validate(self):
        if type(self.version) is not int or type(self.authority_epoch) is not int or type(self.threshold) is not int:
            raise IntegrityError("strict root ints")
        if min(self.version,self.authority_epoch,self.threshold)<1: raise IntegrityError("bad root metadata")
        if len(set(self.revoked))!=len(self.revoked): raise IntegrityError("duplicate revoked")
        active=set(self.keys)-set(self.revoked)
        if self.threshold>len(active): raise IntegrityError("threshold exceeds active")
        for sid,hx in self.keys.items():
            try: key=bytes.fromhex(hx)
            except ValueError as e: raise IntegrityError("bad key hex") from e
            if sid!=key_id(key): raise IntegrityError("key identity mismatch")
        return True

@dataclass(frozen=True)
class RecoveryAuthority:
    generation:int
    threshold:int
    keys:dict[str,str]
    revoked:tuple[str,...]=()
    @property
    def descriptor(self):
        return {"generation":self.generation,"threshold":self.threshold,
                "keys":dict(sorted(self.keys.items())),"revoked":sorted(self.revoked)}
    @property
    def authority_id(self): return digest(self.descriptor)
    def validate(self):
        if type(self.generation) is not int or type(self.threshold) is not int or min(self.generation,self.threshold)<1:
            raise IntegrityError("bad recovery metadata")
        active=set(self.keys)-set(self.revoked)
        if self.threshold>len(active): raise IntegrityError("recovery threshold exceeds active")
        for sid,hx in self.keys.items():
            key=bytes.fromhex(hx)
            if sid!=key_id(key): raise IntegrityError("recovery key identity mismatch")
        return True

def verify_threshold(keys,threshold,revoked,payload,signatures):
    seen=set(); valid=[]; revoked=set(revoked)
    for item in signatures:
        if item.signer_id in seen: continue
        seen.add(item.signer_id)
        if item.signer_id in revoked: continue
        hx=keys.get(item.signer_id)
        if hx is None: continue
        if hmac.compare_digest(sign(bytes.fromhex(hx),payload),item.signature): valid.append(item.signer_id)
    if len(valid)<threshold: raise ThresholdError(f"valid={len(valid)} threshold={threshold}")
    return tuple(sorted(valid))

def rotation_payload(old,new):
    return {"kind":"observer_registry_root_rotation","registry_id":old.registry_id,"old_root_id":old.root_id,"new_root":new.descriptor}

def recovery_payload(old,new,recovery):
    return {"kind":"observer_registry_break_glass","registry_id":old.registry_id,"old_root_id":old.root_id,
            "recovery_authority_id":recovery.authority_id,"new_root":new.descriptor}

@dataclass(frozen=True)
class RegistrySnapshot:
    registry_id:str; version:int; generation:int; threshold:int; observers:dict; previous_digest:str|None
    root_version:int; authority_epoch:int; root_id:str; signatures:tuple[Signature,...]
    @property
    def unsigned(self):
        return {"registry_id":self.registry_id,"version":self.version,"generation":self.generation,"threshold":self.threshold,
                "observers":self.observers,"previous_digest":self.previous_digest,"root_version":self.root_version,
                "authority_epoch":self.authority_epoch,"root_id":self.root_id}
    @property
    def snapshot_id(self): return digest({**self.unsigned,"signatures":[asdict(x) for x in self.signatures]})

@dataclass(frozen=True)
class ObserverEvidence:
    observer_id:str; observer_generation:int; registry_snapshot_id:str; root_id:str; payload_digest:str; signature:str
    @property
    def unsigned(self):
        return {"observer_id":self.observer_id,"observer_generation":self.observer_generation,
                "registry_snapshot_id":self.registry_snapshot_id,"root_id":self.root_id,"payload_digest":self.payload_digest}
    @classmethod
    def issue(cls,*,key,**kw):
        u=dict(kw); return cls(**u,signature=sign(key,u))

class JsonStore:
    def __init__(self,path): self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True)
    def save(self,obj):
        fd,tmp=tempfile.mkstemp(prefix=self.path.name+".",dir=str(self.path.parent))
        try:
            with os.fdopen(fd,"w",encoding="utf-8") as f:
                json.dump(obj,f,sort_keys=True,separators=(",",":")); f.flush(); os.fsync(f.fileno())
            os.replace(tmp,self.path)
        finally:
            if os.path.exists(tmp): os.unlink(tmp)
    def load(self): return json.loads(self.path.read_text(encoding="utf-8"))

class RegistryAuthority:
    def __init__(self,bootstrap_root,recovery,store=None):
        bootstrap_root.validate(); recovery.validate(); self.recovery=recovery; self.store=store
        self.bootstrap_root_id=bootstrap_root.root_id
        self.roots={bootstrap_root.root_id:bootstrap_root}; self.current_root_id=bootstrap_root.root_id
        self.root_transitions=[]
        self.registry_history={}; self.current_snapshot_id=None
        if store and store.path.exists(): self._load(store.load())
        elif store: self._persist()
    def _encode_root(self,r): return r.descriptor
    def _decode_root(self,x): return RootState(x["registry_id"],x["version"],x["authority_epoch"],x["threshold"],dict(x["keys"]),tuple(x.get("revoked",[])))
    def _encode_snapshot(self,s): return {**s.unsigned,"signatures":[asdict(x) for x in s.signatures],"snapshot_id":s.snapshot_id}
    def _decode_snapshot(self,x):
        return RegistrySnapshot(x["registry_id"],x["version"],x["generation"],x["threshold"],dict(x["observers"]),x["previous_digest"],
                                x["root_version"],x["authority_epoch"],x["root_id"],tuple(Signature(**y) for y in x["signatures"]))
    def _persist(self):
        if self.store:
            self.store.save({"roots":{rid:self._encode_root(r) for rid,r in self.roots.items()},"current_root_id":self.current_root_id,
                             "bootstrap_root_id":self.bootstrap_root_id,"root_transitions":self.root_transitions,
                             "registry_history":self.registry_history,"current_snapshot_id":self.current_snapshot_id,
                             "recovery_authority_id":self.recovery.authority_id})
    def _load(self,raw):
        if raw.get("recovery_authority_id")!=self.recovery.authority_id: raise IntegrityError("recovery authority substitution")
        if raw.get("bootstrap_root_id")!=self.bootstrap_root_id: raise IntegrityError("bootstrap root substitution")
        self.roots={rid:self._decode_root(x) for rid,x in raw["roots"].items()}; self.current_root_id=raw["current_root_id"]
        self.root_transitions=list(raw.get("root_transitions",[]))
        self.registry_history=dict(raw["registry_history"]); self.current_snapshot_id=raw["current_snapshot_id"]; self._verify_all()
    def current_root(self): return self.roots[self.current_root_id]
    def current_snapshot(self): return self._decode_snapshot(self.registry_history[self.current_snapshot_id])
    def snapshot(self,sid): return self._decode_snapshot(self.registry_history[sid])
    def _verify_root_history(self):
        roots=sorted(self.roots.values(),key=lambda x:x.version)
        if not roots: raise IntegrityError("missing roots")
        seen=set(); rid=roots[0].registry_id
        for r in roots:
            r.validate()
            if r.registry_id!=rid: raise SubstitutionError("root registry mismatch")
            if r.version in seen: raise SubstitutionError("same-version root substitution")
            seen.add(r.version)
            if self.roots.get(r.root_id)!=r: raise IntegrityError("root id mismatch")
        if roots[0].root_id!=self.bootstrap_root_id: raise IntegrityError("bootstrap root missing")
        if self.current_root().version!=max(seen): raise RollbackError("root pointer rollback")
        transitions={x.get("new_root_id"):x for x in self.root_transitions}
        if len(transitions)!=len(self.root_transitions): raise IntegrityError("duplicate root transition")
        for a,b in zip(roots,roots[1:]):
            if b.version!=a.version+1: raise RollbackError("root version gap")
            t=transitions.get(b.root_id)
            if not t or t.get("old_root_id")!=a.root_id: raise IntegrityError("missing root transition proof")
            signatures=tuple(Signature(**x) for x in t.get("signatures",[]))
            if b.authority_epoch==a.authority_epoch:
                if t.get("kind")!="rotation": raise IntegrityError("wrong transition kind")
                p=rotation_payload(a,b)
                old_count=t.get("old_signature_count")
                if type(old_count) is not int or old_count<0 or old_count>len(signatures): raise IntegrityError("bad signature partition")
                verify_threshold(a.keys,a.threshold,a.revoked,p,signatures[:old_count])
                verify_threshold(b.keys,b.threshold,b.revoked,p,signatures[old_count:])
            elif b.authority_epoch==a.authority_epoch+1:
                if t.get("kind")!="recovery" or t.get("recovery_authority_id")!=self.recovery.authority_id: raise IntegrityError("wrong recovery transition")
                verify_threshold(self.recovery.keys,self.recovery.threshold,self.recovery.revoked,recovery_payload(a,b,self.recovery),signatures)
            else: raise EpochError("bad root epoch transition")
        if set(transitions)!={r.root_id for r in roots[1:]}: raise IntegrityError("orphan root transition")
    def _validate_membership(self,s):
        if type(s.version) is not int or type(s.generation) is not int or type(s.threshold) is not int: raise IntegrityError("strict registry ints")
        if min(s.version,s.generation,s.threshold)<1: raise IntegrityError("bad registry metadata")
        active=0
        for oid,m in s.observers.items():
            if m.get("observer_id")!=oid: raise MembershipError("identity mismatch")
            if m.get("status") not in ("ACTIVE","REVOKED"): raise MembershipError("bad status")
            if type(m.get("generation")) is not int or m["generation"]<1: raise MembershipError("bad observer generation")
            try: bytes.fromhex(m["key_hex"])
            except ValueError as e: raise MembershipError("bad observer key") from e
            active += m["status"]=="ACTIVE"
        if s.threshold>active: raise MembershipError("threshold exceeds active")
    def _verify_snapshot(self,s):
        self._validate_membership(s); root=self.roots.get(s.root_id)
        if root is None: raise IntegrityError("unknown root")
        if (s.registry_id,s.root_version,s.authority_epoch)!=(root.registry_id,root.version,root.authority_epoch): raise SubstitutionError("snapshot/root binding")
        verify_threshold(root.keys,root.threshold,root.revoked,s.unsigned,s.signatures); return root
    def _verify_registry_history(self):
        snaps=sorted((self._decode_snapshot(x) for x in self.registry_history.values()),key=lambda x:x.version); prev=None
        for i,s in enumerate(snaps,1):
            self._verify_snapshot(s)
            if s.version!=i: raise RollbackError("registry version gap")
            if self.registry_history[s.snapshot_id]["snapshot_id"]!=s.snapshot_id: raise IntegrityError("snapshot id mismatch")
            if prev is None:
                if s.previous_digest is not None: raise IntegrityError("bootstrap predecessor")
            else:
                if s.registry_id!=prev.registry_id or s.previous_digest!=prev.snapshot_id: raise SubstitutionError("registry chain")
                if s.generation<=prev.generation: raise RollbackError("registry generation")
            prev=s
        if prev and self.current_snapshot_id!=prev.snapshot_id: raise RollbackError("registry pointer rollback")
    def _verify_all(self): self._verify_root_history(); self._verify_registry_history()
    def rotate_root(self,new,old_signatures,new_signatures):
        old=self.current_root(); new.validate()
        if new.registry_id!=old.registry_id: raise SubstitutionError("wrong registry")
        if new.version!=old.version+1: raise RollbackError("root version")
        if new.authority_epoch!=old.authority_epoch: raise EpochError("normal rotation cannot change epoch")
        p=rotation_payload(old,new); old_signatures=tuple(old_signatures); new_signatures=tuple(new_signatures)
        verify_threshold(old.keys,old.threshold,old.revoked,p,old_signatures); verify_threshold(new.keys,new.threshold,new.revoked,p,new_signatures)
        self.roots[new.root_id]=new; self.current_root_id=new.root_id
        self.root_transitions.append({"kind":"rotation","old_root_id":old.root_id,"new_root_id":new.root_id,"old_signature_count":len(old_signatures),"signatures":[asdict(x) for x in old_signatures+new_signatures]})
        self._persist(); return new.root_id
    def recover_root(self,new,recovery_signatures):
        old=self.current_root(); new.validate()
        if new.registry_id!=old.registry_id: raise SubstitutionError("wrong registry")
        if new.version!=old.version+1: raise RollbackError("root version")
        if new.authority_epoch!=old.authority_epoch+1: raise EpochError("recovery must advance epoch")
        p=recovery_payload(old,new,self.recovery); recovery_signatures=tuple(recovery_signatures)
        verify_threshold(self.recovery.keys,self.recovery.threshold,self.recovery.revoked,p,recovery_signatures)
        self.roots[new.root_id]=new; self.current_root_id=new.root_id
        self.root_transitions.append({"kind":"recovery","old_root_id":old.root_id,"new_root_id":new.root_id,"recovery_authority_id":self.recovery.authority_id,"signatures":[asdict(x) for x in recovery_signatures]})
        self._persist(); return new.root_id
    def accept_snapshot(self,s):
        root=self._verify_snapshot(s)
        if root.root_id!=self.current_root_id: raise ThresholdError("stale root signer")
        if self.current_snapshot_id is None:
            if s.version!=1 or s.previous_digest is not None: raise RollbackError("registry bootstrap")
        else:
            cur=self.current_snapshot()
            if s.version!=cur.version+1 or s.generation<=cur.generation: raise RollbackError("stale registry snapshot")
            if s.registry_id!=cur.registry_id or s.previous_digest!=cur.snapshot_id: raise SubstitutionError("registry predecessor")
        self.registry_history[s.snapshot_id]=self._encode_snapshot(s); self.current_snapshot_id=s.snapshot_id; self._persist(); return s.snapshot_id
    def verify_evidence(self,e,historical=False):
        s=self.snapshot(e.registry_snapshot_id) if historical else self.current_snapshot()
        if e.registry_snapshot_id!=s.snapshot_id or e.root_id!=s.root_id: raise EvidenceError("evidence authority binding")
        if not historical and s.snapshot_id!=self.current_snapshot_id: raise EvidenceError("stale registry evidence")
        self._verify_snapshot(s); m=s.observers.get(e.observer_id)
        if not m or m["status"]!="ACTIVE" or e.observer_generation!=m["generation"]: raise MembershipError("inactive/stale observer")
        if not hmac.compare_digest(sign(bytes.fromhex(m["key_hex"]),e.unsigned),e.signature): raise EvidenceError("bad observer evidence")
        return True
    def quorum(self,evidence,payload_digest,*,snapshot_id=None,historical=False):
        s=self.snapshot(snapshot_id) if historical else self.current_snapshot(); seen=set()
        for e in evidence:
            if e.payload_digest!=payload_digest or e.registry_snapshot_id!=s.snapshot_id or e.root_id!=s.root_id: continue
            try: self.verify_evidence(e,historical=historical)
            except RegistryTrustError: continue
            seen.add(e.observer_id)
        return len(seen)>=s.threshold

class UnsafeSingleSignerRootSwap:
    def accept_snapshot(self,s,asserted_key): return hmac.compare_digest(sign(asserted_key,s.unsigned),s.signatures[0].signature)
