from __future__ import annotations

from experiments.provider_recovery_authority_lifecycle.asymmetric_custody import (
    PublicRecoveryAuthority,
    accepted_public_signatures,
    custody_rotation_payload,
    sha as custody_sha,
    verify_public_threshold,
)

from .migration_guard import MigrationGuardError
from .suffix import (
    PublicRecoveryRotationError,
    SupportedAsymmetricBreakGlassLedger,
    _accepted_root_signatures,
)


class SupportedFencedAsymmetricBreakGlassLedger:
    """Final LAB-086 surface with post-cutoff SQL fencing.

    The LAB-085 public-custody object remains a useful historical verifier, but its
    old ``rotate()`` entry point is not sufficient authority after the LAB-086
    cutoff because it lacks current-root co-authorization.  This wrapper installs
    database-level guards so that even a stale caller holding the underlying
    custody object cannot commit a successor after cutoff unless the exact LAB-086
    root proof has already been persisted in the same transaction.

    The supported rotation path therefore uses proof-first ordering:

      validate old/new public quorum + current root quorum
      -> persist exact root proof
      -> mutate public authority/transition/head
      -> verify resulting history
      -> commit

    Any failure rolls back both the proof and the public-custody mutation.
    """

    def __init__(self, *args, **kwargs):
        self._ledger = SupportedAsymmetricBreakGlassLedger(*args, **kwargs)
        self._install_fence()
        self.verify_durable()

    @classmethod
    def from_existing(cls, ledger):
        if type(ledger) is not SupportedAsymmetricBreakGlassLedger:
            raise TypeError("exact LAB-086 SupportedAsymmetricBreakGlassLedger required")
        self = cls.__new__(cls)
        self._ledger = ledger
        self._install_fence()
        self.verify_durable()
        return self

    def __getattr__(self, name):
        return getattr(self._ledger, name)

    @staticmethod
    def _ensure_root_proof_table_locked(q):
        q.execute(
            """CREATE TABLE IF NOT EXISTS provider_asymmetric_recovery_public_root_proofs(
              new_public_authority_id TEXT PRIMARY KEY,old_public_authority_id TEXT NOT NULL,
              root_authority_id TEXT NOT NULL,root_version INTEGER NOT NULL,root_generation INTEGER NOT NULL,
              intent_digest TEXT NOT NULL,root_signatures_json TEXT NOT NULL)"""
        )

    @classmethod
    def _install_fence_locked(cls, q):
        cls._ensure_root_proof_table_locked(q)

        # A stale LAB-085 writer first tries to insert the successor authority.
        # After cutoff this is legal only if an exact proof has already been
        # inserted for the currently active public + normal-root predecessors.
        q.execute(
            """CREATE TRIGGER IF NOT EXISTS lab086_public_authority_requires_root_proof
            BEFORE INSERT ON provider_recovery_public_authorities
            WHEN EXISTS(
              SELECT 1 FROM provider_asymmetric_break_glass_boundary WHERE singleton=1
            ) AND NOT EXISTS(
              SELECT 1
              FROM provider_asymmetric_recovery_public_root_proofs p
              JOIN provider_recovery_public_head h ON h.singleton=1
              JOIN provider_rotation_authority_head r ON r.singleton=1
              WHERE p.new_public_authority_id=NEW.authority_id
                AND p.old_public_authority_id=h.authority_id
                AND p.root_authority_id=r.authority_id
                AND p.root_version=r.version
                AND p.root_generation=r.generation
            )
            BEGIN
              SELECT RAISE(ABORT,'LAB-086 public recovery successor requires current-root proof first');
            END"""
        )
        q.execute(
            """CREATE TRIGGER IF NOT EXISTS lab086_public_authority_is_immutable
            BEFORE UPDATE ON provider_recovery_public_authorities
            WHEN EXISTS(
              SELECT 1 FROM provider_asymmetric_break_glass_boundary WHERE singleton=1
            )
            BEGIN
              SELECT RAISE(ABORT,'LAB-086 public recovery authorities are immutable after cutoff');
            END"""
        )

        q.execute(
            """CREATE TRIGGER IF NOT EXISTS lab086_public_transition_requires_root_proof
            BEFORE INSERT ON provider_recovery_public_transitions
            WHEN EXISTS(
              SELECT 1 FROM provider_asymmetric_break_glass_boundary WHERE singleton=1
            ) AND NOT EXISTS(
              SELECT 1
              FROM provider_asymmetric_recovery_public_root_proofs p
              JOIN provider_recovery_public_head h ON h.singleton=1
              JOIN provider_rotation_authority_head r ON r.singleton=1
              WHERE p.new_public_authority_id=NEW.new_authority_id
                AND p.old_public_authority_id=NEW.old_authority_id
                AND p.old_public_authority_id=h.authority_id
                AND p.root_authority_id=NEW.root_authority_id
                AND p.root_authority_id=r.authority_id
                AND p.root_version=r.version
                AND p.root_generation=r.generation
            )
            BEGIN
              SELECT RAISE(ABORT,'LAB-086 public recovery transition requires exact root proof first');
            END"""
        )
        q.execute(
            """CREATE TRIGGER IF NOT EXISTS lab086_public_transition_is_immutable
            BEFORE UPDATE ON provider_recovery_public_transitions
            WHEN EXISTS(
              SELECT 1 FROM provider_asymmetric_break_glass_boundary WHERE singleton=1
            )
            BEGIN
              SELECT RAISE(ABORT,'LAB-086 public recovery transitions are immutable after cutoff');
            END"""
        )

        # The head update is the authoritative activation point.  Recheck the
        # exact predecessor and current normal-root binding immediately before it.
        q.execute(
            """CREATE TRIGGER IF NOT EXISTS lab086_public_head_requires_root_proof
            BEFORE UPDATE ON provider_recovery_public_head
            WHEN EXISTS(
              SELECT 1 FROM provider_asymmetric_break_glass_boundary WHERE singleton=1
            ) AND NOT EXISTS(
              SELECT 1
              FROM provider_asymmetric_recovery_public_root_proofs p
              JOIN provider_rotation_authority_head r ON r.singleton=1
              WHERE p.new_public_authority_id=NEW.authority_id
                AND p.old_public_authority_id=OLD.authority_id
                AND p.root_authority_id=r.authority_id
                AND p.root_version=r.version
                AND p.root_generation=r.generation
            )
            BEGIN
              SELECT RAISE(ABORT,'LAB-086 public recovery head requires exact current-root proof');
            END"""
        )

    def _install_fence(self):
        q = self._ledger._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            self._install_fence_locked(q)
            q.commit()
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()

    def rotate_public_recovery_authority(
        self,
        new_public,
        old_public_signatures,
        new_public_signatures,
        root_signatures,
    ):
        if type(new_public) is not PublicRecoveryAuthority:
            raise TypeError("exact PublicRecoveryAuthority required")
        ledger = self._ledger
        q = ledger._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            ledger._reject_prepared_locked(q)
            ledger._ensure_asymmetric_schema_locked(q)
            self._install_fence_locked(q)
            boundary = ledger.migration_guard.verify_locked(q)
            if boundary is None:
                raise MigrationGuardError("authenticated migration boundary required")

            old = ledger.public_recovery_custody.current_locked(q)
            root = ledger.rotation_authority.current_locked(q)
            new_public.validate()
            if (
                new_public.name != old.name
                or new_public.version != old.version + 1
                or new_public.generation != old.generation + 1
            ):
                raise PublicRecoveryRotationError(
                    "public recovery authority must advance exactly one"
                )

            payload = custody_rotation_payload(old, new_public, root.authority_id)
            old_valid = accepted_public_signatures(
                old, payload, tuple(old_public_signatures)
            )
            new_valid = accepted_public_signatures(
                new_public, payload, tuple(new_public_signatures)
            )
            verify_public_threshold(old, payload, old_valid)
            verify_public_threshold(new_public, payload, new_valid)
            root_valid = _accepted_root_signatures(
                root, payload, tuple(root_signatures)
            )

            proof = (
                old.authority_id,
                root.authority_id,
                root.version,
                root.generation,
                custody_sha(payload),
                ledger.rotation_authority._encode_signatures(root_valid),
            )
            existing = q.execute(
                "SELECT old_public_authority_id,root_authority_id,root_version,root_generation,"
                "intent_digest,root_signatures_json "
                "FROM provider_asymmetric_recovery_public_root_proofs "
                "WHERE new_public_authority_id=?",
                (new_public.authority_id,),
            ).fetchone()
            if existing is not None and existing != proof:
                raise PublicRecoveryRotationError(
                    "public recovery root proof substitution"
                )
            if existing is None:
                q.execute(
                    "INSERT INTO provider_asymmetric_recovery_public_root_proofs VALUES(?,?,?,?,?,?,?)",
                    (new_public.authority_id, *proof),
                )

            # The trigger permits this old LAB-085 primitive only because the
            # exact co-authorization proof now exists inside this transaction.
            ledger.public_recovery_custody.rotate_locked(
                q, new_public, root.authority_id, old_valid, new_valid
            )
            ledger._verify_public_recovery_rotations_locked(q, boundary)
            q.commit()
            return {
                "old_public_authority_id": old.authority_id,
                "new_public_authority_id": new_public.authority_id,
                "root_authority_id": root.authority_id,
                "root_signers": tuple(sorted(s.signer_id for s in root_valid)),
            }
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()

    def verify_durable(self):
        self._ledger.verify_durable()
        q = self._ledger._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            self._install_fence_locked(q)
            boundary = self._ledger.migration_guard.verify_locked(q)
            if boundary is not None:
                self._ledger._verify_public_recovery_rotations_locked(q, boundary)
            q.commit()
            return True
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()
