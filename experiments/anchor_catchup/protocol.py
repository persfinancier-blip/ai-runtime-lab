from __future__ import annotations
import hashlib,hmac,json,sqlite3
from dataclasses import dataclass
from pathlib import Path
class CatchupError(RuntimeError): pass
class StaleWrite(CatchupError): pass
class AnchorUnavailable(CatchupError): pass
class AnchorUnknownOutcome(CatchupError): pass
class AnchorConflict(CatchupError): pass
class AnchorMismatch(CatchupError): pass
class ProofError(CatchupError): pass
class PendingAnchor(CatchupError): pass
@dataclass(frozen=True)
class AnchorIntent:
    sequence:int; authority_epoch:int; key_generation:int; task_id:str; payload_digest:str; proof_mac:str; status:str
@dataclass(frozen=True)
class CatchupEvidence:
    sequence:int; anchor_position:int; proof_ref:str; outcome:str
def _msg(sequence,authority_epoch,key_generation,task_id,payload_digest):
    return json.dumps({'authority_epoch':int(authority_epoch),'key_generation':int(key_generation),'payload_digest':str(payload_digest),'sequence':int(sequence),'task_id':str(task_id)},sort_keys=True,separators=(',',':')).encode()
def sign_proof(secret,**kw): return hmac.new(secret,_msg(**kw),hashlib.sha256).hexdigest()
def proof_ref(i):
    raw=json.dumps({'authority_epoch':i.authority_epoch,'key_generation':i.key_generation,'payload_digest':i.payload_digest,'proof_mac':i.proof_mac,'sequence':i.sequence,'task_id':i.task_id},sort_keys=True,separators=(',',':')).encode()
    return hashlib.sha256(raw).hexdigest()
class MonotonicAnchor:
    def __init__(self,value=0): self.value=int(value); self.available=True; self.increment_calls=0
    def read(self):
        if not self.available: raise AnchorUnavailable('anchor unavailable')
        return self.value
    def increment(self,*,expected,timeout_after_commit=False):
        if not self.available: raise AnchorUnavailable('anchor unavailable')
        self.increment_calls+=1
        if self.value!=int(expected): raise AnchorConflict(f'expected={expected} current={self.value}')
        self.value+=1
        if timeout_after_commit: raise AnchorUnknownOutcome('increment committed; response lost')
        return self.value
class CatchupDB:
    def __init__(self,path): self.path=str(path); self._init()
    def connect(self):
        c=sqlite3.connect(self.path,timeout=5,isolation_level=None); c.execute('PRAGMA journal_mode=DELETE'); c.execute('PRAGMA synchronous=FULL'); return c
    def _init(self):
        c=self.connect(); c.executescript("""CREATE TABLE IF NOT EXISTS authority(singleton INTEGER PRIMARY KEY CHECK(singleton=1),authority_epoch INTEGER NOT NULL,key_generation INTEGER NOT NULL,global_sequence INTEGER NOT NULL); INSERT OR IGNORE INTO authority VALUES(1,1,1,0); CREATE TABLE IF NOT EXISTS anchor_intent(sequence INTEGER PRIMARY KEY,authority_epoch INTEGER NOT NULL,key_generation INTEGER NOT NULL,task_id TEXT NOT NULL,payload_digest TEXT NOT NULL,proof_mac TEXT NOT NULL,status TEXT NOT NULL CHECK(status IN ('PENDING','CONFIRMED')));"""); c.close()
    def authority(self):
        c=self.connect(); r=c.execute('SELECT authority_epoch,key_generation,global_sequence FROM authority WHERE singleton=1').fetchone(); c.close(); return tuple(r)
    def intent(self,sequence):
        c=self.connect(); r=c.execute('SELECT sequence,authority_epoch,key_generation,task_id,payload_digest,proof_mac,status FROM anchor_intent WHERE sequence=?',(int(sequence),)).fetchone(); c.close(); return AnchorIntent(*r) if r else None
    def publish(self,secret,*,task_id,payload_digest,expected_global_sequence=None):
        c=self.connect()
        try:
            c.execute('BEGIN IMMEDIATE')
            p=c.execute("SELECT sequence FROM anchor_intent WHERE status='PENDING' LIMIT 1").fetchone()
            if p: raise PendingAnchor(f'sequence {p[0]} pending')
            epoch,keygen,gseq=c.execute('SELECT authority_epoch,key_generation,global_sequence FROM authority WHERE singleton=1').fetchone()
            if expected_global_sequence is not None and gseq!=expected_global_sequence: raise StaleWrite('stale global sequence')
            seq=gseq+1; mac=sign_proof(secret,sequence=seq,authority_epoch=epoch,key_generation=keygen,task_id=task_id,payload_digest=payload_digest)
            c.execute('UPDATE authority SET global_sequence=? WHERE singleton=1 AND global_sequence=?',(seq,gseq))
            c.execute("INSERT INTO anchor_intent VALUES(?,?,?,?,?,?,'PENDING')",(seq,epoch,keygen,task_id,payload_digest,mac)); c.execute('COMMIT')
            return AnchorIntent(seq,epoch,keygen,task_id,payload_digest,mac,'PENDING')
        except:
            try:c.execute('ROLLBACK')
            except:pass
            raise
        finally:c.close()
    def confirm(self,sequence,*,expected_epoch,expected_key_generation):
        c=self.connect()
        try:
            c.execute('BEGIN IMMEDIATE'); epoch,keygen,gseq=c.execute('SELECT authority_epoch,key_generation,global_sequence FROM authority WHERE singleton=1').fetchone()
            if (epoch,keygen)!=(expected_epoch,expected_key_generation): raise StaleWrite('authority/key rotated during catch-up')
            if gseq!=int(sequence): raise StaleWrite('sequence no longer current')
            cur=c.execute("UPDATE anchor_intent SET status='CONFIRMED' WHERE sequence=? AND authority_epoch=? AND key_generation=? AND status IN ('PENDING','CONFIRMED')",(int(sequence),expected_epoch,expected_key_generation))
            if cur.rowcount!=1: raise ProofError('missing current intent')
            c.execute('COMMIT')
        except:
            try:c.execute('ROLLBACK')
            except:pass
            raise
        finally:c.close()
    def rotate(self,new_secret,*,expected_epoch,new_epoch,new_key_generation):
        c=self.connect()
        try:
            c.execute('BEGIN IMMEDIATE'); p=c.execute("SELECT sequence FROM anchor_intent WHERE status='PENDING' LIMIT 1").fetchone()
            if p: raise PendingAnchor('cannot rotate while anchor pending')
            epoch,keygen,gseq=c.execute('SELECT authority_epoch,key_generation,global_sequence FROM authority WHERE singleton=1').fetchone()
            if epoch!=expected_epoch or new_epoch<=epoch or new_key_generation<=keygen: raise StaleWrite('stale/invalid rotation')
            seq=gseq+1; task_id='__authority_rotation__'; digest=hashlib.sha256(f'{epoch}:{keygen}->{new_epoch}:{new_key_generation}'.encode()).hexdigest()
            mac=sign_proof(new_secret,sequence=seq,authority_epoch=new_epoch,key_generation=new_key_generation,task_id=task_id,payload_digest=digest)
            c.execute('UPDATE authority SET authority_epoch=?,key_generation=?,global_sequence=? WHERE singleton=1',(new_epoch,new_key_generation,seq))
            c.execute("INSERT INTO anchor_intent VALUES(?,?,?,?,?,?,'PENDING')",(seq,new_epoch,new_key_generation,task_id,digest,mac)); c.execute('COMMIT')
            return AnchorIntent(seq,new_epoch,new_key_generation,task_id,digest,mac,'PENDING')
        except:
            try:c.execute('ROLLBACK')
            except:pass
            raise
        finally:c.close()
