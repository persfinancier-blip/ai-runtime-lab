from __future__ import annotations
import hashlib, json, sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

class HistoryError(RuntimeError): pass
class IntegrityError(HistoryError): pass
class ThresholdError(HistoryError): pass
class StaleAuthority(HistoryError): pass
class LegacyBoundaryError(HistoryError): pass
class ProofRebind(HistoryError): pass
class UnsupportedLegacyProof(HistoryError): pass

def canon(obj): return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()
def sha(obj): return hashlib.sha256(obj if isinstance(obj,(bytes,bytearray)) else canon(obj)).hexdigest()
def public_id(raw): return sha(bytes(raw))

@dataclass(frozen=True)
class PublicSigner:
    signer_id:str; public_hex:str
    def validate(self):
        try:
            raw=bytes.fromhex(self.public_hex); Ed25519PublicKey.from_public_bytes(raw)
        except Exception as exc: raise IntegrityError("invalid public key") from exc
        if self.signer_id != public_id(raw): raise IntegrityError("signer id/public key mismatch")

class RecoverySigner:
    def __init__(self, seed:bytes):
        if len(seed)!=32: raise ValueError("Ed25519 seed must be 32 bytes")
        self._private=Ed25519PrivateKey.from_private_bytes(seed)
        raw=self._private.public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)
        self.public=PublicSigner(public_id(raw),raw.hex())
    def sign(self,payload): return Signature(self.public.signer_id,self._private.sign(canon(payload)).hex())

@dataclass(frozen=True)
class Signature: signer_id:str; signature_hex:str

@dataclass(frozen=True)
class RecoveryAuthority:
    authority_id:str; version:int; generation:int; threshold:int; signers:tuple[PublicSigner,...]; revoked:tuple[str,...]=()
    @classmethod
    def build(cls,version,generation,threshold,signers,revoked=()):
        ss=tuple(signers); body={"version":version,"generation":generation,"threshold":threshold,"signers":[{"signer_id":s.signer_id,"public_hex":s.public_hex} for s in ss],"revoked":sorted(revoked)}
        return cls(sha(body),version,generation,threshold,ss,tuple(sorted(revoked)))
    @property
    def descriptor(self): return {"authority_id":self.authority_id,"version":self.version,"generation":self.generation,"threshold":self.threshold,"signers":[{"signer_id":s.signer_id,"public_hex":s.public_hex} for s in self.signers],"revoked":list(self.revoked)}
    def validate(self):
        if type(self.version) is not int or type(self.generation) is not int or min(self.version,self.generation)<1: raise IntegrityError("version/generation")
        if type(self.threshold) is not int or self.threshold<1: raise IntegrityError("threshold")
        seen=set()
        for s in self.signers:
            s.validate()
            if s.signer_id in seen: raise IntegrityError("duplicate signer")
            seen.add(s.signer_id)
        if self.threshold>len(seen-set(self.revoked)): raise IntegrityError("threshold exceeds active signers")
        d=dict(self.descriptor); claimed=d.pop("authority_id")
        if sha(d)!=claimed: raise IntegrityError("authority content id")

def verify_threshold(authority,payload,signatures):
    authority.validate(); keys={s.signer_id:bytes.fromhex(s.public_hex) for s in authority.signers}; revoked=set(authority.revoked); used=set(); accepted=[]
    for sig in signatures:
        if sig.signer_id in used or sig.signer_id in revoked: continue
        key=keys.get(sig.signer_id)
        if key is None: continue
        try: Ed25519PublicKey.from_public_bytes(key).verify(bytes.fromhex(sig.signature_hex),canon(payload))
        except (ValueError,InvalidSignature): continue
        used.add(sig.signer_id); accepted.append(sig)
    if len(accepted)<authority.threshold: raise ThresholdError(f"valid={len(accepted)} threshold={authority.threshold}")
    return tuple(accepted)

def boundary_payload(legacy_digest,cutoff_sequence,root_id,recovery): return {"kind":"asymmetric-break-glass-boundary-v1","legacy_digest":legacy_digest,"cutoff_sequence":cutoff_sequence,"root_id":root_id,"recovery_authority_id":recovery.authority_id,"recovery_version":recovery.version,"recovery_generation":recovery.generation}
def break_glass_payload(sequence,predecessor_root_id,successor_root_id,recovery): return {"kind":"asymmetric-break-glass-proof-v1","sequence":sequence,"predecessor_root_id":predecessor_root_id,"successor_root_id":successor_root_id,"recovery_authority_id":recovery.authority_id,"recovery_version":recovery.version,"recovery_generation":recovery.generation}
def rotation_payload(old,new): return {"kind":"asymmetric-recovery-rotation-v1","old_authority_id":old.authority_id,"new_authority":new.descriptor}

