from __future__ import annotations
import hashlib,hmac,json,sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any
class BundleError(ValueError): pass
class AuthenticationError(BundleError): pass
class RollbackError(BundleError): pass
class SubstitutionError(BundleError): pass
class MixAndMatchError(BundleError): pass
class AuthorityError(BundleError): pass
class ReplayError(BundleError): pass
def _pos(n,v):
    if type(v) is not int or v<1: raise BundleError(f'invalid {n}')
def canonical(o): return json.dumps(o,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
def digest(o): return hashlib.sha256(canonical(o)).hexdigest()
def mac(k,o): return hmac.new(k,canonical(o),hashlib.sha256).hexdigest()
@dataclass(frozen=True)
class PolicyDocument:
    policy_id:str; version:int; generation:int; effective_from:int; effective_until:int|None; required_logs:int; required_operators:int; mode:str
    def validate(self):
        if not self.policy_id: raise BundleError('missing policy id')
        for n in ('version','generation','effective_from','required_logs'): _pos(n,getattr(self,n))
        if type(self.required_operators) is not int or self.required_operators<0: raise BundleError('invalid required_operators')
        if self.effective_until is not None and (type(self.effective_until) is not int or self.effective_until<=self.effective_from): raise BundleError('invalid policy interval')
        if self.mode not in {'HISTORICAL','CURRENT_POLICY'}: raise BundleError('invalid mode')
    def as_dict(self):
        self.validate(); return {'policy_id':self.policy_id,'version':self.version,'generation':self.generation,'effective_from':self.effective_from,'effective_until':self.effective_until,'required_logs':self.required_logs,'required_operators':self.required_operators,'mode':self.mode}
    @property
    def content_digest(self): return digest(self.as_dict())
@dataclass(frozen=True)
class TrustDocument:
    snapshot_id:str; version:int; generation:int; issued_at:int; expires_at:int; logs:tuple[tuple[str,str,str,str],...]
    def validate(self):
        if not self.snapshot_id: raise BundleError('missing trust snapshot id')
        for n in ('version','generation','issued_at','expires_at'): _pos(n,getattr(self,n))
        if self.expires_at<=self.issued_at: raise BundleError('invalid trust interval')
        seen=set()
        for row in self.logs:
            if not isinstance(row,tuple) or len(row)!=4 or not all(isinstance(x,str) and x for x in row): raise BundleError('invalid trust log')
            if row[0] in seen: raise BundleError('duplicate log id')
            seen.add(row[0])
    def as_dict(self):
        self.validate(); return {'snapshot_id':self.snapshot_id,'version':self.version,'generation':self.generation,'issued_at':self.issued_at,'expires_at':self.expires_at,'logs':[list(x) for x in sorted(self.logs)]}
    @property
    def content_digest(self): return digest(self.as_dict())
@dataclass(frozen=True)
class BundleManifest:
    bundle_id:str; version:int; generation:int; issued_at:int; expires_at:int; authority_generation:int; policy_digest:str; trust_digest:str
    def validate(self):
        if not self.bundle_id: raise BundleError('missing bundle id')
        for n in ('version','generation','issued_at','expires_at','authority_generation'): _pos(n,getattr(self,n))
        if self.expires_at<=self.issued_at: raise BundleError('invalid bundle interval')
        for n in ('policy_digest','trust_digest'):
            v=getattr(self,n)
            if not isinstance(v,str) or len(v)!=64: raise BundleError(f'invalid {n}')
            int(v,16)
    def as_dict(self):
        self.validate(); return {'bundle_id':self.bundle_id,'version':self.version,'generation':self.generation,'issued_at':self.issued_at,'expires_at':self.expires_at,'authority_generation':self.authority_generation,'policy_digest':self.policy_digest,'trust_digest':self.trust_digest}
    @property
    def content_digest(self): return digest(self.as_dict())
@dataclass(frozen=True)
class SignedBundle:
    manifest:BundleManifest; policy:PolicyDocument; trust:TrustDocument; signer_id:str; signature:str
    @classmethod
    def issue(cls,*,manifest,policy,trust,signer_id,key): return cls(manifest,policy,trust,signer_id,mac(key,manifest.as_dict()))
    def validate_content_binding(self):
        self.manifest.validate(); self.policy.validate(); self.trust.validate()
        if self.policy.content_digest!=self.manifest.policy_digest: raise MixAndMatchError('policy digest does not match manifest')
        if self.trust.content_digest!=self.manifest.trust_digest: raise MixAndMatchError('trust digest does not match manifest')
class Authority:
    def __init__(self,generation,signer_id,key):
        _pos('authority generation',generation)
        if not signer_id or not key: raise AuthorityError('invalid authority')
        self.generation=generation; self.signer_id=signer_id; self._key=key
    def verify(self,bundle):
        if bundle.manifest.authority_generation!=self.generation: raise AuthorityError('bundle authority generation mismatch')
        if bundle.signer_id!=self.signer_id: raise AuthenticationError('unknown signer')
        if not hmac.compare_digest(mac(self._key,bundle.manifest.as_dict()),bundle.signature): raise AuthenticationError('bad bundle signature')
@dataclass(frozen=True)
class DecisionBinding:
    bundle_id:str; bundle_version:int; bundle_generation:int; bundle_digest:str; policy_digest:str; trust_digest:str
class BundleStore:
    def __init__(self,path:str|Path,authority:Authority):
        self.path=str(path); self.authority=authority; self.db=sqlite3.connect(self.path)
        self.db.execute('PRAGMA foreign_keys=ON')
        self.db.executescript('''
        CREATE TABLE IF NOT EXISTS bundles(bundle_id TEXT,version INTEGER,generation INTEGER,digest TEXT,authority_generation INTEGER,issued_at INTEGER,expires_at INTEGER,manifest_json TEXT,signature TEXT,signer_id TEXT,PRIMARY KEY(bundle_id,version,generation),UNIQUE(bundle_id,version),UNIQUE(bundle_id,generation));
        CREATE TABLE IF NOT EXISTS policies(bundle_id TEXT,version INTEGER,generation INTEGER,digest TEXT,document_json TEXT,PRIMARY KEY(bundle_id,version,generation),FOREIGN KEY(bundle_id,version,generation) REFERENCES bundles(bundle_id,version,generation) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS trusts(bundle_id TEXT,version INTEGER,generation INTEGER,digest TEXT,document_json TEXT,PRIMARY KEY(bundle_id,version,generation),FOREIGN KEY(bundle_id,version,generation) REFERENCES bundles(bundle_id,version,generation) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS active(singleton INTEGER PRIMARY KEY CHECK(singleton=1),bundle_id TEXT,version INTEGER,generation INTEGER,digest TEXT);
        '''); self.db.commit()
    def close(self): self.db.close()
    def _active_row(self): return self.db.execute('SELECT bundle_id,version,generation,digest FROM active WHERE singleton=1').fetchone()
    def accept(self,bundle:SignedBundle,*,now:int,failpoint:str|None=None):
        _pos('now',now); bundle.validate_content_binding(); self.authority.verify(bundle); m=bundle.manifest
        if now<m.issued_at or now>m.expires_at: raise RollbackError('bundle outside authenticated publication window')
        active=self._active_row()
        if active:
            cid,cv,cg,cd=active
            if m.bundle_id!=cid: raise SubstitutionError('bundle lineage changed')
            if m.version==cv and m.generation==cg:
                if m.content_digest!=cd: raise SubstitutionError('same coordinates, different manifest')
                return self.binding(m.bundle_id,m.version,m.generation)
            if m.version<=cv or m.generation<=cg: raise RollbackError('bundle rollback')
            if m.version!=cv+1 or m.generation!=cg+1: raise RollbackError('bundle continuity gap')
        mj=canonical(m.as_dict()).decode(); pj=canonical(bundle.policy.as_dict()).decode(); tj=canonical(bundle.trust.as_dict()).decode()
        try:
            self.db.execute('BEGIN IMMEDIATE')
            locked=self._active_row()
            if locked!=active: raise RollbackError('active bundle changed concurrently')
            self.db.execute('INSERT INTO bundles VALUES(?,?,?,?,?,?,?,?,?,?)',(m.bundle_id,m.version,m.generation,m.content_digest,m.authority_generation,m.issued_at,m.expires_at,mj,bundle.signature,bundle.signer_id))
            if failpoint=='after_manifest': raise RuntimeError('injected crash after manifest')
            self.db.execute('INSERT INTO policies VALUES(?,?,?,?,?)',(m.bundle_id,m.version,m.generation,bundle.policy.content_digest,pj))
            if failpoint=='after_policy': raise RuntimeError('injected crash after policy')
            self.db.execute('INSERT INTO trusts VALUES(?,?,?,?,?)',(m.bundle_id,m.version,m.generation,bundle.trust.content_digest,tj))
            if failpoint=='after_trust': raise RuntimeError('injected crash after trust')
            self.db.execute('INSERT INTO active VALUES(1,?,?,?,?) ON CONFLICT(singleton) DO UPDATE SET bundle_id=excluded.bundle_id,version=excluded.version,generation=excluded.generation,digest=excluded.digest',(m.bundle_id,m.version,m.generation,m.content_digest))
            if failpoint=='before_commit': raise RuntimeError('injected crash before commit')
            self.db.commit()
        except Exception:
            self.db.rollback(); raise
        return self.binding(m.bundle_id,m.version,m.generation)
    def binding(self,bid,v,g):
        row=self.db.execute('SELECT b.digest,b.manifest_json,p.digest,p.document_json,t.digest,t.document_json FROM bundles b JOIN policies p USING(bundle_id,version,generation) JOIN trusts t USING(bundle_id,version,generation) WHERE b.bundle_id=? AND b.version=? AND b.generation=?',(bid,v,g)).fetchone()
        if not row: raise ReplayError('bundle tuple unavailable or partial')
        bd,mj,pd,pj,td,tj=row
        try:
            manifest=json.loads(mj); policy=json.loads(pj); trust=json.loads(tj)
        except Exception as exc: raise ReplayError('stored bundle object is not valid JSON') from exc
        if digest(manifest)!=bd or digest(policy)!=pd or digest(trust)!=td: raise ReplayError('stored object digest mismatch')
        if manifest.get('bundle_id')!=bid or manifest.get('version')!=v or manifest.get('generation')!=g: raise ReplayError('stored manifest coordinates mismatch')
        if manifest.get('policy_digest')!=pd or manifest.get('trust_digest')!=td: raise ReplayError('stored manifest/object binding mismatch')
        return DecisionBinding(bid,v,g,bd,pd,td)
    def active_binding(self):
        row=self._active_row()
        if not row: raise ReplayError('no active bundle')
        return self.binding(row[0],row[1],row[2])
    def replay(self,binding):
        observed=self.binding(binding.bundle_id,binding.bundle_version,binding.bundle_generation)
        if observed!=binding: raise ReplayError('historical bundle content changed')
        return observed
    def rotate_authority(self,new_authority):
        if new_authority.generation!=self.authority.generation+1: raise AuthorityError('authority generation must advance exactly once')
        self.authority=new_authority
class UnsafeSplitHistories:
    def __init__(self): self.policy=None; self.trust=None
    def update_policy(self,release,d): self.policy=(release,d)
    def update_trust(self,release,d): self.trust=(release,d)
    def current_pair_is_coherent(self): return bool(self.policy and self.trust)
