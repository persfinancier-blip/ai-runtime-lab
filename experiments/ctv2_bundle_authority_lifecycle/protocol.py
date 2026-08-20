from __future__ import annotations
import hashlib,hmac,json,sqlite3
from dataclasses import dataclass
from pathlib import Path

class Error(RuntimeError): pass
class ThresholdError(Error): pass
class StaleRoot(Error): pass
class AuthenticationError(Error): pass
class RecoveryError(Error): pass
class ReplayError(Error): pass
class SubstitutionError(Error): pass

def canonical(o): return json.dumps(o,sort_keys=True,separators=(',',':')).encode()
def digest(o): return hashlib.sha256(canonical(o)).hexdigest()
def kid(k:bytes): return hashlib.sha256(k).hexdigest()[:16]
def sign(k:bytes,o): return hmac.new(k,canonical(o),hashlib.sha256).hexdigest()

@dataclass(frozen=True)
class Sig: signer_id:str; signature:str

@dataclass(frozen=True)
class Root:
    provider_id:str; version:int; epoch:int; threshold:int
    root_keys:dict[str,str]; bundle_keys:dict[str,str]
    revoked_root:tuple[str,...]=(); revoked_bundle:tuple[str,...]=()
    def desc(self):
        return {'provider_id':self.provider_id,'version':self.version,'epoch':self.epoch,'threshold':self.threshold,
                'root_keys':dict(sorted(self.root_keys.items())),'bundle_keys':dict(sorted(self.bundle_keys.items())),
                'revoked_root':sorted(self.revoked_root),'revoked_bundle':sorted(self.revoked_bundle)}
    @property
    def root_digest(self): return digest(self.desc())
    def validate(self):
        if type(self.version) is not int or self.version<1: raise Error('bad root version')
        if type(self.epoch) is not int or self.epoch<1: raise Error('bad root epoch')
        active=set(self.root_keys)-set(self.revoked_root)
        if type(self.threshold) is not int or self.threshold<1 or self.threshold>len(active): raise Error('bad threshold')
        for sid,hx in {**self.root_keys,**self.bundle_keys}.items():
            if sid!=kid(bytes.fromhex(hx)): raise SubstitutionError('key id/material mismatch')

@dataclass(frozen=True)
class Recovery:
    generation:int; threshold:int; keys:dict[str,str]
    def validate(self):
        if type(self.generation) is not int or self.generation<1: raise RecoveryError('bad recovery generation')
        if type(self.threshold) is not int or self.threshold<1 or self.threshold>len(self.keys): raise RecoveryError('bad recovery threshold')
        for sid,hx in self.keys.items():
            if sid!=kid(bytes.fromhex(hx)): raise SubstitutionError('recovery key id/material mismatch')
    def desc(self): return {'generation':self.generation,'threshold':self.threshold,'keys':dict(sorted(self.keys.items()))}
    @property
    def recovery_digest(self): return digest(self.desc())

@dataclass(frozen=True)
class Bundle:
    bundle_id:str; version:int; generation:int; issued_at:int
    root_version:int; root_epoch:int; root_digest:str
    signer_id:str; payload_digest:str; signature:str
    @property
    def unsigned(self):
        return {'bundle_id':self.bundle_id,'version':self.version,'generation':self.generation,'issued_at':self.issued_at,
                'root_version':self.root_version,'root_epoch':self.root_epoch,'root_digest':self.root_digest,
                'signer_id':self.signer_id,'payload_digest':self.payload_digest}
    @classmethod
    def issue(cls,*,bundle_id,version,generation,issued_at,root,signer_id,key,payload_digest):
        tmp={'bundle_id':bundle_id,'version':version,'generation':generation,'issued_at':issued_at,
             'root_version':root.version,'root_epoch':root.epoch,'root_digest':root.root_digest,
             'signer_id':signer_id,'payload_digest':payload_digest}
        return cls(**tmp,signature=sign(key,tmp))
    @property
    def bundle_digest(self): return digest({**self.unsigned,'signature':self.signature})

def verify_threshold(keys,threshold,revoked,payload,sigs):
    seen=set(); valid=[]
    for s in sigs:
        if s.signer_id in seen: continue
        seen.add(s.signer_id)
        if s.signer_id in revoked: continue
        hx=keys.get(s.signer_id)
        if hx and hmac.compare_digest(sign(bytes.fromhex(hx),payload),s.signature): valid.append(s.signer_id)
    if len(valid)<threshold: raise ThresholdError(f'valid={len(valid)} threshold={threshold}')
    return tuple(sorted(valid))

