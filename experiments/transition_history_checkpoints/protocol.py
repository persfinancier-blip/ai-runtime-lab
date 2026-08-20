from __future__ import annotations

import hashlib, hmac, json, sqlite3
from dataclasses import asdict, dataclass
from typing import Any

from experiments.transition_history_integrity.protocol import (
    HistoryStore, IntegrityError as HistoryIntegrityError, digest,
    recovery_payload, rotation_payload, verify_threshold,
)

SCHEMA = 1
PROTOCOL = "lab059-history-v1"

class CheckpointError(RuntimeError): pass
class CheckpointAuthenticationError(CheckpointError): pass
class CheckpointRollbackError(CheckpointError): pass
class CheckpointSubstitutionError(CheckpointError): pass
class CheckpointHeadMismatch(CheckpointError): pass
class SuffixIntegrityError(CheckpointError): pass

def canon(x): return json.dumps(x, sort_keys=True, separators=(",", ":")).encode()
def hx(data): return hashlib.sha256(data).hexdigest()
def mac(key, obj): return hmac.new(key, canon(obj), hashlib.sha256).hexdigest()
def strict_int(x, name, minimum=0):
    if type(x) is not int or x < minimum: raise CheckpointAuthenticationError(f"invalid {name}")
def strict_hex(x, name, n):
    if type(x) is not str or len(x) != n: raise CheckpointAuthenticationError(f"invalid {name}")
    try: bytes.fromhex(x)
    except ValueError as e: raise CheckpointAuthenticationError(f"invalid {name}") from e

@dataclass(frozen=True)
class HistoryCheckpoint:
    schema_version:int; protocol_version:str; history_id:str; sequence:int
    root_id:str; recovery_id:str; prefix_commitment:str; external_anchor_id:str
    signer_id:str; signature:str
    @property
    def unsigned(self):
        d=asdict(self); d.pop("signature"); return d
    @property
    def checkpoint_id(self): return hx(canon(asdict(self)))
    @classmethod
    def parse(cls, raw):
        x=json.loads(raw) if isinstance(raw,str) else dict(raw)
        required=set(cls.__dataclass_fields__)
        if set(x)!=required: raise CheckpointAuthenticationError("checkpoint fields")
        strict_int(x["schema_version"],"schema_version",1); strict_int(x["sequence"],"sequence")
        for k in ("protocol_version","external_anchor_id"):
            if type(x[k]) is not str or not x[k]: raise CheckpointAuthenticationError(f"invalid {k}")
        for k,n in (("history_id",64),("root_id",64),("recovery_id",64),("prefix_commitment",64),("signer_id",16),("signature",64)):
            strict_hex(x[k],k,n)
        return cls(**x)
    from_json = parse

