from __future__ import annotations
import hashlib,hmac,json,sqlite3
from dataclasses import asdict,dataclass
from pathlib import Path
from experiments.anchor_threshold_root.protocol import RootState,RecoveryAuthority,Signature,key_id,root_descriptor,rotation_payload,recovery_payload,verify_threshold,sign
from experiments.sink_registry_binding.protocol import RegistryEntry,canon

class LifecycleError(RuntimeError): pass
class AuthorityRollback(LifecycleError): pass
class AuthoritySubstitution(LifecycleError): pass
class HistoricalAuthorityMissing(LifecycleError): pass
class EntryAuthError(LifecycleError): pass
class UnsafeRecovery(LifecycleError): pass

def digest_obj(o): return hashlib.sha256(json.dumps(o,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def root_id(r:RootState): return digest_obj(root_descriptor(r))
def recovery_descriptor(r:RecoveryAuthority): return {'generation':r.generation,'threshold':r.threshold,'keys':dict(sorted(r.keys.items())),'revoked':sorted(r.revoked)}
def recovery_id(r:RecoveryAuthority): return digest_obj(recovery_descriptor(r))

def _root_from_json(raw):
    x=json.loads(raw); r=RootState(x['provider_id'],x['version'],x['authority_epoch'],x['threshold'],dict(x['keys']),tuple(x.get('revoked',[]))); r.validate(); return r

def _sig_json(items): return json.dumps([asdict(x) for x in items],sort_keys=True,separators=(',',':'))
def _sig_parse(raw): return tuple(Signature(x['signer_id'],x['signature']) for x in json.loads(raw))
def _recovery_from_json(raw):
    x=json.loads(raw); r=RecoveryAuthority(x['generation'],x['threshold'],dict(x['keys']),tuple(x.get('revoked',[]))); r.validate(); return r

class DurableRegistryAuthority:
    """Threshold-authorized, restart-persistent signing authority for LAB-075 entries.

    Current authority gates new publication. Historical authority rows remain only
    for verification of entries already bound under that exact generation.
    """
    def __init__(self,path,bootstrap:RootState,recovery:RecoveryAuthority):
        bootstrap.validate(); recovery.validate(); self.path=str(path); self.recovery=recovery
        q=self._con(); self._schema(q)
        if q.execute('SELECT COUNT(*) FROM registry_authority_head').fetchone()[0]==0:
            self._put_root(q,bootstrap,kind='bootstrap',predecessor=None,proof_old='[]',proof_new='[]',proof_recovery='[]')
            q.execute('INSERT INTO registry_authority_head VALUES(1,?,?,?)',(root_id(bootstrap),bootstrap.version,bootstrap.authority_epoch))
            rid=recovery_id(recovery)
            q.execute('INSERT INTO registry_recovery_authority VALUES(?,?)',(rid,json.dumps(recovery_descriptor(recovery),sort_keys=True,separators=(',',':'))))
            q.execute('INSERT INTO registry_authority_meta VALUES(1,?,?)',(root_id(bootstrap),rid))
            q.commit()
        q.close(); self.verify_durable(bootstrap,recovery)
    def _con(self):
        q=sqlite3.connect(self.path,timeout=5); q.execute('PRAGMA busy_timeout=5000'); return q
    def _schema(self,q):
        q.executescript('''
        CREATE TABLE IF NOT EXISTS registry_authorities(
          authority_id TEXT PRIMARY KEY,version INTEGER NOT NULL,epoch INTEGER NOT NULL,body TEXT NOT NULL,
          transition_kind TEXT NOT NULL,predecessor_id TEXT,proof_old TEXT NOT NULL,proof_new TEXT NOT NULL,proof_recovery TEXT NOT NULL);
        CREATE UNIQUE INDEX IF NOT EXISTS registry_authority_versions ON registry_authorities(version);
        CREATE TABLE IF NOT EXISTS registry_authority_head(singleton INTEGER PRIMARY KEY CHECK(singleton=1),authority_id TEXT NOT NULL,version INTEGER NOT NULL,epoch INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS registry_authority_meta(singleton INTEGER PRIMARY KEY CHECK(singleton=1),bootstrap_id TEXT NOT NULL,recovery_id TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS registry_recovery_authority(recovery_id TEXT PRIMARY KEY,body TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS registry_authorized_entries(entry_digest TEXT PRIMARY KEY,entry_json TEXT NOT NULL,authority_id TEXT NOT NULL,authority_version INTEGER NOT NULL);
        ''')
    def _put_root(self,q,r,*,kind,predecessor,proof_old,proof_new,proof_recovery):
        body=json.dumps(root_descriptor(r),sort_keys=True,separators=(',',':')); aid=root_id(r)
        q.execute('INSERT INTO registry_authorities VALUES(?,?,?,?,?,?,?,?,?)',(aid,r.version,r.authority_epoch,body,kind,predecessor,proof_old,proof_new,proof_recovery)); return aid
    def _load_root(self,q,aid):
        row=q.execute('SELECT body FROM registry_authorities WHERE authority_id=?',(aid,)).fetchone()
        if row is None: raise HistoricalAuthorityMissing(aid)
        r=_root_from_json(row[0])
        if root_id(r)!=aid: raise AuthoritySubstitution('authority content digest mismatch')
        return r
    def _load_recovery(self,q,rid):
        row=q.execute('SELECT body FROM registry_recovery_authority WHERE recovery_id=?',(rid,)).fetchone()
        if row is None: raise UnsafeRecovery('missing durable recovery authority')
        r=_recovery_from_json(row[0])
        if recovery_id(r)!=rid: raise UnsafeRecovery('recovery authority content digest mismatch')
        return r
    def current(self):
        q=self._con()
        try:
            aid,v,e=q.execute('SELECT authority_id,version,epoch FROM registry_authority_head WHERE singleton=1').fetchone(); r=self._load_root(q,aid)
            if (r.version,r.authority_epoch)!=(v,e): raise AuthoritySubstitution('head relational mismatch')
            return r
        finally:q.close()
    def assert_current(self,candidate:RootState):
        current=self.current()
        if root_id(candidate)!=root_id(current): raise AuthorityRollback('ambient authority is not durable head')
        return current
    def rotate(self,new:RootState,old_sigs,new_sigs):
        new.validate(); q=self._con()
        try:
            q.execute('BEGIN IMMEDIATE'); aid,v,e=q.execute('SELECT authority_id,version,epoch FROM registry_authority_head WHERE singleton=1').fetchone(); old=self._load_root(q,aid)
            if new.provider_id!=old.provider_id or new.authority_epoch!=old.authority_epoch or new.version!=old.version+1: raise AuthorityRollback('invalid successor')
            p=rotation_payload(old,new); verify_threshold(old.keys,old.threshold,old.revoked,p,old_sigs); verify_threshold(new.keys,new.threshold,new.revoked,p,new_sigs)
            nid=self._put_root(q,new,kind='rotation',predecessor=aid,proof_old=_sig_json(old_sigs),proof_new=_sig_json(new_sigs),proof_recovery='[]')
            changed=q.execute('UPDATE registry_authority_head SET authority_id=?,version=?,epoch=? WHERE singleton=1 AND authority_id=? AND version=? AND epoch=?',(nid,new.version,new.authority_epoch,aid,v,e)).rowcount
            if changed!=1: raise AuthorityRollback('rotation CAS lost')
            q.commit(); return new
        except:
            if q.in_transaction:q.rollback()
            raise
        finally:q.close()
    def recover(self,new:RootState,recovery_sigs):
        new.validate(); q=self._con()
        try:
            q.execute('BEGIN IMMEDIATE'); aid,v,e=q.execute('SELECT authority_id,version,epoch FROM registry_authority_head WHERE singleton=1').fetchone(); old=self._load_root(q,aid)
            if new.provider_id!=old.provider_id or new.authority_epoch!=old.authority_epoch+1 or new.version!=old.version+1: raise UnsafeRecovery('invalid recovery successor')
            rid=q.execute('SELECT recovery_id FROM registry_authority_meta WHERE singleton=1').fetchone()[0]; rec=self._load_recovery(q,rid)
            p=recovery_payload(old,new,rec.generation); verify_threshold(rec.keys,rec.threshold,rec.revoked,p,recovery_sigs)
            nid=self._put_root(q,new,kind='recovery',predecessor=aid,proof_old='[]',proof_new='[]',proof_recovery=_sig_json(recovery_sigs))
            changed=q.execute('UPDATE registry_authority_head SET authority_id=?,version=?,epoch=? WHERE singleton=1 AND authority_id=? AND version=? AND epoch=?',(nid,new.version,new.authority_epoch,aid,v,e)).rowcount
            if changed!=1: raise AuthorityRollback('recovery CAS lost')
            q.commit(); return new
        except:
            if q.in_transaction:q.rollback()
            raise
        finally:q.close()
    def issue(self,entry:RegistryEntry,signer_key:bytes):
        entry.validate_shape(); current=self.current(); sid=key_id(signer_key)
        if entry.issuer_id!=sid or entry.issuer_generation!=current.version: raise EntryAuthError('entry issuer not current authority generation')
        if sid not in current.keys or sid in current.revoked or current.keys[sid]!=signer_key.hex(): raise EntryAuthError('signer not active')
        sig=hmac.new(signer_key,canon(entry.unsigned),hashlib.sha256).hexdigest(); return RegistryEntry(**entry.unsigned,signature=sig)
    def _verify_against(self,entry,r):
        entry.validate_shape(); hx=r.keys.get(entry.issuer_id)
        if entry.issuer_generation!=r.version or hx is None: raise EntryAuthError('historical issuer mismatch')
        if entry.issuer_id in r.revoked: raise EntryAuthError('signer revoked in bound authority snapshot')
        exp=hmac.new(bytes.fromhex(hx),canon(entry.unsigned),hashlib.sha256).hexdigest()
        if not hmac.compare_digest(exp,entry.signature): raise EntryAuthError('invalid entry signature')
        return entry
    def verify_for_publication(self,entry):
        current=self.current()
        if entry.issuer_generation!=current.version: raise EntryAuthError('stale signer cannot authorize new publication')
        return self._verify_against(entry,current)
    def accept_entry(self,entry):
        q=self._con()
        try:
            q.execute('BEGIN IMMEDIATE'); aid,v,e=q.execute('SELECT authority_id,version,epoch FROM registry_authority_head WHERE singleton=1').fetchone(); current=self._load_root(q,aid)
            if entry.issuer_generation!=v: raise EntryAuthError('authority rotated before publication')
            self._verify_against(entry,current); d=entry.entry_digest
            raw=json.dumps({**entry.unsigned,'signature':entry.signature},sort_keys=True,separators=(',',':'))
            q.execute('INSERT OR IGNORE INTO registry_authorized_entries VALUES(?,?,?,?)',(d,raw,aid,v))
            row=q.execute('SELECT entry_json,authority_id,authority_version FROM registry_authorized_entries WHERE entry_digest=?',(d,)).fetchone()
            if row!=(raw,aid,v): raise AuthoritySubstitution('entry binding substitution')
            q.commit(); return d
        except:
            if q.in_transaction:q.rollback()
            raise
        finally:q.close()
    def verify_historical_entry(self,entry_digest):
        q=self._con()
        try:
            row=q.execute('SELECT entry_json,authority_id,authority_version FROM registry_authorized_entries WHERE entry_digest=?',(entry_digest,)).fetchone()
            if row is None: raise HistoricalAuthorityMissing('entry')
            x=json.loads(row[0]); e=RegistryEntry(x['sink_id'],x['generation'],x['adapter_digest'],x['endpoint_origin'],x['operation_profile'],x.get('predecessor_entry_digest'),x['issuer_id'],x['issuer_generation'],x['signature'])
            if e.entry_digest!=entry_digest: raise AuthoritySubstitution('entry digest mismatch')
            r=self._load_root(q,row[1])
            if r.version!=row[2]: raise AuthoritySubstitution('entry authority version mismatch')
            return self._verify_against(e,r)
        finally:q.close()
    def verify_durable(self,bootstrap:RootState|None=None,recovery:RecoveryAuthority|None=None):
        q=self._con()
        try:
            meta=q.execute('SELECT bootstrap_id,recovery_id FROM registry_authority_meta WHERE singleton=1').fetchone()
            if meta is None: raise AuthoritySubstitution('missing authority meta')
            if bootstrap is not None and meta[0]!=root_id(bootstrap): raise AuthorityRollback('bootstrap substitution/rollback')
            durable_recovery=self._load_recovery(q,meta[1])
            if recovery is not None and meta[1]!=recovery_id(recovery): raise UnsafeRecovery('recovery authority substitution')
            rows=q.execute('SELECT authority_id,version,epoch,transition_kind,predecessor_id,proof_old,proof_new,proof_recovery FROM registry_authorities ORDER BY version').fetchall()
            if not rows: raise AuthoritySubstitution('missing authority history')
            previous=None
            for aid,v,epoch,kind,pred,po,pn,pr in rows:
                r=self._load_root(q,aid)
                if (r.version,r.authority_epoch)!=(v,epoch): raise AuthoritySubstitution('authority relational mismatch')
                if kind=='bootstrap':
                    if previous is not None or pred is not None or aid!=meta[0]: raise AuthoritySubstitution('invalid bootstrap')
                elif kind=='rotation':
                    if previous is None or pred!=root_id(previous): raise AuthoritySubstitution('rotation predecessor mismatch')
                    p=rotation_payload(previous,r); verify_threshold(previous.keys,previous.threshold,previous.revoked,p,_sig_parse(po)); verify_threshold(r.keys,r.threshold,r.revoked,p,_sig_parse(pn))
                elif kind=='recovery':
                    if previous is None or pred!=root_id(previous): raise AuthoritySubstitution('recovery predecessor mismatch')
                    rec=durable_recovery
                    p=recovery_payload(previous,r,rec.generation); verify_threshold(rec.keys,rec.threshold,rec.revoked,p,_sig_parse(pr))
                else: raise AuthoritySubstitution('unknown transition')
                previous=r
            h=q.execute('SELECT authority_id,version,epoch FROM registry_authority_head WHERE singleton=1').fetchone()
            if previous is None or h!=(root_id(previous),previous.version,previous.authority_epoch): raise AuthoritySubstitution('head/history mismatch')
            for d,raw,aid,v in q.execute('SELECT entry_digest,entry_json,authority_id,authority_version FROM registry_authorized_entries'):
                x=json.loads(raw); e=RegistryEntry(x['sink_id'],x['generation'],x['adapter_digest'],x['endpoint_origin'],x['operation_profile'],x.get('predecessor_entry_digest'),x['issuer_id'],x['issuer_generation'],x['signature'])
                if e.entry_digest!=d: raise AuthoritySubstitution('stored entry digest mismatch')
                r=self._load_root(q,aid)
                if r.version!=v: raise AuthoritySubstitution('stored entry authority mismatch')
                self._verify_against(e,r)
            return True
        finally:q.close()

class UnsafeAmbientAuthority:
    def __init__(self,key): self.key=bytes(key)
    def replace(self,new_key): self.key=bytes(new_key); return True
