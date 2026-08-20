from __future__ import annotations
import hashlib,hmac,json,os,tempfile
from dataclasses import asdict,dataclass
from pathlib import Path

class AuthorityError(RuntimeError): pass
class IntegrityError(AuthorityError): pass
class ThresholdError(AuthorityError): pass
class RollbackError(AuthorityError): pass
class RecoveryBoundaryError(AuthorityError): pass

def canonical(o): return json.dumps(o,sort_keys=True,separators=(',',':')).encode()
def digest(o): return hashlib.sha256(canonical(o)).hexdigest()
def sign(k,o): return hmac.new(k,canonical(o),hashlib.sha256).hexdigest()
def kid(k): return hashlib.sha256(k).hexdigest()[:16]

@dataclass(frozen=True)
class Sig: signer_id:str; signature:str

@dataclass(frozen=True)
class Authority:
    kind:str; registry_id:str; version:int; generation:int; threshold:int; keys:dict[str,str]; revoked:tuple[str,...]=()
    @property
    def descriptor(self): return {'kind':self.kind,'registry_id':self.registry_id,'version':self.version,'generation':self.generation,'threshold':self.threshold,'keys':dict(sorted(self.keys.items())),'revoked':sorted(self.revoked)}
    @property
    def authority_id(self): return digest(self.descriptor)
    def validate(self):
        if self.kind not in ('root','recovery'): raise IntegrityError('kind')
        if type(self.version) is not int or type(self.generation) is not int or min(self.version,self.generation)<1: raise IntegrityError('version/generation')
        if type(self.threshold) is not int or self.threshold<1: raise IntegrityError('threshold')
        active=set(self.keys)-set(self.revoked)
        if self.threshold>len(active): raise IntegrityError('threshold exceeds active')
        for sid,hx in self.keys.items():
            k=bytes.fromhex(hx)
            if sid!=kid(k): raise IntegrityError('key id')
        return True

def verify(a,p,sigs):
    a.validate(); seen=set(); valid=[]
    for s in sigs:
        if s.signer_id in seen or s.signer_id in a.revoked: continue
        seen.add(s.signer_id); hx=a.keys.get(s.signer_id)
        if hx and hmac.compare_digest(sign(bytes.fromhex(hx),p),s.signature): valid.append(s.signer_id)
    if len(valid)<a.threshold: raise ThresholdError(f'{a.kind} valid={len(valid)} threshold={a.threshold}')
    return tuple(sorted(valid))

def rotate_payload(root,old,new): return {'kind':'recovery-rotation','root':root.authority_id,'old':old.authority_id,'new':new.descriptor}
def recover_payload(oldroot,newroot,recovery): return {'kind':'root-recovery','old_root':oldroot.authority_id,'recovery':recovery.authority_id,'new_root':newroot.descriptor}

class Store:
    def __init__(self,path): self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True)
    def save(self,o):
        fd,tmp=tempfile.mkstemp(dir=str(self.path.parent))
        try:
            with os.fdopen(fd,'w') as f: json.dump(o,f,sort_keys=True); f.flush(); os.fsync(f.fileno())
            os.replace(tmp,self.path)
        finally:
            if os.path.exists(tmp): os.unlink(tmp)
    def load(self): return json.loads(self.path.read_text())

