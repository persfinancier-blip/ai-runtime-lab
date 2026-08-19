from __future__ import annotations
import hashlib, json, sqlite3
from dataclasses import dataclass
from pathlib import Path

class RotationError(RuntimeError): pass
class StaleProposal(RotationError): pass
class SameVersionSubstitution(RotationError): pass
class UnknownCommitOutcome(RotationError): pass
class InvalidTransition(RotationError): pass

def canonical(obj): return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()
def digest_obj(obj): return hashlib.sha256(canonical(obj)).hexdigest()

@dataclass(frozen=True)
class Root:
    provider_id:str; version:int; authority_epoch:int; threshold:int; key_ids:tuple[str,...]
    def descriptor(self): return {"provider_id":self.provider_id,"version":self.version,"authority_epoch":self.authority_epoch,"threshold":self.threshold,"key_ids":list(self.key_ids)}
    @property
    def digest(self): return digest_obj(self.descriptor())

@dataclass(frozen=True)
class Proposal:
    proposal_id:str; kind:str; predecessor_digest:str; predecessor_version:int; predecessor_epoch:int; candidate:Root; signer_ids:tuple[str,...]
    @property
    def digest(self):
        return digest_obj({"proposal_id":self.proposal_id,"kind":self.kind,"predecessor_digest":self.predecessor_digest,"predecessor_version":self.predecessor_version,"predecessor_epoch":self.predecessor_epoch,"candidate":self.candidate.descriptor(),"signer_ids":list(self.signer_ids)})

@dataclass(frozen=True)
class ActivationReceipt:
    proposal_id:str; proposal_digest:str; root_digest:str; transition_seq:int; provider_id:str; version:int; authority_epoch:int; signer_ids:tuple[str,...]