class PublicOnlyBreakGlassHistory:
    def __init__(self,path:Path|str,bootstrap:RecoveryAuthority):
        bootstrap.validate(); self.path=str(path); self.bootstrap_id=bootstrap.authority_id
        q=sqlite3.connect(self.path)
        q.executescript("""
        CREATE TABLE IF NOT EXISTS recovery_authorities(authority_id TEXT PRIMARY KEY, body TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS recovery_head(singleton INTEGER PRIMARY KEY CHECK(singleton=1), authority_id TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS recovery_rotations(sequence INTEGER PRIMARY KEY, old_id TEXT NOT NULL, new_id TEXT NOT NULL, payload TEXT NOT NULL, old_sigs TEXT NOT NULL, new_sigs TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS migration_boundary(singleton INTEGER PRIMARY KEY CHECK(singleton=1), legacy_digest TEXT NOT NULL, cutoff_sequence INTEGER NOT NULL, root_id TEXT NOT NULL, recovery_authority_id TEXT NOT NULL, payload TEXT NOT NULL, signatures TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS break_glass_proofs(sequence INTEGER PRIMARY KEY, predecessor_root_id TEXT NOT NULL, successor_root_id TEXT NOT NULL, recovery_authority_id TEXT NOT NULL, payload TEXT NOT NULL, signatures TEXT NOT NULL);
        """)
        if q.execute("SELECT COUNT(*) FROM recovery_head").fetchone()[0]==0:
            self._put_authority(q,bootstrap); q.execute("INSERT INTO recovery_head VALUES(1,?)",(bootstrap.authority_id,)); q.commit()
        q.close(); self.verify_durable()
    def _con(self):
        q=sqlite3.connect(self.path,timeout=5); q.execute("PRAGMA busy_timeout=5000"); return q
    @staticmethod
    def _decode_authority(body):
        d=json.loads(body); a=RecoveryAuthority(d["authority_id"],d["version"],d["generation"],d["threshold"],tuple(PublicSigner(x["signer_id"],x["public_hex"]) for x in d["signers"]),tuple(d.get("revoked",[]))); a.validate(); return a
    def _put_authority(self,q,a):
        a.validate(); body=json.dumps(a.descriptor,sort_keys=True,separators=(",",":")); q.execute("INSERT OR IGNORE INTO recovery_authorities VALUES(?,?)",(a.authority_id,body)); row=q.execute("SELECT body FROM recovery_authorities WHERE authority_id=?",(a.authority_id,)).fetchone()
        if not row or row[0]!=body: raise IntegrityError("authority substitution")
    def _authority(self,q,aid):
        row=q.execute("SELECT body FROM recovery_authorities WHERE authority_id=?",(aid,)).fetchone()
        if not row: raise IntegrityError("missing historical public authority")
        a=self._decode_authority(row[0])
        if a.authority_id!=aid: raise IntegrityError("authority rebound")
        return a
    @staticmethod
    def _sigs(raw): return tuple(Signature(x["signer_id"],x["signature_hex"]) for x in json.loads(raw))
    @staticmethod
    def _sig_json(sigs): return json.dumps([{"signer_id":s.signer_id,"signature_hex":s.signature_hex} for s in sigs],sort_keys=True,separators=(",",":"))
    def establish_boundary(self,legacy_digest,cutoff_sequence,root_id,signatures):
        if not isinstance(legacy_digest,str) or len(legacy_digest)!=64 or any(c not in "0123456789abcdef" for c in legacy_digest): raise LegacyBoundaryError("legacy digest")
        if type(cutoff_sequence) is not int or cutoff_sequence<0: raise LegacyBoundaryError("cutoff")
        q=self._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            if q.execute("SELECT 1 FROM migration_boundary").fetchone(): raise LegacyBoundaryError("boundary exists")
            a=self._authority(q,q.execute("SELECT authority_id FROM recovery_head").fetchone()[0]); payload=boundary_payload(legacy_digest,cutoff_sequence,root_id,a); accepted=verify_threshold(a,payload,signatures)
            q.execute("INSERT INTO migration_boundary VALUES(1,?,?,?,?,?,?)",(legacy_digest,cutoff_sequence,root_id,a.authority_id,json.dumps(payload,sort_keys=True,separators=(",",":")),self._sig_json(accepted))); q.commit(); return sha(payload)
        except:
            if q.in_transaction:q.rollback()
            raise
        finally:q.close()
    def rotate_authority(self,new,old_signatures,new_signatures):
        q=self._con()
        try:
            q.execute("BEGIN IMMEDIATE"); old=self._authority(q,q.execute("SELECT authority_id FROM recovery_head").fetchone()[0]); new.validate()
            if new.version!=old.version+1 or new.generation<=old.generation: raise StaleAuthority("non-monotonic successor")
            payload=rotation_payload(old,new); osigs=verify_threshold(old,payload,old_signatures); nsigs=verify_threshold(new,payload,new_signatures); self._put_authority(q,new); seq=q.execute("SELECT COALESCE(MAX(sequence),0)+1 FROM recovery_rotations").fetchone()[0]
            q.execute("INSERT INTO recovery_rotations VALUES(?,?,?,?,?,?)",(seq,old.authority_id,new.authority_id,json.dumps(payload,sort_keys=True,separators=(",",":")),self._sig_json(osigs),self._sig_json(nsigs))); q.execute("UPDATE recovery_head SET authority_id=? WHERE singleton=1 AND authority_id=?",(new.authority_id,old.authority_id)); q.commit()
        except:
            if q.in_transaction:q.rollback()
            raise
        finally:q.close()
    def record_break_glass(self,sequence,predecessor_root_id,successor_root_id,signatures):
        q=self._con()
        try:
            q.execute("BEGIN IMMEDIATE"); b=q.execute("SELECT cutoff_sequence FROM migration_boundary").fetchone()
            if not b: raise LegacyBoundaryError("no boundary")
            if type(sequence) is not int or sequence<=b[0]: raise UnsupportedLegacyProof("legacy sequence")
            a=self._authority(q,q.execute("SELECT authority_id FROM recovery_head").fetchone()[0]); payload=break_glass_payload(sequence,predecessor_root_id,successor_root_id,a); accepted=verify_threshold(a,payload,signatures)
            q.execute("INSERT INTO break_glass_proofs VALUES(?,?,?,?,?,?)",(sequence,predecessor_root_id,successor_root_id,a.authority_id,json.dumps(payload,sort_keys=True,separators=(",",":")),self._sig_json(accepted))); q.commit(); return sha(payload)
        except:
            if q.in_transaction:q.rollback()
            raise
        finally:q.close()
    def verify_durable(self):
        q=self._con()
        try:
            q.execute("BEGIN IMMEDIATE"); current=self._authority(q,self.bootstrap_id)
            for seq,old_id,new_id,praw,osraw,nsraw in q.execute("SELECT sequence,old_id,new_id,payload,old_sigs,new_sigs FROM recovery_rotations ORDER BY sequence"):
                if old_id!=current.authority_id: raise IntegrityError("rotation continuity")
                new=self._authority(q,new_id); payload=json.loads(praw)
                if payload!=rotation_payload(current,new): raise IntegrityError("rotation payload")
                verify_threshold(current,payload,self._sigs(osraw)); verify_threshold(new,payload,self._sigs(nsraw)); current=new
            if q.execute("SELECT authority_id FROM recovery_head").fetchone()[0]!=current.authority_id: raise IntegrityError("head/history")
            b=q.execute("SELECT legacy_digest,cutoff_sequence,root_id,recovery_authority_id,payload,signatures FROM migration_boundary").fetchone(); cutoff=None
            if b:
                legacy,cutoff,root_id,aid,praw,sraw=b; a=self._authority(q,aid); payload=json.loads(praw)
                if payload!=boundary_payload(legacy,cutoff,root_id,a): raise LegacyBoundaryError("boundary rebound")
                verify_threshold(a,payload,self._sigs(sraw))
            for seq,pred,succ,aid,praw,sraw in q.execute("SELECT sequence,predecessor_root_id,successor_root_id,recovery_authority_id,payload,signatures FROM break_glass_proofs ORDER BY sequence"):
                if cutoff is None or seq<=cutoff: raise UnsupportedLegacyProof("legacy row in asymmetric table")
                a=self._authority(q,aid); payload=json.loads(praw)
                if payload!=break_glass_payload(seq,pred,succ,a): raise ProofRebind("proof rebound")
                verify_threshold(a,payload,self._sigs(sraw))
            q.commit(); return True
        except:
            if q.in_transaction:q.rollback()
            raise
        finally:q.close()

class UnsafeLegacyAutoPromotion:
    def promote(self,legacy_sequence,legacy_hmac_proof): return bool(legacy_hmac_proof) and legacy_sequence>=0
