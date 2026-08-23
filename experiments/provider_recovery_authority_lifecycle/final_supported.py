from __future__ import annotations

from experiments.provider_threshold_rotation.strict import require_canonical_authority
from .asymmetric_custody import accepted_public_signatures, verify_public_threshold
from .custody_break_glass import (
    CustodyBreakGlassError,
    accepted_custody_break_glass_signatures,
    custody_break_glass_digest,
    custody_break_glass_payload,
    custody_enablement_payload,
)
from .public_custody_supported import SupportedPublicRecoveryAuthorityLifecycleLedger
from .supported import SupportedRecoveryAuthorityLifecycleLedger


class SupportedRecoveryCustodyLedger(SupportedPublicRecoveryAuthorityLifecycleLedger):
    """Final LAB-085 supported surface.

    Public Ed25519 custody is authoritative for every *new* break-glass effect.
    Until LAB-086 migrates historical LAB-084 rows, a new recovery also records the
    compatibility HMAC proof, but both proofs must authorize the same transition in
    the same SQLite transaction. The inherited HMAC-only recovery entry point is
    blocked on this final surface.
    """

    def __init__(self, *args, custody_enablement_signatures=None, **kwargs):
        self._lab085_enablement_signatures = tuple(custody_enablement_signatures or ())
        self._lab085_final_initializing = True
        super().__init__(*args, **kwargs)
        q = self._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            self._ensure_break_glass_schema_locked(q)
            self._verify_break_glass_custody_locked(q)
            q.commit()
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()
        self._lab085_final_initializing = False
        self._lab085_enablement_signatures = ()
        self.verify_durable()

    def _ensure_break_glass_schema_locked(self, q):
        q.execute(
            """CREATE TABLE IF NOT EXISTS provider_recovery_custody_enablement(
              singleton INTEGER PRIMARY KEY CHECK(singleton=1),
              start_rotation_authority_id TEXT NOT NULL,
              start_rotation_version INTEGER NOT NULL,
              start_rotation_generation INTEGER NOT NULL,
              symmetric_authority_id TEXT NOT NULL,
              public_authority_id TEXT NOT NULL
            )"""
        )
        q.execute(
            """CREATE TABLE IF NOT EXISTS provider_rotation_recovery_custody_proofs(
              new_rotation_authority_id TEXT PRIMARY KEY,
              public_authority_id TEXT NOT NULL,
              symmetric_authority_id TEXT NOT NULL,
              compatibility_intent_digest TEXT NOT NULL,
              custody_intent_digest TEXT NOT NULL,
              public_signatures_json TEXT NOT NULL
            )"""
        )
        q.execute(
            """CREATE TABLE IF NOT EXISTS provider_recovery_custody_enablement_proof(
              singleton INTEGER PRIMARY KEY CHECK(singleton=1),
              enablement_digest TEXT NOT NULL,
              public_signatures_json TEXT NOT NULL
            )"""
        )
        if q.execute("SELECT COUNT(*) FROM provider_recovery_custody_enablement").fetchone()[0] == 0:
            root = self.rotation_authority.current_locked(q)
            symmetric = self.recovery_lifecycle.current_locked(q)
            public = self.public_recovery_custody.current_locked(q)
            self._compatible(symmetric, public)
            q.execute(
                "INSERT INTO provider_recovery_custody_enablement VALUES(1,?,?,?,?,?)",
                (
                    root.authority_id,
                    root.version,
                    root.generation,
                    symmetric.authority_id,
                    public.authority_id,
                ),
            )
        self._verify_or_create_enablement_proof_locked(q)

    def _load_break_glass_enablement_components_locked(self, q):
        row = q.execute(
            "SELECT start_rotation_authority_id,start_rotation_version,start_rotation_generation,"
            "symmetric_authority_id,public_authority_id FROM provider_recovery_custody_enablement WHERE singleton=1"
        ).fetchone()
        if row is None:
            raise CustodyBreakGlassError("missing public-custody break-glass enablement")
        root = self.rotation_authority._load_locked(q, row[0])
        if (root.version, root.generation) != (row[1], row[2]):
            raise CustodyBreakGlassError("break-glass enablement root mismatch")
        symmetric = self.recovery_lifecycle._load_recovery_locked(q, row[3])
        public = self.public_recovery_custody._load_authority_locked(q, row[4])
        self._compatible(symmetric, public)
        binding = q.execute(
            "SELECT public_authority_id,version,generation FROM provider_recovery_custody_bindings WHERE symmetric_authority_id=?",
            (symmetric.authority_id,),
        ).fetchone()
        if binding != (public.authority_id, symmetric.version, symmetric.generation):
            raise CustodyBreakGlassError("break-glass enablement custody binding mismatch")
        return root, symmetric, public

    def _verify_or_create_enablement_proof_locked(self, q):
        root, symmetric, public = self._load_break_glass_enablement_components_locked(q)
        payload = custody_enablement_payload(root, symmetric, public)
        expected_digest = custody_break_glass_digest(payload)
        row = q.execute(
            "SELECT enablement_digest,public_signatures_json FROM provider_recovery_custody_enablement_proof WHERE singleton=1"
        ).fetchone()
        if row is None:
            if not self._lab085_enablement_signatures:
                raise CustodyBreakGlassError("missing authenticated public-custody enablement proof")
            accepted = accepted_public_signatures(
                public, payload, self._lab085_enablement_signatures
            )
            verify_public_threshold(public, payload, accepted)
            encoded = self.public_recovery_custody._encode_signatures(accepted)
            q.execute(
                "INSERT INTO provider_recovery_custody_enablement_proof VALUES(1,?,?)",
                (expected_digest, encoded),
            )
            return root, symmetric, public
        if row[0] != expected_digest:
            raise CustodyBreakGlassError("public-custody enablement digest mismatch")
        decoded = self.public_recovery_custody._decode_signatures(row[1])
        accepted = accepted_public_signatures(public, payload, decoded)
        verify_public_threshold(public, payload, accepted)
        if self.public_recovery_custody._encode_signatures(accepted) != row[1]:
            raise CustodyBreakGlassError("noncanonical public-custody enablement proof")
        return root, symmetric, public

    def _load_break_glass_enablement_locked(self, q):
        return self._verify_or_create_enablement_proof_locked(q)

    def break_glass_custody_payload(self, new_authority):
        require_canonical_authority(new_authority)
        q = self._con()
        try:
            q.execute("BEGIN")
            self._ensure_break_glass_schema_locked(q)
            old = self.rotation_authority.current_locked(q)
            symmetric = self.recovery_lifecycle.current_locked(q)
            public = self.public_recovery_custody.current_locked(q)
            compatibility = self.recovery.current_recovery_locked(q)
            if compatibility.authority_id != symmetric.recovery.authority_id:
                raise CustodyBreakGlassError("symmetric/LAB-084 recovery heads diverged")
            self._compatible(symmetric, public)
            legacy = self.recovery.make_intent(old, new_authority, compatibility)
            payload = custody_break_glass_payload(
                old, new_authority, public, compatibility, legacy.intent_digest
            )
            q.commit()
            return payload
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()

    def recover_rotation_authority(self, *args, **kwargs):
        raise CustodyBreakGlassError(
            "public custody is enabled; HMAC-only break-glass recovery is verification-only compatibility history"
        )

    def recover_rotation_authority_with_custody(
        self,
        new_authority,
        public_signatures,
        compatibility_recovery_signatures,
    ):
        require_canonical_authority(new_authority)
        q = self._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            self._reject_prepared_locked(q)
            self._ensure_break_glass_schema_locked(q)
            self._verify_custody_bindings_locked(q)
            self._verify_break_glass_custody_locked(q)

            old = self.rotation_authority.current_locked(q)
            symmetric = self.recovery_lifecycle.current_locked(q)
            public = self.public_recovery_custody.current_locked(q)
            compatibility = self.recovery.current_recovery_locked(q)
            if compatibility.authority_id != symmetric.recovery.authority_id:
                raise CustodyBreakGlassError("symmetric/LAB-084 recovery heads diverged")
            self._compatible(symmetric, public)

            legacy = self.recovery.make_intent(old, new_authority, compatibility)
            payload = custody_break_glass_payload(
                old, new_authority, public, compatibility, legacy.intent_digest
            )
            accepted = accepted_custody_break_glass_signatures(public, payload, public_signatures)

            out = self.recovery.recover_locked(
                q, new_authority, tuple(compatibility_recovery_signatures)
            )
            proof = (
                public.authority_id,
                symmetric.authority_id,
                legacy.intent_digest,
                custody_break_glass_digest(payload),
                self.public_recovery_custody._encode_signatures(accepted),
            )
            existing = q.execute(
                "SELECT public_authority_id,symmetric_authority_id,compatibility_intent_digest,"
                "custody_intent_digest,public_signatures_json FROM provider_rotation_recovery_custody_proofs "
                "WHERE new_rotation_authority_id=?",
                (new_authority.authority_id,),
            ).fetchone()
            if existing is not None and existing != proof:
                raise CustodyBreakGlassError("custody break-glass proof substitution")
            if existing is None:
                q.execute(
                    "INSERT INTO provider_rotation_recovery_custody_proofs VALUES(?,?,?,?,?,?)",
                    (new_authority.authority_id, *proof),
                )
            self._verify_break_glass_custody_locked(q)
            q.commit()
            return {
                **out,
                "public_recovery_authority_id": public.authority_id,
                "public_recovery_signers": tuple(sorted(s.signer_id for s in accepted)),
            }
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()

    def _verify_break_glass_custody_locked(self, q):
        self._ensure_break_glass_schema_locked(q)
        start_root, _, _ = self._load_break_glass_enablement_locked(q)
        recovery_rows = q.execute(
            "SELECT new_rotation_authority_id,old_rotation_authority_id,old_rotation_version,"
            "recovery_authority_id,recovery_generation,intent_digest "
            "FROM provider_rotation_recovery_transitions"
        ).fetchall()
        required = []
        for new_id, old_id, old_version, recovery_id, recovery_generation, legacy_digest in recovery_rows:
            proof = q.execute(
                "SELECT public_authority_id,symmetric_authority_id,compatibility_intent_digest,"
                "custody_intent_digest,public_signatures_json FROM provider_rotation_recovery_custody_proofs "
                "WHERE new_rotation_authority_id=?",
                (new_id,),
            ).fetchone()
            if old_version < start_root.version:
                if proof is not None:
                    raise CustodyBreakGlassError("public custody proof attached before enablement")
                continue
            required.append(new_id)
            if proof is None:
                raise CustodyBreakGlassError("post-enablement recovery lacks public custody proof")
            public = self.public_recovery_custody._load_authority_locked(q, proof[0])
            symmetric = self.recovery_lifecycle._load_recovery_locked(q, proof[1])
            self._compatible(symmetric, public)
            if (symmetric.recovery.authority_id, symmetric.recovery.generation) != (recovery_id, recovery_generation):
                raise CustodyBreakGlassError("custody proof recovery authority mismatch")
            binding = q.execute(
                "SELECT public_authority_id,version,generation FROM provider_recovery_custody_bindings "
                "WHERE symmetric_authority_id=?",
                (symmetric.authority_id,),
            ).fetchone()
            if binding != (public.authority_id, symmetric.version, symmetric.generation):
                raise CustodyBreakGlassError("custody proof authority is not historically bound")
            old = self.rotation_authority._load_locked(q, old_id)
            new = self.rotation_authority._load_locked(q, new_id)
            legacy = self.recovery.make_intent(old, new, symmetric.recovery)
            if legacy.intent_digest != legacy_digest or proof[2] != legacy_digest:
                raise CustodyBreakGlassError("custody proof legacy intent mismatch")
            payload = custody_break_glass_payload(
                old, new, public, symmetric.recovery, legacy.intent_digest
            )
            if proof[3] != custody_break_glass_digest(payload):
                raise CustodyBreakGlassError("custody break-glass intent digest mismatch")
            decoded = self.public_recovery_custody._decode_signatures(proof[4])
            accepted = accepted_public_signatures(public, payload, decoded)
            verify_public_threshold(public, payload, accepted)
            if self.public_recovery_custody._encode_signatures(accepted) != proof[4]:
                raise CustodyBreakGlassError("noncanonical public custody proof")
        count = q.execute("SELECT COUNT(*) FROM provider_rotation_recovery_custody_proofs").fetchone()[0]
        if count != len(required):
            raise CustodyBreakGlassError("orphan/duplicate custody break-glass proof")
        return True

    def verify_durable(self):
        if getattr(self, "_lab085_final_initializing", False):
            return SupportedPublicRecoveryAuthorityLifecycleLedger.verify_durable(self)
        if getattr(self, "_lab085_custody_initializing", False):
            return SupportedPublicRecoveryAuthorityLifecycleLedger.verify_durable(self)
        if not hasattr(self, "public_recovery_custody"):
            return SupportedPublicRecoveryAuthorityLifecycleLedger.verify_durable(self)

        guard = self._con()
        try:
            guard.execute("BEGIN IMMEDIATE")
            # Do not call the intermediate surface's public verify_durable here:
            # it now establishes its own write-excluding guard.  Re-run the
            # same authoritative layers directly while this final-surface guard
            # remains the single serialization boundary.
            SupportedRecoveryAuthorityLifecycleLedger.verify_durable(self)
            self.public_recovery_custody.verify_durable()
            self._verify_custody_bindings_locked(guard)
            self._verify_break_glass_custody_locked(guard)
            guard.commit()
            return True
        except:
            if guard.in_transaction:
                guard.rollback()
            raise
        finally:
            guard.close()
