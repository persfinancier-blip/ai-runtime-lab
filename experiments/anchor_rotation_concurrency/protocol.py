from __future__ import annotations
import hashlib, hmac, json, sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

class RotationError(RuntimeError): pass
class ThresholdError(RotationError): pass
class StalePredecessor(RotationError): pass
class WrongProvider(RotationError): pass
class VersionError(RotationError): pass
class EpochError(RotationError): pass
class UnknownOutcome(RotationError): pass
class IntegrityError(RotationError): pass
class ProposalSubstitution(IntegrityError): pass
class EquivocationDetected(RotationError): pass

def canonical(obj: dict) -> bytes: return json.dumps(obj,sort_keys=True,separators=(",",":")).encode()
def digest_obj(obj: dict) -> str: return hashlib.sha256(canonical(obj)).hexdigest()
def key_id(key: bytes) -> str: return hashlib.sha256(key).hexdigest()[:16]
def sign(key: bytes,payload: dict) -> str: return hmac.new(key,canonical(payload),hashlib.sha256).hexdigest()

@dataclass(frozen=True)
class Signature:
    signer_id:str; signature:str

@dataclass(frozen=True)
class RootState:
    provider_id:str; version:int; authority_epoch:int; threshold:int; keys:dict[str,str]; revoked:tuple[str,...]=()
    def descriptor(self): return {"provider_id":self.provider_id,"version":self.version,"authority_epoch":self.authority_epoch,"threshold":self.threshold,"keys":dict(sorted(self.keys.items())),"revoked":sorted(self.revoked)}
    @property
    def digest(self): return digest_obj(self.descriptor())
    def validate(self):
        if type(self.version) is not int or self.version<1: raise IntegrityError("bad version")
        if type(self.authority_epoch) is not int or self.authority_epoch<1: raise IntegrityError("bad epoch")
        active=set(self.keys)-set(self.revoked)
        if type(self.threshold) is not int or self.threshold<1 or self.threshold>len(active): raise IntegrityError("bad threshold")
        for sid,hx in self.keys.items():
            key=bytes.fromhex(hx)
            if sid!=key_id(key): raise IntegrityError("key id mismatch")

@dataclass(frozen=True)
class RecoveryAuthority:
    generation:int; threshold:int; keys:dict[str,str]; revoked:tuple[str,...]=()

@dataclass(frozen=True)
class Proposal:
    proposal_id:str; kind:str; predecessor_digest:str; predecessor_version:int; predecessor_epoch:int; candidate:RootState
    old_signatures:tuple[Signature,...]=(); new_signatures:tuple[Signature,...]=(); recovery_signatures:tuple[Signature,...]=()
    @property
    def payload(self): return {"kind":self.kind,"proposal_id":self.proposal_id,"predecessor_digest":self.predecessor_digest,"predecessor_version":self.predecessor_version,"predecessor_epoch":self.predecessor_epoch,"candidate":self.candidate.descriptor()}
    @property
    def digest(self): return digest_obj(self.payload)

def verify_threshold(keys:dict[str,str],threshold:int,revoked:Iterable[str],payload:dict,signatures:Iterable[Signature])->tuple[str,...]:
    revoked=set(revoked); seen=set(); valid=[]
    for s in signatures:
        if s.signer_id in seen: continue
        seen.add(s.signer_id)
        if s.signer_id in revoked: continue
        hx=keys.get(s.signer_id)
        if hx is None: continue
        if hmac.compare_digest(sign(bytes.fromhex(hx),payload),s.signature): valid.append(s.signer_id)
    if len(valid)<threshold: raise ThresholdError(f"valid={len(valid)} threshold={threshold}")
    return tuple(sorted(valid))