class Lifecycle:
    def __init__(self,root,recovery,store=None):
        root.validate(); recovery.validate()
        self.bootstrap_root=root.authority_id; self.bootstrap_recovery=recovery.authority_id
        self.roots={root.authority_id:root}; self.current_root_id=root.authority_id; self.recoveries={recovery.authority_id:recovery}; self.current_recovery_id=recovery.authority_id
        self.transitions=[]; self.root_recoveries=[]; self.store=store
        if store and store.path.exists(): self._load(store.load())
        elif store: self._persist()
    def current_root(self): return self.roots[self.current_root_id]
    def current_recovery(self): return self.recoveries[self.current_recovery_id]
    def _enc(self,a): return a.descriptor
    def _dec(self,x): return Authority(x['kind'],x['registry_id'],x['version'],x['generation'],x['threshold'],dict(x['keys']),tuple(x.get('revoked',[])))
    def _persist(self):
        if self.store:self.store.save({'bootstrap_root':self.bootstrap_root,'bootstrap_recovery':self.bootstrap_recovery,'roots':{k:self._enc(v) for k,v in self.roots.items()},'current_root_id':self.current_root_id,'recoveries':{k:self._enc(v) for k,v in self.recoveries.items()},'current_recovery_id':self.current_recovery_id,'transitions':self.transitions,'root_recoveries':self.root_recoveries})
    def _load(self,r):
        if r['bootstrap_root']!=self.bootstrap_root or r['bootstrap_recovery']!=self.bootstrap_recovery: raise IntegrityError('bootstrap substitution')
        self.roots={k:self._dec(v) for k,v in r['roots'].items()}; self.current_root_id=r['current_root_id']; self.recoveries={k:self._dec(v) for k,v in r['recoveries'].items()}; self.current_recovery_id=r['current_recovery_id']; self.transitions=list(r['transitions']); self.root_recoveries=list(r['root_recoveries']); self._verify_history()
    def rotate_recovery(self,new,old_sigs,new_sigs,root_sigs):
        old=self.current_recovery(); root=self.current_root(); new.validate(); p=rotate_payload(root,old,new)
        if new.kind!='recovery' or new.registry_id!=old.registry_id or new.registry_id!=root.registry_id: raise IntegrityError('binding')
        if new.version!=old.version+1 or new.generation<=old.generation: raise RollbackError('successor')
        verify(old,p,old_sigs); verify(new,p,new_sigs); verify(root,p,root_sigs)
        self.recoveries[new.authority_id]=new; self.current_recovery_id=new.authority_id
        self.transitions.append({'old':old.authority_id,'new':new.authority_id,'root':root.authority_id,'old_sigs':[asdict(x) for x in old_sigs],'new_sigs':[asdict(x) for x in new_sigs],'root_sigs':[asdict(x) for x in root_sigs]}); self._persist(); return new.authority_id
    def recover_root(self,newroot,recovery_sigs):
        rec=self.current_recovery(); oldroot=self.current_root(); newroot.validate(); p=recover_payload(oldroot,newroot,rec)
        if newroot.kind!='root' or newroot.registry_id!=oldroot.registry_id: raise IntegrityError('root binding')
        if newroot.version!=oldroot.version+1 or newroot.generation!=oldroot.generation+1: raise RollbackError('root successor')
        verify(rec,p,recovery_sigs); old=oldroot; self.roots[newroot.authority_id]=newroot; self.current_root_id=newroot.authority_id
        self.root_recoveries.append({'old_root':old.authority_id,'new_root':newroot.authority_id,'recovery':rec.authority_id,'recovery_version':rec.version,'recovery_generation':rec.generation,'sigs':[asdict(x) for x in recovery_sigs]}); self._persist(); return newroot.authority_id
    def historical_recovery(self,new_root_id):
        for x in self.root_recoveries:
            if x['new_root']==new_root_id:return self.recoveries[x['recovery']]
        raise KeyError(new_root_id)
    def final_boundary(self): raise RecoveryBoundaryError('root quorum + recovery quorum unavailable/compromised => external bootstrap required')
    def _verify_history(self):
        for rid,r in self.roots.items():
            r.validate()
            if rid!=r.authority_id: raise IntegrityError('root id mismatch')
        if self.bootstrap_root not in self.roots or self.current_root_id not in self.roots: raise IntegrityError('root history binding')
        rs=sorted(self.recoveries.values(),key=lambda a:a.version)
        if not rs or rs[0].authority_id!=self.bootstrap_recovery: raise IntegrityError('bootstrap recovery')
        if self.current_recovery().version!=rs[-1].version: raise RollbackError('recovery pointer')
        bynew={x['new']:x for x in self.transitions}
        for old,new in zip(rs,rs[1:]):
            if new.version!=old.version+1 or new.generation<=old.generation: raise RollbackError('history')
            t=bynew.get(new.authority_id)
            if not t or t['old']!=old.authority_id: raise IntegrityError('transition proof missing')
            root=self.roots.get(t['root'])
            if root is None: raise IntegrityError('unknown coauthorizing root')
            p=rotate_payload(root,old,new)
            verify(old,p,tuple(Sig(**x) for x in t['old_sigs'])); verify(new,p,tuple(Sig(**x) for x in t['new_sigs']))
            verify(root,p,tuple(Sig(**x) for x in t['root_sigs']))
        for x in self.root_recoveries:
            rec=self.recoveries.get(x['recovery'])
            if not rec or x['recovery_version']!=rec.version or x['recovery_generation']!=rec.generation: raise IntegrityError('historical recovery identity')

class UnsafeSelfSwap:
    def rotate(self,old,new,sigs):
        p={'kind':'unsafe','old':old.authority_id,'new':new.descriptor}; verify(old,p,sigs); return new