def transition_payload(old,new,kind):
    return {'kind':kind,'predecessor':old.desc(),'candidate':new.desc()}

class LifecycleStore:
    def __init__(self,path,initial:Root,recovery:Recovery):
        initial.validate(); recovery.validate(); self.path=str(path)
        c=self.connect()
        c.executescript('''
        PRAGMA journal_mode=WAL;
        CREATE TABLE IF NOT EXISTS roots(provider_id TEXT,version INTEGER,epoch INTEGER,root_digest TEXT UNIQUE,root_json TEXT,kind TEXT,PRIMARY KEY(provider_id,version,epoch));
        CREATE TABLE IF NOT EXISTS active_root(singleton INTEGER PRIMARY KEY CHECK(singleton=1),provider_id TEXT,version INTEGER,epoch INTEGER,root_digest TEXT);
        CREATE TABLE IF NOT EXISTS recovery_authority(singleton INTEGER PRIMARY KEY CHECK(singleton=1),recovery_digest TEXT, recovery_json TEXT);
        CREATE TABLE IF NOT EXISTS bundles(bundle_id TEXT,version INTEGER,generation INTEGER,bundle_digest TEXT UNIQUE,root_digest TEXT,signer_id TEXT,bundle_json TEXT,PRIMARY KEY(bundle_id,version,generation));
        CREATE TABLE IF NOT EXISTS active_bundle(singleton INTEGER PRIMARY KEY CHECK(singleton=1),bundle_id TEXT,version INTEGER,generation INTEGER,bundle_digest TEXT);
        ''')
        if c.execute('SELECT 1 FROM active_root').fetchone() is None:
            c.execute('INSERT INTO roots VALUES(?,?,?,?,?,?)',(initial.provider_id,initial.version,initial.epoch,initial.root_digest,json.dumps(initial.desc(),sort_keys=True),'bootstrap'))
            c.execute('INSERT INTO active_root VALUES(1,?,?,?,?)',(initial.provider_id,initial.version,initial.epoch,initial.root_digest))
        if c.execute('SELECT 1 FROM recovery_authority').fetchone() is None:
            c.execute('INSERT INTO recovery_authority VALUES(1,?,?)',(recovery.recovery_digest,json.dumps(recovery.desc(),sort_keys=True)))
        c.commit(); c.close(); self.recovery=self._load_recovery()
    def connect(self):
        c=sqlite3.connect(self.path,timeout=5,isolation_level=None,check_same_thread=False); c.row_factory=sqlite3.Row; return c
    @staticmethod
    def _root(row):
        x=json.loads(row['root_json']); r=Root(x['provider_id'],x['version'],x['epoch'],x['threshold'],dict(x['root_keys']),dict(x['bundle_keys']),tuple(x['revoked_root']),tuple(x['revoked_bundle'])); r.validate()
        if r.root_digest!=row['root_digest']: raise SubstitutionError('stored root digest mismatch')
        return r
    def _load_recovery(self):
        c=self.connect()
        try:
            row=c.execute('SELECT * FROM recovery_authority WHERE singleton=1').fetchone(); x=json.loads(row['recovery_json']); r=Recovery(x['generation'],x['threshold'],dict(x['keys'])); r.validate()
            if r.recovery_digest!=row['recovery_digest']: raise SubstitutionError('stored recovery digest mismatch')
            return r
        finally:c.close()
    def current_root(self):
        c=self.connect()
        try:return self._root(c.execute('SELECT r.* FROM roots r JOIN active_root a ON r.root_digest=a.root_digest').fetchone())
        finally:c.close()
    def _verify_bundle(self,root,b):
        if (b.root_version,b.root_epoch,b.root_digest)!=(root.version,root.epoch,root.root_digest): raise StaleRoot('bundle bound to stale root')
        if b.signer_id in root.revoked_bundle or b.signer_id not in root.bundle_keys: raise AuthenticationError('bundle signer not current')
        key=bytes.fromhex(root.bundle_keys[b.signer_id])
        if not hmac.compare_digest(sign(key,b.unsigned),b.signature): raise AuthenticationError('bad bundle signature')
    def publish(self,b:Bundle,failpoint=None):
        c=self.connect()
        try:
            c.execute('BEGIN IMMEDIATE')
            root=self._root(c.execute('SELECT r.* FROM roots r JOIN active_root a ON r.root_digest=a.root_digest').fetchone())
            self._verify_bundle(root,b)
            active=c.execute('SELECT * FROM active_bundle').fetchone()
            if active:
                if b.bundle_id!=active['bundle_id']: raise SubstitutionError('bundle lineage')
                if b.version<=active['version'] or b.generation<=active['generation']: raise ReplayError('bundle rollback')
                if b.version!=active['version']+1 or b.generation!=active['generation']+1: raise ReplayError('bundle gap')
            if failpoint=='before_insert': raise RuntimeError('crash')
            c.execute('INSERT INTO bundles VALUES(?,?,?,?,?,?,?)',(b.bundle_id,b.version,b.generation,b.bundle_digest,b.root_digest,b.signer_id,json.dumps({**b.unsigned,'signature':b.signature},sort_keys=True)))
            if failpoint=='after_insert': raise RuntimeError('crash')
            c.execute('INSERT INTO active_bundle VALUES(1,?,?,?,?) ON CONFLICT(singleton) DO UPDATE SET bundle_id=excluded.bundle_id,version=excluded.version,generation=excluded.generation,bundle_digest=excluded.bundle_digest',(b.bundle_id,b.version,b.generation,b.bundle_digest))
            c.commit(); return b.bundle_digest
        except Exception:
            if c.in_transaction:c.rollback()
            raise
        finally:c.close()
    def transition(self,new:Root,old_sigs=(),new_sigs=(),recovery_sigs=(),kind='rotation',failpoint=None):
        new.validate(); c=self.connect()
        try:
            c.execute('BEGIN IMMEDIATE')
            old=self._root(c.execute('SELECT r.* FROM roots r JOIN active_root a ON r.root_digest=a.root_digest').fetchone())
            if new.provider_id!=old.provider_id or new.version!=old.version+1: raise StaleRoot()
            p=transition_payload(old,new,kind)
            if kind=='rotation':
                if new.epoch!=old.epoch: raise StaleRoot()
                verify_threshold(old.root_keys,old.threshold,old.revoked_root,p,old_sigs)
                verify_threshold(new.root_keys,new.threshold,new.revoked_root,p,new_sigs)
            elif kind=='recovery':
                if new.epoch!=old.epoch+1: raise RecoveryError()
                verify_threshold(self.recovery.keys,self.recovery.threshold,(),p,recovery_sigs)
            else: raise Error('bad transition kind')
            if failpoint=='before_insert': raise RuntimeError('crash')
            c.execute('INSERT INTO roots VALUES(?,?,?,?,?,?)',(new.provider_id,new.version,new.epoch,new.root_digest,json.dumps(new.desc(),sort_keys=True),kind))
            if failpoint=='after_insert': raise RuntimeError('crash')
            changed=c.execute('UPDATE active_root SET provider_id=?,version=?,epoch=?,root_digest=? WHERE singleton=1 AND root_digest=?',(new.provider_id,new.version,new.epoch,new.root_digest,old.root_digest)).rowcount
            if changed!=1: raise StaleRoot()
            c.commit(); return new.root_digest
        except Exception:
            if c.in_transaction:c.rollback()
            raise
        finally:c.close()
    def replay(self,bundle_digest):
        c=self.connect()
        try:
            br=c.execute('SELECT * FROM bundles WHERE bundle_digest=?',(bundle_digest,)).fetchone()
            if not br: raise ReplayError('bundle unavailable')
            rr=c.execute('SELECT * FROM roots WHERE root_digest=?',(br['root_digest'],)).fetchone()
            if not rr: raise ReplayError('historical root unavailable')
            root=self._root(rr); raw=json.loads(br['bundle_json'])
            b=Bundle(raw['bundle_id'],raw['version'],raw['generation'],raw['issued_at'],raw['root_version'],raw['root_epoch'],raw['root_digest'],raw['signer_id'],raw['payload_digest'],raw['signature'])
            if b.bundle_digest!=bundle_digest: raise ReplayError('stored bundle changed')
            self._verify_bundle(root,b)
            return {'bundle_digest':bundle_digest,'historical_root_digest':root.root_digest,'root_version':root.version,'root_epoch':root.epoch,'signer_id':b.signer_id}
        finally:c.close()

class UnsafeAuthoritySwap:
    def __init__(self, signer_id,key): self.signer_id=signer_id; self.key=key
    def rotate_authority(self,signer_id,key): self.signer_id=signer_id; self.key=key