class SerializedRootStore:
    def __init__(self,path:str|Path,initial:RootState,recovery:RecoveryAuthority):
        self.path=str(path); self.recovery=recovery; initial.validate(); c=self.connect()
        try:
            c.executescript('''PRAGMA journal_mode=WAL;
            CREATE TABLE IF NOT EXISTS active_root(singleton INTEGER PRIMARY KEY CHECK(singleton=1),provider_id TEXT NOT NULL,version INTEGER NOT NULL,authority_epoch INTEGER NOT NULL,root_digest TEXT NOT NULL,root_json TEXT NOT NULL,activation_seq INTEGER NOT NULL);
            CREATE TABLE IF NOT EXISTS activations(seq INTEGER PRIMARY KEY AUTOINCREMENT,proposal_id TEXT NOT NULL UNIQUE,proposal_digest TEXT NOT NULL UNIQUE,predecessor_digest TEXT NOT NULL,candidate_digest TEXT NOT NULL,kind TEXT NOT NULL,receipt TEXT NOT NULL UNIQUE,chain_hash TEXT NOT NULL);
            CREATE UNIQUE INDEX IF NOT EXISTS one_successor_per_parent ON activations(predecessor_digest);''')
            if c.execute('SELECT 1 FROM active_root WHERE singleton=1').fetchone() is None:
                c.execute('INSERT INTO active_root VALUES(1,?,?,?,?,?,0)',(initial.provider_id,initial.version,initial.authority_epoch,initial.digest,json.dumps(initial.descriptor(),sort_keys=True)))
            c.commit()
        finally:c.close()
    def connect(self):
        c=sqlite3.connect(self.path,timeout=5.0,isolation_level=None,check_same_thread=False); c.row_factory=sqlite3.Row; return c
    @staticmethod
    def row_to_root(r):
        x=json.loads(r['root_json']); return RootState(x['provider_id'],x['version'],x['authority_epoch'],x['threshold'],dict(x['keys']),tuple(x.get('revoked',())))
    def current(self):
        c=self.connect()
        try:return self.row_to_root(c.execute('SELECT * FROM active_root WHERE singleton=1').fetchone())
        finally:c.close()
    def get_activation(self,pid):
        c=self.connect()
        try:
            r=c.execute('SELECT * FROM activations WHERE proposal_id=?',(pid,)).fetchone(); return dict(r) if r else None
        finally:c.close()
    def get_receipt(self,pid):
        r=self.get_activation(pid); return r['receipt'] if r else None
    @staticmethod
    def _reconcile_existing(r,p):
        if r is None:return None
        if r['proposal_digest']!=p.digest or r['candidate_digest']!=p.candidate.digest or r['predecessor_digest']!=p.predecessor_digest: raise ProposalSubstitution('proposal_id reused with different transition identity')
        return r['receipt']
    def activation_rows(self):
        c=self.connect()
        try:return [dict(r) for r in c.execute('SELECT * FROM activations ORDER BY seq')]
        finally:c.close()
    def _validate(self,current,p):
        p.candidate.validate()
        if current.provider_id!=p.candidate.provider_id: raise WrongProvider()
        if p.predecessor_digest!=current.digest or p.predecessor_version!=current.version or p.predecessor_epoch!=current.authority_epoch: raise StalePredecessor()
        if p.candidate.version!=current.version+1: raise VersionError()
        if p.kind=='rotation':
            if p.candidate.authority_epoch!=current.authority_epoch: raise EpochError()
            verify_threshold(current.keys,current.threshold,current.revoked,p.payload,p.old_signatures); verify_threshold(p.candidate.keys,p.candidate.threshold,p.candidate.revoked,p.payload,p.new_signatures); return
        if p.kind=='recovery':
            if p.candidate.authority_epoch!=current.authority_epoch+1: raise EpochError()
            verify_threshold(self.recovery.keys,self.recovery.threshold,self.recovery.revoked,p.payload,p.recovery_signatures); return
        raise RotationError('unknown proposal kind')
    def activate(self,p,crash_before_commit=False,timeout_after_commit=False):
        existing=self._reconcile_existing(self.get_activation(p.proposal_id),p)
        if existing:return existing
        c=self.connect()
        try:
            c.execute('BEGIN IMMEDIATE')
            er=c.execute('SELECT * FROM activations WHERE proposal_id=?',(p.proposal_id,)).fetchone()
            if er:
                receipt=self._reconcile_existing(dict(er),p); c.commit(); return receipt
            current=self.row_to_root(c.execute('SELECT * FROM active_root WHERE singleton=1').fetchone()); self._validate(current,p)
            if crash_before_commit: raise RuntimeError('injected crash before commit')
            prev=c.execute('SELECT chain_hash FROM activations ORDER BY seq DESC LIMIT 1').fetchone(); prev_hash=prev['chain_hash'] if prev else '0'*64
            receipt=f'activation:{p.digest}'; chain_hash=hashlib.sha256((prev_hash+p.digest+receipt).encode()).hexdigest()
            c.execute('INSERT INTO activations(proposal_id,proposal_digest,predecessor_digest,candidate_digest,kind,receipt,chain_hash) VALUES(?,?,?,?,?,?,?)',(p.proposal_id,p.digest,p.predecessor_digest,p.candidate.digest,p.kind,receipt,chain_hash))
            seq=c.execute('SELECT seq FROM activations WHERE proposal_id=?',(p.proposal_id,)).fetchone()['seq']
            changed=c.execute('UPDATE active_root SET provider_id=?,version=?,authority_epoch=?,root_digest=?,root_json=?,activation_seq=? WHERE singleton=1 AND root_digest=? AND version=? AND authority_epoch=?',(p.candidate.provider_id,p.candidate.version,p.candidate.authority_epoch,p.candidate.digest,json.dumps(p.candidate.descriptor(),sort_keys=True),seq,p.predecessor_digest,p.predecessor_version,p.predecessor_epoch)).rowcount
            if changed!=1: raise StalePredecessor()
            c.commit()
            if timeout_after_commit: raise UnknownOutcome('commit succeeded but receipt was not observed')
            return receipt
        except sqlite3.IntegrityError as e:
            if c.in_transaction:c.rollback()
            existing=self._reconcile_existing(self.get_activation(p.proposal_id),p)
            if existing:return existing
            raise StalePredecessor(str(e))
        except Exception:
            if c.in_transaction:c.rollback()
            raise
        finally:c.close()

class UnsafeCheckThenWriteStore:
    def __init__(self,initial):self.current=initial;self.accepted=[]
    def check(self,p):return p.predecessor_digest==self.current.digest and p.predecessor_version==self.current.version
    def write_without_recheck(self,p):self.current=p.candidate;self.accepted.append(p.proposal_id)

class TransparencyObserver:
    def __init__(self):self.by_parent={}
    def observe(self,a):
        parent=a['predecessor_digest']; value=(a['candidate_digest'],a['proposal_digest']); prior=self.by_parent.get(parent)
        if prior and prior!=value: raise EquivocationDetected(f'parent {parent} has conflicting successors')
        self.by_parent[parent]=value
