from __future__ import annotations

import hashlib
import json

from experiments.provider_recovery_authority_lifecycle.asymmetric_custody import accepted_public_signatures,verify_public_threshold
from experiments.provider_recovery_authority_lifecycle.final_supported import SupportedRecoveryCustodyLedger
from experiments.provider_recovery_authority_lifecycle.supported import SupportedRecoveryAuthorityLifecycleLedger
from experiments.provider_rotation_recovery.protocol import RecoveryAuthorityMismatch

class MigrationGuardError(RuntimeError): pass
class LegacyHistoryChanged(MigrationGuardError): pass

def _canon(value)->bytes:return json.dumps(value,sort_keys=True,separators=(",",":")).encode()
def _digest(value)->str:
    raw=value if isinstance(value,(bytes,bytearray)) else _canon(value)
    return hashlib.sha256(raw).hexdigest()
def migration_payload(*,legacy_digest,cutoff_root,symmetric_authority_id,public_authority):
    return {"kind":"provider-asymmetric-break-glass-boundary-v1","legacy_digest":legacy_digest,
        "cutoff_root_id":cutoff_root.authority_id,"cutoff_root_version":cutoff_root.version,"cutoff_root_generation":cutoff_root.generation,
        "symmetric_authority_id":symmetric_authority_id,"public_authority_id":public_authority.authority_id,
        "public_authority_version":public_authority.version,"public_authority_generation":public_authority.generation}
def _exact_supported_ledger(ledger):
    if type(ledger) is SupportedRecoveryCustodyLedger:return True
    try:
        from experiments.asymmetric_break_glass_history.suffix import SupportedAsymmetricBreakGlassLedger
    except ImportError:return False
    return type(ledger) is SupportedAsymmetricBreakGlassLedger