class CatchupProtocol:
    def __init__(self,db,anchor,keyring): self.db=db; self.anchor=anchor; self.keyring=dict(keyring)
    def _verify_current_intent(self):
        epoch,keygen,gseq=self.db.authority(); i=self.db.intent(gseq)
        if i is None: raise ProofError('database sequence lacks durable anchor intent')
        if (i.authority_epoch,i.key_generation)!=(epoch,keygen): raise ProofError('stale authority/key intent')
        secret=self.keyring.get((epoch,keygen))
        if secret is None: raise ProofError('current proof key unavailable')
        expected=sign_proof(secret,sequence=i.sequence,authority_epoch=i.authority_epoch,key_generation=i.key_generation,task_id=i.task_id,payload_digest=i.payload_digest)
        if not hmac.compare_digest(expected,i.proof_mac): raise ProofError('intent authentication failed')
        return i
    def reconcile(self,*,timeout_after_commit=False):
        i=self._verify_current_intent(); _,_,gseq=self.db.authority(); observed=self.anchor.read()
        if observed>gseq: raise AnchorMismatch('anchor ahead of DB: rollback detected')
        if observed==gseq:
            self.db.confirm(gseq,expected_epoch=i.authority_epoch,expected_key_generation=i.key_generation); return CatchupEvidence(gseq,observed,proof_ref(i),'ALREADY_ALIGNED')
        if observed!=gseq-1: raise AnchorMismatch(f'unsafe gap anchor={observed} db={gseq}')
        try:new=self.anchor.increment(expected=observed,timeout_after_commit=timeout_after_commit)
        except AnchorUnknownOutcome: raise
        except AnchorConflict:new=self.anchor.read()
        if new!=gseq: raise AnchorMismatch(f'unexpected anchor {new} != {gseq}')
        epoch2,keygen2,gseq2=self.db.authority()
        if (epoch2,keygen2,gseq2)!=(i.authority_epoch,i.key_generation,i.sequence): raise StaleWrite('DB changed during catch-up')
        self.db.confirm(gseq,expected_epoch=i.authority_epoch,expected_key_generation=i.key_generation); return CatchupEvidence(gseq,new,proof_ref(i),'ADVANCED')
    def consequential_continuation_allowed(self):
        epoch,keygen,gseq=self.db.authority(); i=self.db.intent(gseq)
        if i is None or i.status!='CONFIRMED': return False
        if (i.authority_epoch,i.key_generation)!=(epoch,keygen): return False
        try:return self.anchor.read()==gseq
        except AnchorUnavailable:return False
class UnsafeBlindRetry:
    def __init__(self,anchor): self.anchor=anchor
    def run(self):
        try:self.anchor.increment(expected=self.anchor.read(),timeout_after_commit=True)
        except AnchorUnknownOutcome:
            current=self.anchor.read(); self.anchor.increment(expected=current)