class RotationDB:
    def __init__(self,path,initial=None):
        self.path=str(path)
        if initial is not None:self._init(initial)
    def connect(self):
        c=sqlite3.connect(self.path,timeout=5.0,isolation_level=None,check_same_thread=False)
        c.execute('PRAGMA journal_mode=WAL'); c.execute('PRAGMA synchronous=FULL'); return c
    def _init(self,initial):
        c=self.connect()
        try:
            c.executescript('''CREATE TABLE IF NOT EXISTS active_root(singleton INTEGER PRIMARY KEY CHECK(singleton=1),provider_id TEXT NOT NULL,version INTEGER NOT NULL,authority_epoch INTEGER NOT NULL,root_digest TEXT NOT NULL,root_json TEXT NOT NULL,transition_seq INTEGER NOT NULL);CREATE TABLE IF NOT EXISTS transitions(transition_seq INTEGER PRIMARY KEY,proposal_id TEXT NOT NULL UNIQUE,proposal_digest TEXT NOT NULL UNIQUE,predecessor_digest TEXT NOT NULL,root_digest TEXT NOT NULL,root_json TEXT NOT NULL,kind TEXT NOT NULL,signer_ids_json TEXT NOT NULL,committed INTEGER NOT NULL CHECK(committed=1));CREATE UNIQUE INDEX IF NOT EXISTS one_successor_per_predecessor ON transitions(predecessor_digest);CREATE TABLE IF NOT EXISTS proposal_observations(proposal_digest TEXT PRIMARY KEY,proposal_id TEXT NOT NULL,predecessor_digest TEXT NOT NULL,kind TEXT NOT NULL,signer_ids_json TEXT NOT NULL);''')
            if c.execute('SELECT 1 FROM active_root WHERE singleton=1').fetchone() is None:
                c.execute('INSERT INTO active_root VALUES(1,?,?,?,?,?,0)',(initial.provider_id,initial.version,initial.authority_epoch,initial.digest,json.dumps(initial.descriptor(),sort_keys=True)))
        finally:c.close()
    def active(self):
        c=self.connect()
        try:
            r=c.execute('SELECT root_json,transition_seq FROM active_root WHERE singleton=1').fetchone(); raw=json.loads(r[0]); return Root(raw['provider_id'],raw['version'],raw['authority_epoch'],raw['threshold'],tuple(raw['key_ids'])),int(r[1])
        finally:c.close()
    def receipt(self,pid):
        c=self.connect()
        try:
            row=c.execute('SELECT proposal_digest,root_digest,transition_seq,root_json,signer_ids_json FROM transitions WHERE proposal_id=?',(pid,)).fetchone()
            if row is None:return None
            raw=json.loads(row[3]); return ActivationReceipt(pid,row[0],row[1],int(row[2]),raw['provider_id'],raw['version'],raw['authority_epoch'],tuple(json.loads(row[4])))
        finally:c.close()
    def observe(self,p):
        c=self.connect()
        try:
            c.execute('BEGIN IMMEDIATE')
            row=c.execute('SELECT proposal_id FROM proposal_observations WHERE proposal_digest=?',(p.digest,)).fetchone()
            if row is None:
                c.execute('INSERT INTO proposal_observations VALUES(?,?,?,?,?)',(p.digest,p.proposal_id,p.predecessor_digest,p.kind,json.dumps(sorted(set(p.signer_ids)))))
            c.execute('COMMIT')
        finally:c.close()
    def equivocation_candidates(self,predecessor_digest):
        c=self.connect()
        try:
            rows=c.execute('SELECT proposal_digest,proposal_id,kind,signer_ids_json FROM proposal_observations WHERE predecessor_digest=? ORDER BY proposal_digest',(predecessor_digest,)).fetchall(); out=[]
            for i,a in enumerate(rows):
                sa=set(json.loads(a[3]))
                for b in rows[i+1:]:
                    overlap=tuple(sorted(sa & set(json.loads(b[3])))); out.append({'proposal_a':a[0],'proposal_b':b[0],'proposal_id_a':a[1],'proposal_id_b':b[1],'overlapping_signers':overlap})
            return out
        finally:c.close()
    def transition_count(self):
        c=self.connect()
        try:return int(c.execute('SELECT COUNT(*) FROM transitions').fetchone()[0])
        finally:c.close()
    @staticmethod
    def validate_against(old,p):
        if p.predecessor_digest!=old.digest or p.predecessor_version!=old.version or p.predecessor_epoch!=old.authority_epoch: raise StaleProposal('predecessor changed')
        if p.candidate.provider_id!=old.provider_id: raise InvalidTransition('provider changed')
        if p.candidate.version!=old.version+1:
            if p.candidate.version==old.version and p.candidate.digest!=old.digest: raise SameVersionSubstitution('same-version substitution')
            raise InvalidTransition('version')
        if p.kind=='rotation':
            if p.candidate.authority_epoch!=old.authority_epoch: raise InvalidTransition('rotation epoch')
        elif p.kind=='recovery':
            if p.candidate.authority_epoch!=old.authority_epoch+1: raise InvalidTransition('recovery epoch')
        else: raise InvalidTransition('kind')
        if not p.signer_ids: raise InvalidTransition('signers')
    def activate(self,p,crash_before_commit=False,timeout_after_commit=False):
        self.observe(p)
        existing=self.receipt(p.proposal_id)
        if existing:
            if existing.proposal_digest!=p.digest: raise SameVersionSubstitution('proposal id content changed')
            return existing
        c=self.connect(); committed=False
        try:
            c.execute('BEGIN IMMEDIATE')
            row=c.execute('SELECT proposal_digest FROM transitions WHERE proposal_id=?',(p.proposal_id,)).fetchone()
            if row:
                c.execute('ROLLBACK'); return self.receipt(p.proposal_id)
            ar=c.execute('SELECT root_json,root_digest,transition_seq FROM active_root WHERE singleton=1').fetchone(); raw=json.loads(ar[0]); old=Root(raw['provider_id'],raw['version'],raw['authority_epoch'],raw['threshold'],tuple(raw['key_ids']))
            self.validate_against(old,p); next_seq=int(ar[2])+1
            if crash_before_commit:
                c.execute('ROLLBACK'); raise RuntimeError('injected crash')
            root_json=json.dumps(p.candidate.descriptor(),sort_keys=True); signer_json=json.dumps(sorted(set(p.signer_ids)))
            c.execute('INSERT INTO transitions VALUES(?,?,?,?,?,?,?,?,1)',(next_seq,p.proposal_id,p.digest,p.predecessor_digest,p.candidate.digest,root_json,p.kind,signer_json))
            changed=c.execute('UPDATE active_root SET provider_id=?,version=?,authority_epoch=?,root_digest=?,root_json=?,transition_seq=? WHERE singleton=1 AND root_digest=? AND transition_seq=?',(p.candidate.provider_id,p.candidate.version,p.candidate.authority_epoch,p.candidate.digest,root_json,next_seq,p.predecessor_digest,int(ar[2]))).rowcount
            if changed!=1:
                c.execute('ROLLBACK'); raise StaleProposal('CAS lost')
            c.execute('COMMIT'); committed=True
        finally:c.close()
        if timeout_after_commit and committed: raise UnknownCommitOutcome(p.proposal_id)
        return self.receipt(p.proposal_id)

class UnsafeCheckThenWrite:
    def __init__(self,initial): self.active=initial; self.activations=[]
    def validate(self,p): RotationDB.validate_against(self.active,p)
    def write(self,p): self.active=p.candidate; self.activations.append(p.proposal_id)