class AuthenticatedBreakGlassMigrationGuard:
    def __init__(self,ledger):
        if not _exact_supported_ledger(ledger):raise TypeError("exact LAB-085/LAB-086 supported ledger required")
        self.ledger=ledger;q=ledger._con()
        try:
            q.execute("BEGIN IMMEDIATE");self._ensure_schema_locked(q)
            if type(ledger) is SupportedRecoveryCustodyLedger:self._verify_inherited_locked(q)
            self.verify_locked(q);q.commit()
        except:
            if q.in_transaction:q.rollback()
            raise
        finally:q.close()
    @staticmethod
    def _ensure_schema_locked(q):
        q.execute("""CREATE TABLE IF NOT EXISTS provider_asymmetric_break_glass_boundary(
          singleton INTEGER PRIMARY KEY CHECK(singleton=1),legacy_digest TEXT NOT NULL,
          cutoff_root_id TEXT NOT NULL,cutoff_root_version INTEGER NOT NULL,cutoff_root_generation INTEGER NOT NULL,
          symmetric_authority_id TEXT NOT NULL,public_authority_id TEXT NOT NULL,public_authority_version INTEGER NOT NULL,
          public_authority_generation INTEGER NOT NULL,boundary_digest TEXT NOT NULL,signatures_json TEXT NOT NULL)""")
        q.execute("""CREATE TRIGGER IF NOT EXISTS provider_asymmetric_break_glass_no_legacy_hmac
        BEFORE INSERT ON provider_rotation_recovery_transitions
        WHEN EXISTS(SELECT 1 FROM provider_asymmetric_break_glass_boundary WHERE singleton=1)
        BEGIN SELECT RAISE(ABORT,'LAB-086 migration forbids new HMAC break-glass rows'); END""")
    def _verify_inherited_locked(self,q):
        SupportedRecoveryAuthorityLifecycleLedger.verify_durable(self.ledger)
        self.ledger.public_recovery_custody.verify_durable();self.ledger._verify_custody_bindings_locked(q);self.ledger._verify_break_glass_custody_locked(q);return True
    def _verify_preboundary_locked(self,q):
        if type(self.ledger) is SupportedRecoveryCustodyLedger:return self._verify_inherited_locked(q)
        # Exact LAB-086 surface reuses its own pre-boundary branch, which delegates
        # to the full LAB-085 mixed-root verifier while the same write fence is held.
        return self.ledger._verify_lab086_locked(q)
    def _legacy_snapshot_locked(self,q,cutoff_version):
        rows=q.execute("SELECT r.new_rotation_authority_id,r.old_rotation_authority_id,r.old_rotation_version,r.old_rotation_generation,r.recovery_authority_id,r.recovery_generation,r.intent_digest,r.signatures_json FROM provider_rotation_recovery_transitions r JOIN provider_rotation_authorities a ON a.authority_id=r.new_rotation_authority_id WHERE a.version<=? ORDER BY a.version",(cutoff_version,)).fetchall();out=[]
        for row in rows:
            custody=q.execute("SELECT public_authority_id,symmetric_authority_id,compatibility_intent_digest,custody_intent_digest,public_signatures_json FROM provider_rotation_recovery_custody_proofs WHERE new_rotation_authority_id=?",(row[0],)).fetchone()
            out.append({"hmac_recovery_row":list(row),"public_custody_row":None if custody is None else list(custody)})
        return out
    def _legacy_digest_locked(self,q,cutoff_version):return _digest(self._legacy_snapshot_locked(q,cutoff_version))
    def _current_components_locked(self,q):
        root=self.ledger.rotation_authority.current_locked(q);symmetric=self.ledger.recovery_lifecycle.current_locked(q);compat=self.ledger.recovery.current_recovery_locked(q);public=self.ledger.public_recovery_custody.current_locked(q)
        if compat.authority_id!=symmetric.recovery.authority_id:raise RecoveryAuthorityMismatch("LAB-084/LAB-085 recovery heads diverged")
        self.ledger._compatible(symmetric,public);return root,symmetric,public
    def _verify_boundary_recovery_window_locked(self,q,root,symmetric):
        roots={}
        for (authority_id,) in q.execute("SELECT authority_id FROM provider_rotation_authorities ORDER BY version").fetchall():
            candidate=self.ledger.rotation_authority._load_locked(q,authority_id);roots[candidate.authority_id]=candidate
        window=self.ledger._lifecycle_windows_locked(q,roots).get(symmetric.recovery.authority_id)
        if window is None:raise MigrationGuardError("boundary references unknown recovery generation")
        versioned,lower,upper=window
        if versioned.authority_id!=symmetric.authority_id:raise MigrationGuardError("boundary recovery lifecycle identity mismatch")
        if lower is not None and root.version<lower:raise MigrationGuardError("boundary recovery generation used before activation")
        if upper is not None and root.version>=upper:raise MigrationGuardError("stale recovery generation cannot authorize migration boundary")
        return True
    def payload(self):
        q=self.ledger._con()
        try:
            q.execute("BEGIN IMMEDIATE");self._ensure_schema_locked(q)
            if q.execute("SELECT 1 FROM provider_asymmetric_break_glass_boundary WHERE singleton=1").fetchone():raise MigrationGuardError("migration boundary already exists")
            self.ledger._reject_prepared_locked(q);self._verify_preboundary_locked(q);root,symmetric,public=self._current_components_locked(q)
            out=migration_payload(legacy_digest=self._legacy_digest_locked(q,root.version),cutoff_root=root,symmetric_authority_id=symmetric.authority_id,public_authority=public);q.commit();return out
        except:
            if q.in_transaction:q.rollback()
            raise
        finally:q.close()
    def establish(self,public_signatures):
        q=self.ledger._con()
        try:
            q.execute("BEGIN IMMEDIATE");self._ensure_schema_locked(q)
            if q.execute("SELECT 1 FROM provider_asymmetric_break_glass_boundary WHERE singleton=1").fetchone():raise MigrationGuardError("migration boundary already exists")
            self.ledger._reject_prepared_locked(q);self._verify_preboundary_locked(q);root,symmetric,public=self._current_components_locked(q);legacy=self._legacy_digest_locked(q,root.version)
            payload=migration_payload(legacy_digest=legacy,cutoff_root=root,symmetric_authority_id=symmetric.authority_id,public_authority=public);accepted=accepted_public_signatures(public,payload,tuple(public_signatures));verify_public_threshold(public,payload,accepted);bd=_digest(payload)
            q.execute("INSERT INTO provider_asymmetric_break_glass_boundary VALUES(1,?,?,?,?,?,?,?,?,?,?)",(legacy,root.authority_id,root.version,root.generation,symmetric.authority_id,public.authority_id,public.version,public.generation,bd,self.ledger.public_recovery_custody._encode_signatures(accepted)));self.verify_locked(q);q.commit();return bd
        except:
            if q.in_transaction:q.rollback()
            raise
        finally:q.close()
    def verify_locked(self,q):
        row=q.execute("SELECT legacy_digest,cutoff_root_id,cutoff_root_version,cutoff_root_generation,symmetric_authority_id,public_authority_id,public_authority_version,public_authority_generation,boundary_digest,signatures_json FROM provider_asymmetric_break_glass_boundary WHERE singleton=1").fetchone()
        if row is None:return None
        legacy,rid,rv,rg,sid,pid,pv,pg,bd,sigs=row;root=self.ledger.rotation_authority._load_locked(q,rid)
        if (root.version,root.generation)!=(rv,rg):raise MigrationGuardError("boundary root metadata mismatch")
        symmetric=self.ledger.recovery_lifecycle._load_recovery_locked(q,sid);public=self.ledger.public_recovery_custody._load_authority_locked(q,pid)
        if (public.version,public.generation)!=(pv,pg):raise MigrationGuardError("boundary public authority metadata mismatch")
        self.ledger._compatible(symmetric,public);binding=q.execute("SELECT public_authority_id,version,generation FROM provider_recovery_custody_bindings WHERE symmetric_authority_id=?",(symmetric.authority_id,)).fetchone()
        if binding!=(public.authority_id,symmetric.version,symmetric.generation):raise MigrationGuardError("boundary recovery authority is not historically bound")
        self._verify_boundary_recovery_window_locked(q,root,symmetric)
        payload=migration_payload(legacy_digest=legacy,cutoff_root=root,symmetric_authority_id=sid,public_authority=public)
        if _digest(payload)!=bd:raise MigrationGuardError("boundary digest mismatch")
        decoded=self.ledger.public_recovery_custody._decode_signatures(sigs);accepted=accepted_public_signatures(public,payload,decoded);verify_public_threshold(public,payload,accepted)
        if self.ledger.public_recovery_custody._encode_signatures(accepted)!=sigs:raise MigrationGuardError("noncanonical boundary signatures")
        if self._legacy_digest_locked(q,root.version)!=legacy:raise LegacyHistoryChanged("legacy HMAC history changed after migration")
        return {"boundary_digest":bd,"legacy_digest":legacy,"root_id":root.authority_id,"root_version":root.version,"public_authority_id":public.authority_id}
    def verify(self):
        q=self.ledger._con()
        try:q.execute("BEGIN IMMEDIATE");self._ensure_schema_locked(q);result=self.verify_locked(q);q.commit();return result
        except:
            if q.in_transaction:q.rollback()
            raise
        finally:q.close()
