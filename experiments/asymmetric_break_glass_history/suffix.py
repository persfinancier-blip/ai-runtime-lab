from __future__ import annotations

from experiments.asymmetric_provider_history.supported import SupportedAsymmetricHistoricalSharedAnchorLedger
from experiments.provider_threshold_rotation.protocol import InvalidAuthority,ProviderRotationIntent,StaleAuthority,ThresholdNotMet,ThresholdProof,verify_threshold
from experiments.provider_threshold_rotation.strict import require_canonical_authority
from experiments.provider_rotation_recovery.protocol import RecoveryAuthorityMismatch,RecoveryError
from experiments.provider_recovery_authority_lifecycle.asymmetric_custody import accepted_public_signatures,verify_public_threshold
from experiments.provider_recovery_authority_lifecycle.final_supported import SupportedRecoveryCustodyLedger
from experiments.provider_recovery_authority_lifecycle.supported import SupportedRecoveryAuthorityLifecycleLedger
from .migration_guard import AuthenticatedBreakGlassMigrationGuard,MigrationGuardError,_digest

class AsymmetricBreakGlassError(RuntimeError): pass

def asymmetric_break_glass_payload(*,boundary_digest,old_root,new_root,symmetric_authority,public_authority):
    return {"kind":"provider-asymmetric-break-glass-v1","boundary_digest":boundary_digest,
        "old_root_id":old_root.authority_id,"old_root_version":old_root.version,"old_root_generation":old_root.generation,
        "new_root":new_root.descriptor,"symmetric_authority_id":symmetric_authority.authority_id,
        "symmetric_authority_version":symmetric_authority.version,"symmetric_authority_generation":symmetric_authority.generation,
        "public_authority_id":public_authority.authority_id,"public_authority_version":public_authority.version,
        "public_authority_generation":public_authority.generation}