class CheckpointedHistory:
    """Authenticated prefix checkpoint over LAB-059; whole-store freshness stays external."""
    def __init__(self, store:HistoryStore, *, checkpoint_key:bytes, external_anchor_id:str):
        if not checkpoint_key or not external_anchor_id: raise ValueError("checkpoint identity")
        self.store=store; self.key=checkpoint_key; self.anchor=external_anchor_id
        self.signer_id=hashlib.sha256(checkpoint_key).hexdigest()[:16]
        q=store._con()
        try:
            q.executescript("""
              CREATE TABLE IF NOT EXISTS history_checkpoints(checkpoint_id TEXT PRIMARY KEY,sequence INTEGER NOT NULL UNIQUE,body_json TEXT NOT NULL);
              CREATE TABLE IF NOT EXISTS checkpoint_watermark(singleton INTEGER PRIMARY KEY CHECK(singleton=1),sequence INTEGER NOT NULL,checkpoint_id TEXT NOT NULL);
            """)
        finally: q.close()
    def bootstrap(self,q):
        r=q.execute("SELECT root_id,recovery_id FROM bootstrap WHERE singleton=1").fetchone()
        if not r: raise CheckpointSubstitutionError("missing bootstrap")
        return r
    def history_id(self,q):
        r,c=self.bootstrap(q)
        return digest({"kind":"lab060-history","bootstrap_root_id":r,"bootstrap_recovery_id":c,"protocol_version":PROTOCOL,"external_anchor_id":self.anchor})
    def prefix_commitment(self,q,sequence):
        r,c=self.bootstrap(q)
        running=hashlib.sha256(canon({"kind":"lab060-prefix-v1","bootstrap_root_id":r,"bootstrap_recovery_id":c,"protocol_version":PROTOCOL})).digest()
        rows=q.execute("SELECT sequence,proposal_id,transition_digest,kind,predecessor_root_id,predecessor_recovery_id,successor_root_id,successor_recovery_id,proof_json FROM transitions WHERE sequence<=? ORDER BY sequence",(sequence,)).fetchall()
        if len(rows)!=sequence: raise HistoryIntegrityError("checkpoint prefix sequence gap")
        names=("sequence","proposal_id","transition_digest","kind","predecessor_root_id","predecessor_recovery_id","successor_root_id","successor_recovery_id","proof_json")
        for expected,row in enumerate(rows,1):
            if row[0]!=expected: raise HistoryIntegrityError("checkpoint prefix sequence mismatch")
            running=hashlib.sha256(running+canon(dict(zip(names,row)))).digest()
        return running.hex()
    def encode(self,cp): return json.dumps(asdict(cp),sort_keys=True,separators=(",",":"))
    def create_checkpoint(self):
        q=self.store._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            v=self.store.verify_history(); head=q.execute("SELECT root_id,recovery_id,sequence FROM head WHERE singleton=1").fetchone()
            if head!=(v["root_id"],v["recovery_id"],v["sequence"]): raise CheckpointHeadMismatch("head moved")
            unsigned={"schema_version":SCHEMA,"protocol_version":PROTOCOL,"history_id":self.history_id(q),"sequence":v["sequence"],"root_id":v["root_id"],"recovery_id":v["recovery_id"],"prefix_commitment":self.prefix_commitment(q,v["sequence"]),"external_anchor_id":self.anchor,"signer_id":self.signer_id}
            cp=HistoryCheckpoint(**unsigned,signature=mac(self.key,unsigned))
            wm=q.execute("SELECT sequence,checkpoint_id FROM checkpoint_watermark WHERE singleton=1").fetchone()
            if wm and cp.sequence<wm[0]: raise CheckpointRollbackError("behind watermark")
            if wm and cp.sequence==wm[0]:
                raw=q.execute("SELECT body_json FROM history_checkpoints WHERE checkpoint_id=?",(wm[1],)).fetchone()
                if not raw: raise CheckpointAuthenticationError("missing watermark checkpoint")
                old=HistoryCheckpoint.parse(raw[0])
                if old.checkpoint_id!=cp.checkpoint_id: raise CheckpointSubstitutionError("same-sequence substitution")
                q.commit(); return old
            q.execute("INSERT OR IGNORE INTO history_checkpoints VALUES(?,?,?)",(cp.checkpoint_id,cp.sequence,self.encode(cp)))
            row=q.execute("SELECT checkpoint_id,body_json FROM history_checkpoints WHERE sequence=?",(cp.sequence,)).fetchone()
            if not row or row[0]!=cp.checkpoint_id or HistoryCheckpoint.parse(row[1])!=cp: raise CheckpointSubstitutionError("checkpoint persistence")
            q.execute("INSERT INTO checkpoint_watermark VALUES(1,?,?) ON CONFLICT(singleton) DO UPDATE SET sequence=excluded.sequence,checkpoint_id=excluded.checkpoint_id",(cp.sequence,cp.checkpoint_id))
            q.commit(); return cp
        except:
            if q.in_transaction:q.rollback()
            raise
        finally:q.close()
    def verify_cp(self,q,cp):
        cp=HistoryCheckpoint.parse(asdict(cp))
        if cp.schema_version!=SCHEMA or cp.protocol_version!=PROTOCOL: raise CheckpointAuthenticationError("version")
        if cp.external_anchor_id!=self.anchor or cp.history_id!=self.history_id(q): raise CheckpointSubstitutionError("history/anchor")
        if cp.signer_id!=self.signer_id or not hmac.compare_digest(mac(self.key,cp.unsigned),cp.signature): raise CheckpointAuthenticationError("signature")
        wm=q.execute("SELECT sequence,checkpoint_id FROM checkpoint_watermark WHERE singleton=1").fetchone()
        if not wm: raise CheckpointAuthenticationError("missing watermark")
        if cp.sequence<wm[0]: raise CheckpointRollbackError("stale checkpoint")
        if (cp.sequence,cp.checkpoint_id)!=wm: raise CheckpointSubstitutionError("watermark mismatch")
        row=q.execute("SELECT body_json FROM history_checkpoints WHERE checkpoint_id=?",(cp.checkpoint_id,)).fetchone()
        if not row or HistoryCheckpoint.parse(row[0])!=cp: raise CheckpointSubstitutionError("checkpoint row")
        head=q.execute("SELECT root_id,recovery_id,sequence FROM head WHERE singleton=1").fetchone()
        if not head or cp.sequence>head[2]: raise CheckpointHeadMismatch("checkpoint beyond head")
        self.store._get(q,cp.root_id); self.store._get(q,cp.recovery_id)
        return cp
    def verify_checkpoint(self,cp):
        q=self.store._con()
        try:q.execute("BEGIN"); self.verify_cp(q,cp); q.commit()
        except:
            if q.in_transaction:q.rollback()
            raise
        finally:q.close()
    def audit_checkpoint_prefix(self,cp):
        q=self.store._con()
        try:
            q.execute("BEGIN"); cp=self.verify_cp(q,cp); actual=self.prefix_commitment(q,cp.sequence)
            if not hmac.compare_digest(actual,cp.prefix_commitment): raise CheckpointSubstitutionError("archived prefix commitment mismatch")
            q.commit(); return {"sequence":cp.sequence,"prefix_commitment":actual}
        except:
            if q.in_transaction:q.rollback()
            raise
        finally:q.close()
    def verify_suffix(self,cp):
        q=self.store._con()
        try:
            q.execute("BEGIN"); cp=self.verify_cp(q,cp); root=self.store._get(q,cp.root_id); rec=self.store._get(q,cp.recovery_id)
            rows=q.execute("SELECT sequence,proposal_id,transition_digest,kind,predecessor_root_id,predecessor_recovery_id,successor_root_id,successor_recovery_id,proof_json FROM transitions WHERE sequence>? ORDER BY sequence",(cp.sequence,)).fetchall()
            expected=cp.sequence+1; count=0
            for seq,pid,td,kind,r0,c0,r1,c1,pj in rows:
                if seq!=expected: raise SuffixIntegrityError("suffix sequence gap")
                if (r0,c0)!=(root.authority_id,rec.authority_id): raise SuffixIntegrityError("suffix predecessor")
                proof=json.loads(pj)
                if (proof.get("proposal_id"),proof.get("transition_digest"),proof.get("kind"))!=(pid,td,kind): raise SuffixIntegrityError("proof identity")
                if kind=="rotate_recovery":
                    new=self.store._get(q,c1)
                    if r1!=root.authority_id: raise SuffixIntegrityError("root successor")
                    payload=rotation_payload(root,rec,new)
                    if proof.get("payload")!=payload: raise SuffixIntegrityError("payload")
                    verify_threshold(rec,payload,proof.get("sig1",[])); verify_threshold(new,payload,proof.get("sig2",[])); verify_threshold(root,payload,proof.get("sig3",[]))
                    expected_td=digest({"proposal_id":pid,"kind":kind,"predecessor_root_id":r0,"predecessor_recovery_id":c0,"successor":new.descriptor})
                    rec=new
                elif kind=="recover_root":
                    new=self.store._get(q,r1)
                    if c1!=rec.authority_id: raise SuffixIntegrityError("recovery successor")
                    payload=recovery_payload(root,new,rec)
                    if proof.get("payload")!=payload: raise SuffixIntegrityError("payload")
                    verify_threshold(rec,payload,proof.get("sig1",[]))
                    expected_td=digest({"proposal_id":pid,"kind":kind,"predecessor_root_id":r0,"predecessor_recovery_id":c0,"successor":new.descriptor})
                    root=new
                else: raise SuffixIntegrityError("kind")
                if td!=expected_td: raise SuffixIntegrityError("transition digest")
                expected+=1; count+=1
            head=q.execute("SELECT root_id,recovery_id,sequence FROM head WHERE singleton=1").fetchone()
            derived=(root.authority_id,rec.authority_id,expected-1)
            if head!=derived: raise CheckpointHeadMismatch("suffix/head mismatch")
            q.commit(); return {"root_id":derived[0],"recovery_id":derived[1],"sequence":derived[2],"suffix_transitions_verified":count,"checkpoint_sequence":cp.sequence,"prefix_commitment":cp.prefix_commitment}
        except:
            if q.in_transaction:q.rollback()
            raise
        finally:q.close()
    def latest_checkpoint(self):
        q=self.store._con()
        try:
            row=q.execute("SELECT c.body_json FROM checkpoint_watermark w JOIN history_checkpoints c ON c.checkpoint_id=w.checkpoint_id WHERE w.singleton=1").fetchone()
            if not row: raise CheckpointAuthenticationError("no checkpoint")
            return HistoryCheckpoint.parse(row[0])
        finally:q.close()

class UnsafeCheckpointCache:
    """Deliberately trusts caller-supplied derived state and skips prefix proof checks."""
    def resume(self,store,cached):
        q=store._con()
        try:
            root=store._get(q,cached["root_id"]); rec=store._get(q,cached["recovery_id"]); seq=int(cached["sequence"])
            for n,kind,r1,c1 in q.execute("SELECT sequence,kind,successor_root_id,successor_recovery_id FROM transitions WHERE sequence>? ORDER BY sequence",(seq,)).fetchall():
                if n!=seq+1: raise SuffixIntegrityError("unsafe suffix gap")
                if kind=="rotate_recovery": rec=store._get(q,c1)
                elif kind=="recover_root": root=store._get(q,r1)
                seq=n
            return {"root_id":root.authority_id,"recovery_id":rec.authority_id,"sequence":seq}
        finally:q.close()
