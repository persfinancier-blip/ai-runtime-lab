from __future__ import annotations

import hashlib
import json

from experiments.provider_recovery_authority_lifecycle.asymmetric_custody import (
    accepted_public_signatures,
    verify_public_threshold,
)
from experiments.provider_recovery_authority_lifecycle.final_supported import (
    SupportedRecoveryCustodyLedger,
)
from experiments.provider_rotation_recovery.protocol import RecoveryAuthorityMismatch


class MigrationGuardError(RuntimeError):
    pass


class LegacyHistoryChanged(MigrationGuardError):
    pass


def _canon(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def _digest(value) -> str:
    raw = value if isinstance(value, (bytes, bytearray)) else _canon(value)
    return hashlib.sha256(raw).hexdigest()


def migration_payload(
    *, legacy_digest, cutoff_root, symmetric_authority_id, public_authority
):
    return {
        "kind": "provider-asymmetric-break-glass-boundary-v1",
        "legacy_digest": legacy_digest,
        "cutoff_root_id": cutoff_root.authority_id,
        "cutoff_root_version": cutoff_root.version,
        "cutoff_root_generation": cutoff_root.generation,
        "symmetric_authority_id": symmetric_authority_id,
        "public_authority_id": public_authority.authority_id,
        "public_authority_version": public_authority.version,
        "public_authority_generation": public_authority.generation,
    }


class AuthenticatedBreakGlassMigrationGuard:
    """Authenticated LAB-086 cutoff over the real LAB-084/LAB-085 SQLite state.

    This class deliberately does not become a second authority store. It reads
    the existing rotation/recovery/custody tables through the final LAB-085
    supported object, commits a threshold-signed cutoff, and installs a durable
    SQL guard that prevents an old LAB-085 worker from appending a new HMAC
    break-glass row after migration.
    """

    def __init__(self, ledger: SupportedRecoveryCustodyLedger):
        if type(ledger) is not SupportedRecoveryCustodyLedger:
            raise TypeError("exact final LAB-085 SupportedRecoveryCustodyLedger required")
        self.ledger = ledger
        q = ledger._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            self._ensure_schema_locked(q)
            self._verify_inherited_locked(q)
            self.verify_locked(q)
            q.commit()
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()

    @staticmethod
    def _ensure_schema_locked(q):
        q.execute(
            """CREATE TABLE IF NOT EXISTS provider_asymmetric_break_glass_boundary(
              singleton INTEGER PRIMARY KEY CHECK(singleton=1),
              legacy_digest TEXT NOT NULL,
              cutoff_root_id TEXT NOT NULL,
              cutoff_root_version INTEGER NOT NULL,
              cutoff_root_generation INTEGER NOT NULL,
              symmetric_authority_id TEXT NOT NULL,
              public_authority_id TEXT NOT NULL,
              public_authority_version INTEGER NOT NULL,
              public_authority_generation INTEGER NOT NULL,
              boundary_digest TEXT NOT NULL,
              signatures_json TEXT NOT NULL
            )"""
        )
        q.execute(
            """CREATE TRIGGER IF NOT EXISTS provider_asymmetric_break_glass_no_legacy_hmac
            BEFORE INSERT ON provider_rotation_recovery_transitions
            WHEN EXISTS(
              SELECT 1 FROM provider_asymmetric_break_glass_boundary WHERE singleton=1
            )
            BEGIN
              SELECT RAISE(ABORT, 'LAB-086 migration forbids new HMAC break-glass rows');
            END"""
        )

    def _provider_transitions_locked(self, q):
        enablement = self.ledger._load_enablement_locked(q)
        rows = q.execute(
            "SELECT t.provider_id,t.old_generation_id,t.new_generation_id,g.generation "
            "FROM asymmetric_provider_transitions t "
            "JOIN asymmetric_provider_generations g "
            "ON g.generation_id=t.new_generation_id "
            "WHERE g.generation>? ORDER BY g.generation",
            (enablement.start_provider_generation,),
        ).fetchall()
        return [(row[0], row[1], row[2]) for row in rows]

    def _verify_inherited_locked(self, q):
        """Re-run the inherited authority checks inside the caller's write lock.

        Calling ledger.verify_durable() from this transaction would attempt a
        nested BEGIN IMMEDIATE on another SQLite connection. Instead use the
        final LAB-085 internal verifiers while this single write-excluding
        interval remains authoritative.
        """
        self.ledger._verify_mixed_authority_history_locked(
            q, self._provider_transitions_locked(q)
        )
        self.ledger._verify_custody_bindings_locked(q)
        self.ledger._verify_break_glass_custody_locked(q)
        return True

    def _legacy_snapshot_locked(self, q, cutoff_version):
        rows = q.execute(
            "SELECT r.new_rotation_authority_id,r.old_rotation_authority_id,"
            "r.old_rotation_version,r.old_rotation_generation,r.recovery_authority_id,"
            "r.recovery_generation,r.intent_digest,r.signatures_json "
            "FROM provider_rotation_recovery_transitions r "
            "JOIN provider_rotation_authorities a "
            "ON a.authority_id=r.new_rotation_authority_id "
            "WHERE a.version<=? ORDER BY a.version",
            (cutoff_version,),
        ).fetchall()
        snapshot = []
        for row in rows:
            custody = q.execute(
                "SELECT public_authority_id,symmetric_authority_id,"
                "compatibility_intent_digest,custody_intent_digest,public_signatures_json "
                "FROM provider_rotation_recovery_custody_proofs "
                "WHERE new_rotation_authority_id=?",
                (row[0],),
            ).fetchone()
            snapshot.append(
                {
                    "hmac_recovery_row": list(row),
                    "public_custody_row": None if custody is None else list(custody),
                }
            )
        return snapshot

    def _legacy_digest_locked(self, q, cutoff_version):
        return _digest(self._legacy_snapshot_locked(q, cutoff_version))

    def _current_components_locked(self, q):
        root = self.ledger.rotation_authority.current_locked(q)
        symmetric = self.ledger.recovery_lifecycle.current_locked(q)
        compatibility = self.ledger.recovery.current_recovery_locked(q)
        public = self.ledger.public_recovery_custody.current_locked(q)
        if compatibility.authority_id != symmetric.recovery.authority_id:
            raise RecoveryAuthorityMismatch("LAB-084/LAB-085 recovery heads diverged")
        self.ledger._compatible(symmetric, public)
        return root, symmetric, public

    def payload(self):
        q = self.ledger._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            self._ensure_schema_locked(q)
            if q.execute(
                "SELECT 1 FROM provider_asymmetric_break_glass_boundary WHERE singleton=1"
            ).fetchone():
                raise MigrationGuardError("migration boundary already exists")
            self.ledger._reject_prepared_locked(q)
            self._verify_inherited_locked(q)
            root, symmetric, public = self._current_components_locked(q)
            payload = migration_payload(
                legacy_digest=self._legacy_digest_locked(q, root.version),
                cutoff_root=root,
                symmetric_authority_id=symmetric.authority_id,
                public_authority=public,
            )
            q.commit()
            return payload
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()

    def establish(self, public_signatures):
        q = self.ledger._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            self._ensure_schema_locked(q)
            if q.execute(
                "SELECT 1 FROM provider_asymmetric_break_glass_boundary WHERE singleton=1"
            ).fetchone():
                raise MigrationGuardError("migration boundary already exists")
            self.ledger._reject_prepared_locked(q)
            self._verify_inherited_locked(q)
            root, symmetric, public = self._current_components_locked(q)
            legacy_digest = self._legacy_digest_locked(q, root.version)
            payload = migration_payload(
                legacy_digest=legacy_digest,
                cutoff_root=root,
                symmetric_authority_id=symmetric.authority_id,
                public_authority=public,
            )
            accepted = accepted_public_signatures(
                public, payload, tuple(public_signatures)
            )
            verify_public_threshold(public, payload, accepted)
            boundary_digest = _digest(payload)
            q.execute(
                "INSERT INTO provider_asymmetric_break_glass_boundary "
                "VALUES(1,?,?,?,?,?,?,?,?,?,?)",
                (
                    legacy_digest,
                    root.authority_id,
                    root.version,
                    root.generation,
                    symmetric.authority_id,
                    public.authority_id,
                    public.version,
                    public.generation,
                    boundary_digest,
                    self.ledger.public_recovery_custody._encode_signatures(accepted),
                ),
            )
            self.verify_locked(q)
            q.commit()
            return boundary_digest
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()

    def verify_locked(self, q):
        row = q.execute(
            "SELECT legacy_digest,cutoff_root_id,cutoff_root_version,"
            "cutoff_root_generation,symmetric_authority_id,public_authority_id,"
            "public_authority_version,public_authority_generation,boundary_digest,"
            "signatures_json FROM provider_asymmetric_break_glass_boundary "
            "WHERE singleton=1"
        ).fetchone()
        if row is None:
            return None
        (
            legacy_digest,
            root_id,
            root_version,
            root_generation,
            symmetric_id,
            public_id,
            public_version,
            public_generation,
            boundary_digest,
            signatures_json,
        ) = row
        root = self.ledger.rotation_authority._load_locked(q, root_id)
        if (root.version, root.generation) != (root_version, root_generation):
            raise MigrationGuardError("boundary root metadata mismatch")
        symmetric = self.ledger.recovery_lifecycle._load_recovery_locked(q, symmetric_id)
        public = self.ledger.public_recovery_custody._load_authority_locked(q, public_id)
        if (public.version, public.generation) != (public_version, public_generation):
            raise MigrationGuardError("boundary public authority metadata mismatch")
        self.ledger._compatible(symmetric, public)
        binding = q.execute(
            "SELECT public_authority_id,version,generation "
            "FROM provider_recovery_custody_bindings WHERE symmetric_authority_id=?",
            (symmetric.authority_id,),
        ).fetchone()
        if binding != (public.authority_id, symmetric.version, symmetric.generation):
            raise MigrationGuardError("boundary recovery authority is not historically bound")
        payload = migration_payload(
            legacy_digest=legacy_digest,
            cutoff_root=root,
            symmetric_authority_id=symmetric_id,
            public_authority=public,
        )
        if _digest(payload) != boundary_digest:
            raise MigrationGuardError("boundary digest mismatch")
        decoded = self.ledger.public_recovery_custody._decode_signatures(signatures_json)
        accepted = accepted_public_signatures(public, payload, decoded)
        verify_public_threshold(public, payload, accepted)
        if self.ledger.public_recovery_custody._encode_signatures(accepted) != signatures_json:
            raise MigrationGuardError("noncanonical boundary signatures")
        observed = self._legacy_digest_locked(q, root.version)
        if observed != legacy_digest:
            raise LegacyHistoryChanged("legacy HMAC history changed after migration")
        return {
            "boundary_digest": boundary_digest,
            "legacy_digest": legacy_digest,
            "root_id": root.authority_id,
            "root_version": root.version,
            "public_authority_id": public.authority_id,
        }

    def verify(self):
        q = self.ledger._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            self._ensure_schema_locked(q)
            self._verify_inherited_locked(q)
            result = self.verify_locked(q)
            q.commit()
            return result
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()