class SupportedAsymmetricBreakGlassLedger(SupportedRecoveryCustodyLedger):
    """Real LAB-086 surface: legacy HMAC proof history + Ed25519-only suffix."""
    def __init__(self,*args,**kwargs):
        self._lab086_initializing=True;super().__init__(*args,**kwargs);self._lab086_initializing=False
        self.migration_guard=AuthenticatedBreakGlassMigrationGuard(self)
        q=self._con()
        try:q.execute("BEGIN IMMEDIATE");self._ensure_asymmetric_schema_locked(q);q.commit()
        except:
            if q.in_transaction:q.rollback()
            raise
        finally:q.close()
        self.verify_durable()
    @staticmethod
    def _ensure_asymmetric_schema_locked(q):
        q.execute("""CREATE TABLE IF NOT EXISTS provider_asymmetric_break_glass_proofs(
          new_rotation_authority_id TEXT PRIMARY KEY,old_rotation_authority_id TEXT NOT NULL,
          old_rotation_version INTEGER NOT NULL,old_rotation_generation INTEGER NOT NULL,
          symmetric_authority_id TEXT NOT NULL,public_authority_id TEXT NOT NULL,
          public_authority_version INTEGER NOT NULL,public_authority_generation INTEGER NOT NULL,
          boundary_digest TEXT NOT NULL,intent_digest TEXT NOT NULL,public_signatures_json TEXT NOT NULL)""")
    def recover_rotation_authority(self,*a,**k): raise AsymmetricBreakGlassError("HMAC-only recovery is verification-only history")
    def recover_rotation_authority_with_custody(self,*a,**k): raise AsymmetricBreakGlassError("compatibility HMAC recovery is disabled after LAB-086 migration")
    @staticmethod
    def _require_successor(old,new):
        if new.authority_name!=old.authority_name or new.version!=old.version+1 or new.generation!=old.generation+1:
            raise AsymmetricBreakGlassError("root successor must advance version/generation exactly one")
    def _provider_transitions_locked(self,q):
        enablement=self._load_enablement_locked(q)
        rows=q.execute("SELECT t.provider_id,t.old_generation_id,t.new_generation_id,g.generation FROM asymmetric_provider_transitions t JOIN asymmetric_provider_generations g ON g.generation_id=t.new_generation_id WHERE g.generation>? ORDER BY g.generation",(enablement.start_provider_generation,)).fetchall()
        return [(r[0],r[1],r[2]) for r in rows]
    def asymmetric_recovery_payload(self,new_authority):
        require_canonical_authority(new_authority);q=self._con()
        try:
            q.execute("BEGIN IMMEDIATE");self._ensure_asymmetric_schema_locked(q);self._verify_lab086_locked(q)
            boundary=self.migration_guard.verify_locked(q)
            if boundary is None:raise MigrationGuardError("authenticated migration boundary required")
            old=self.rotation_authority.current_locked(q);symmetric=self.recovery_lifecycle.current_locked(q);public=self.public_recovery_custody.current_locked(q);compat=self.recovery.current_recovery_locked(q)
            if compat.authority_id!=symmetric.recovery.authority_id:raise RecoveryAuthorityMismatch("recovery heads diverged")
            self._compatible(symmetric,public);self._require_successor(old,new_authority)
            out=asymmetric_break_glass_payload(boundary_digest=boundary["boundary_digest"],old_root=old,new_root=new_authority,symmetric_authority=symmetric,public_authority=public);q.commit();return out
        except:
            if q.in_transaction:q.rollback()
            raise
        finally:q.close()
    def recover_rotation_authority_asymmetric(self,new_authority,public_signatures):
        require_canonical_authority(new_authority);q=self._con()
        try:
            q.execute("BEGIN IMMEDIATE");self._reject_prepared_locked(q);self._ensure_asymmetric_schema_locked(q);self._verify_lab086_locked(q)
            boundary=self.migration_guard.verify_locked(q)
            if boundary is None:raise MigrationGuardError("authenticated migration boundary required")
            old=self.rotation_authority.current_locked(q);symmetric=self.recovery_lifecycle.current_locked(q);public=self.public_recovery_custody.current_locked(q);compat=self.recovery.current_recovery_locked(q)
            if compat.authority_id!=symmetric.recovery.authority_id:raise RecoveryAuthorityMismatch("recovery heads diverged")
            self._compatible(symmetric,public);self._require_successor(old,new_authority)
            payload=asymmetric_break_glass_payload(boundary_digest=boundary["boundary_digest"],old_root=old,new_root=new_authority,symmetric_authority=symmetric,public_authority=public)
            accepted=accepted_public_signatures(public,payload,tuple(public_signatures));verify_public_threshold(public,payload,accepted);encoded=self.public_recovery_custody._encode_signatures(accepted);intent=_digest(payload)
            self.rotation_authority._insert_authority_locked(q,new_authority)
            changed=q.execute("UPDATE provider_rotation_authority_head SET authority_id=?,version=?,generation=? WHERE singleton=1 AND authority_id=? AND version=? AND generation=?",(new_authority.authority_id,new_authority.version,new_authority.generation,old.authority_id,old.version,old.generation)).rowcount
            if changed!=1:raise StaleAuthority("root head changed during asymmetric recovery")
            q.execute("INSERT INTO provider_asymmetric_break_glass_proofs VALUES(?,?,?,?,?,?,?,?,?,?,?)",(new_authority.authority_id,old.authority_id,old.version,old.generation,symmetric.authority_id,public.authority_id,public.version,public.generation,boundary["boundary_digest"],intent,encoded))
            self._verify_lab086_locked(q);q.commit()
            return {"old_rotation_authority_id":old.authority_id,"new_rotation_authority_id":new_authority.authority_id,"public_recovery_authority_id":public.authority_id,"public_recovery_signers":tuple(sorted(s.signer_id for s in accepted)),"intent_digest":intent}
        except:
            if q.in_transaction:q.rollback()
            raise
        finally:q.close()
    def _verify_asymmetric_edge_locked(self,q,old,new,windows,boundary_digest):
        row=q.execute("SELECT old_rotation_authority_id,old_rotation_version,old_rotation_generation,symmetric_authority_id,public_authority_id,public_authority_version,public_authority_generation,boundary_digest,intent_digest,public_signatures_json FROM provider_asymmetric_break_glass_proofs WHERE new_rotation_authority_id=?",(new.authority_id,)).fetchone()
        if row is None:raise AsymmetricBreakGlassError("missing asymmetric proof")
        if (row[0],row[1],row[2])!=(old.authority_id,old.version,old.generation):raise AsymmetricBreakGlassError("asymmetric predecessor mismatch")
        if row[7]!=boundary_digest:raise AsymmetricBreakGlassError("boundary mismatch")
        symmetric=self.recovery_lifecycle._load_recovery_locked(q,row[3]);public=self.public_recovery_custody._load_authority_locked(q,row[4]);self._compatible(symmetric,public)
        if (public.version,public.generation)!=(row[5],row[6]):raise AsymmetricBreakGlassError("public recovery metadata mismatch")
        binding=q.execute("SELECT public_authority_id,version,generation FROM provider_recovery_custody_bindings WHERE symmetric_authority_id=?",(symmetric.authority_id,)).fetchone()
        if binding!=(public.authority_id,symmetric.version,symmetric.generation):raise AsymmetricBreakGlassError("unbound public recovery authority")
        window=windows.get(symmetric.recovery.authority_id)
        if window is None:raise RecoveryAuthorityMismatch("unknown recovery generation")
        versioned,lower,upper=window
        if versioned.authority_id!=symmetric.authority_id:raise RecoveryAuthorityMismatch("recovery lifecycle mismatch")
        if lower is not None and old.version<lower:raise RecoveryAuthorityMismatch("generation used before activation")
        if upper is not None and old.version>=upper:raise RecoveryAuthorityMismatch("stale generation used after rotation")
        payload=asymmetric_break_glass_payload(boundary_digest=boundary_digest,old_root=old,new_root=new,symmetric_authority=symmetric,public_authority=public)
        if _digest(payload)!=row[8]:raise AsymmetricBreakGlassError("intent digest mismatch")
        decoded=self.public_recovery_custody._decode_signatures(row[9]);accepted=accepted_public_signatures(public,payload,decoded);verify_public_threshold(public,payload,accepted)
        if self.public_recovery_custody._encode_signatures(accepted)!=row[9]:raise AsymmetricBreakGlassError("noncanonical signatures")
    def _verify_provider_thresholds_locked(self,q,by_id):
        for provider_id,old_gid,new_gid in self._provider_transitions_locked(q):
            row=q.execute("SELECT authority_id,authority_version,authority_generation,intent_digest,signatures_json FROM provider_rotation_threshold_proofs WHERE new_provider_generation_id=?",(new_gid,)).fetchone()
            if row is None:raise ThresholdNotMet("provider transition missing threshold proof")
            authority=by_id.get(row[0])
            if authority is None:raise InvalidAuthority("provider proof references unknown root")
            intent=ProviderRotationIntent(provider_id,old_gid,new_gid,authority.authority_id,authority.version,authority.generation);proof=ThresholdProof(row[3],row[0],row[1],row[2],self.rotation_authority._decode_signatures(row[4]));verify_threshold(authority,intent,proof)
    def _verify_lab086_locked(self,q):
        self._ensure_asymmetric_schema_locked(q);self._verify_custody_bindings_locked(q);self._verify_break_glass_custody_locked(q);boundary=self.migration_guard.verify_locked(q)
        if boundary is None:
            return SupportedRecoveryAuthorityLifecycleLedger._verify_mixed_authority_history_locked(self,q,self._provider_transitions_locked(q))
        rows=q.execute("SELECT authority_id FROM provider_rotation_authorities ORDER BY version").fetchall()
        if not rows:raise InvalidAuthority("missing root history")
        authorities=[self.rotation_authority._load_locked(q,r[0]) for r in rows]
        if authorities[0].authority_id!=self.rotation_authority.bootstrap.authority_id:raise StaleAuthority("root bootstrap changed")
        by_id={a.authority_id:a for a in authorities};windows=self._lifecycle_windows_locked(q,by_id)
        total=q.execute("SELECT COUNT(*) FROM provider_rotation_authority_transitions").fetchone()[0]+q.execute("SELECT COUNT(*) FROM provider_rotation_recovery_transitions").fetchone()[0]+q.execute("SELECT COUNT(*) FROM provider_asymmetric_break_glass_proofs").fetchone()[0]
        if total!=len(authorities)-1:raise RecoveryError("root proof count mismatch")
        for old,new in zip(authorities,authorities[1:]):
            self._require_successor(old,new)
            normal=q.execute("SELECT COUNT(*) FROM provider_rotation_authority_transitions WHERE new_authority_id=?",(new.authority_id,)).fetchone()[0]
            legacy=q.execute("SELECT recovery_authority_id,recovery_generation FROM provider_rotation_recovery_transitions WHERE new_rotation_authority_id=?",(new.authority_id,)).fetchone();asym=q.execute("SELECT COUNT(*) FROM provider_asymmetric_break_glass_proofs WHERE new_rotation_authority_id=?",(new.authority_id,)).fetchone()[0]
            if normal+(0 if legacy is None else 1)+asym!=1:raise RecoveryError("root edge must have exactly one proof type")
            if normal:self._verify_normal_edge_locked(q,old,new)
            elif legacy is not None:
                window=windows.get(legacy[0])
                if window is None:raise RecoveryAuthorityMismatch("legacy proof unknown recovery generation")
                versioned,lower,upper=window
                if versioned.recovery.generation!=legacy[1]:raise RecoveryAuthorityMismatch("legacy generation mismatch")
                if lower is not None and old.version<lower:raise RecoveryAuthorityMismatch("legacy used before activation")
                if upper is not None and old.version>=upper:raise RecoveryAuthorityMismatch("legacy used after deactivation")
                self.recovery.verify_recovery_transition_with_authority_locked(q,old,new,versioned.recovery)
            else:
                if old.version<boundary["root_version"]:raise AsymmetricBreakGlassError("asymmetric proof before cutoff")
                self._verify_asymmetric_edge_locked(q,old,new,windows,boundary["boundary_digest"])
        if self.rotation_authority.current_locked(q).authority_id!=authorities[-1].authority_id:raise StaleAuthority("root head rollback")
        self._verify_provider_thresholds_locked(q,by_id);return True
    def verify_durable(self):
        if getattr(self,"_lab086_initializing",False) or not hasattr(self,"migration_guard"):return True
        # Hold one write-excluding guard across every lower verifier and the LAB-086
        # cross-layer checks.  Running provider/public-custody verification before
        # acquiring this guard permits a concurrent writer to mutate already-checked
        # proof rows before the final binding pass observes them.
        q=self._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            SupportedAsymmetricHistoricalSharedAnchorLedger.verify_durable(self)
            self.public_recovery_custody.verify_durable()
            self._verify_lab086_locked(q)
            q.commit();return True
        except:
            if q.in_transaction:q.rollback()
            raise
        finally:q.close()
