from __future__ import annotations
import hashlib, hmac, json, sqlite3
from dataclasses import dataclass

class ReplayError(RuntimeError): pass
class StaleWrite(ReplayError): pass
class AnchorMismatch(ReplayError): pass

@dataclass(frozen=True)
class Record:
    task_id:str; authority_epoch:int; key_generation:int; sequence:int; payload_digest:str; mac:str

def _msg(task_id, authority_epoch, key_generation, sequence, payload_digest):
    return json.dumps({"authority_epoch":int(authority_epoch),"key_generation":int(key_generation),"payload_digest":str(payload_digest),"sequence":int(sequence),"task_id":str(task_id)},sort_keys=True,separators=(",",":")).encode()

def sign_record(secret, task_id, authority_epoch, key_generation, sequence, payload_digest):
    mac=hmac.new(secret,_msg(task_id,authority_epoch,key_generation,sequence,payload_digest),hashlib.sha256).hexdigest()
    return Record(task_id,authority_epoch,key_generation,sequence,payload_digest,mac)

def verify_record(secret, r):
    return hmac.compare_digest(sign_record(secret,r.task_id,r.authority_epoch,r.key_generation,r.sequence,r.payload_digest).mac,r.mac)

class Anchor:
    def __init__(self,value=0): self.value=int(value)
    def advance(self,value):
        value=int(value)
        if value < self.value: raise AnchorMismatch("anchor cannot move backwards")
        self.value=value
    def read(self): return self.value

class WatermarkDB:
    def __init__(self,path): self.path=str(path); self._init()
    def connect(self):
        c=sqlite3.connect(self.path,timeout=5,isolation_level=None)
        c.execute("PRAGMA journal_mode=DELETE"); c.execute("PRAGMA synchronous=FULL")
        return c
    def _init(self):
        c=self.connect(); c.executescript('''
        CREATE TABLE IF NOT EXISTS authority(singleton INTEGER PRIMARY KEY CHECK(singleton=1),authority_epoch INTEGER NOT NULL,key_generation INTEGER NOT NULL,global_sequence INTEGER NOT NULL);
        INSERT OR IGNORE INTO authority VALUES(1,1,1,0);
        CREATE TABLE IF NOT EXISTS task_watermark(task_id TEXT PRIMARY KEY,sequence INTEGER NOT NULL,authority_epoch INTEGER NOT NULL,key_generation INTEGER NOT NULL,payload_digest TEXT NOT NULL,mac TEXT NOT NULL);
        '''); c.close()
    def state(self):
        c=self.connect(); a=c.execute("SELECT authority_epoch,key_generation,global_sequence FROM authority WHERE singleton=1").fetchone(); rows=c.execute("SELECT task_id,sequence,authority_epoch,key_generation,payload_digest,mac FROM task_watermark ORDER BY task_id").fetchall(); c.close()
        return {"authority_epoch":a[0],"key_generation":a[1],"global_sequence":a[2],"tasks":rows}
    def publish(self,secret,task_id,payload_digest,expected_global_sequence=None):
        c=self.connect()
        try:
            c.execute("BEGIN IMMEDIATE")
            epoch,keygen,gseq=c.execute("SELECT authority_epoch,key_generation,global_sequence FROM authority WHERE singleton=1").fetchone()
            if expected_global_sequence is not None and gseq != expected_global_sequence: raise StaleWrite("stale global sequence")
            seq=gseq+1; rec=sign_record(secret,task_id,epoch,keygen,seq,payload_digest)
            cur=c.execute("UPDATE authority SET global_sequence=? WHERE singleton=1 AND global_sequence=?",(seq,gseq))
            if cur.rowcount != 1: raise StaleWrite("lost update")
            cur=c.execute('''INSERT INTO task_watermark VALUES(?,?,?,?,?,?) ON CONFLICT(task_id) DO UPDATE SET sequence=excluded.sequence,authority_epoch=excluded.authority_epoch,key_generation=excluded.key_generation,payload_digest=excluded.payload_digest,mac=excluded.mac WHERE excluded.sequence > task_watermark.sequence''',(task_id,seq,epoch,keygen,payload_digest,rec.mac))
            if cur.rowcount != 1: raise StaleWrite("task watermark did not advance")
            c.execute("COMMIT"); return rec
        except:
            try:c.execute("ROLLBACK")
            except:pass
            raise
        finally:c.close()
    def rotate(self,expected_epoch,new_epoch,new_key_generation):
        c=self.connect()
        try:
            c.execute("BEGIN IMMEDIATE")
            epoch,keygen,gseq=c.execute("SELECT authority_epoch,key_generation,global_sequence FROM authority WHERE singleton=1").fetchone()
            if epoch!=expected_epoch or new_epoch<=epoch or new_key_generation<=keygen: raise StaleWrite("stale/invalid rotation")
            c.execute("UPDATE authority SET authority_epoch=?,key_generation=?,global_sequence=? WHERE singleton=1",(new_epoch,new_key_generation,gseq+1)); c.execute("COMMIT")
        except:
            try:c.execute("ROLLBACK")
            except:pass
            raise
        finally:c.close()
    def verify_fresh(self,secret,r,anchor=None):
        if not verify_record(secret,r): return False
        c=self.connect(); epoch,keygen,gseq=c.execute("SELECT authority_epoch,key_generation,global_sequence FROM authority WHERE singleton=1").fetchone(); row=c.execute("SELECT sequence,authority_epoch,key_generation,payload_digest,mac FROM task_watermark WHERE task_id=?",(r.task_id,)).fetchone(); c.close()
        if anchor is not None:
            av=anchor.read()
            if av > gseq: raise AnchorMismatch("database rollback detected")
            if av < gseq: raise AnchorMismatch("database state is not yet externally anchored")
        if (r.authority_epoch,r.key_generation)!=(epoch,keygen) or row is None: return False
        return row==(r.sequence,r.authority_epoch,r.key_generation,r.payload_digest,r.mac)

class UnsafeSplitStore:
    def __init__(self): self.record=None; self.watermark=0
    def publish_record_only(self,r): self.record=r
