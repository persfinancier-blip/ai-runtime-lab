from __future__ import annotations
from experiments.asymmetric_provider_history.supported import SupportedAsymmetricHistoricalSharedAnchorLedger
from experiments.provider_recovery_authority_lifecycle.asymmetric_custody import PublicRecoveryAuthority, accepted_public_signatures, custody_rotation_payload, sha as custody_sha, verify_public_threshold
from .migration_guard import MigrationGuardError
from .strict_fence import assert_public_mutation_fence_locked, install_public_mutation_fence_locked, remove_public_mutation_fence_locked
from .suffix import PublicRecoveryRotationError, SupportedAsymmetricBreakGlassLedger, _accepted_root_signatures

class SupportedFencedAsymmetricBreakGlassLedger:
    """Final LAB-086 surface with transaction-scoped public-recovery mutation.

    After the authenticated cutoff, underlying LAB-085/LAB-086 writers are denied
    by unconditional SQLite triggers. Durable root-proof rows are evidence only;
    they are never accepted as mutation capability.

    The only supported public-recovery rotation path is:

      BEGIN IMMEDIATE
      -> verify boundary + complete LAB-086 history + old/new public quorum + current root quorum
      -> persist/validate exact historical proof
      -> transactionally remove deny triggers
      -> mutate authority/transition/head
      -> reinstall + verify deny triggers
      -> re-verify complete LAB-086 history
      -> COMMIT

    Because SQLite schema DDL participates in the transaction, any exception or
    crash before commit rolls the temporary trigger removal back together with the
    data changes. No durable boolean/token is introduced as authority.
    """

    def __init__(self, *args, **kwargs):
        self._ledger = SupportedAsymmetricBreakGlassLedger(*args, **kwargs)
        self._install_fence()
        self.verify_durable()

    @classmethod
    def from_existing(cls, ledger):
        if type(ledger) is not SupportedAsymmetricBreakGlassLedger:
            raise TypeError('exact LAB-086 SupportedAsymmetricBreakGlassLedger required')
        self = cls.__new__(cls)
        self._ledger = ledger
        self._install_fence()
        self.verify_durable()
        return self

    def __getattr__(self, name):
        return getattr(self._ledger, name)

    @staticmethod
    def _ensure_root_proof_table_locked(q):
        q.execute('CREATE TABLE IF NOT EXISTS provider_asymmetric_recovery_public_root_proofs(\n              new_public_authority_id TEXT PRIMARY KEY,old_public_authority_id TEXT NOT NULL,\n              root_authority_id TEXT NOT NULL,root_version INTEGER NOT NULL,root_generation INTEGER NOT NULL,\n              intent_digest TEXT NOT NULL,root_signatures_json TEXT NOT NULL)')

    @classmethod
    def _install_fence_locked(cls, q):
        cls._ensure_root_proof_table_locked(q)
        install_public_mutation_fence_locked(q)
        assert_public_mutation_fence_locked(q)

    def _install_fence(self):
        q = self._ledger._con()
        try:
            q.execute('BEGIN IMMEDIATE')
            self._install_fence_locked(q)
            q.commit()
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()

    def rotate_public_recovery_authority(self, new_public, old_public_signatures, new_public_signatures, root_signatures):
        if type(new_public) is not PublicRecoveryAuthority:
            raise TypeError('exact PublicRecoveryAuthority required')
        ledger = self._ledger
        q = ledger._con()
        try:
            q.execute('BEGIN IMMEDIATE')
            ledger._reject_prepared_locked(q)
            ledger._ensure_asymmetric_schema_locked(q)
            self._install_fence_locked(q)
            boundary = ledger.migration_guard.verify_locked(q)
            if boundary is None:
                raise MigrationGuardError('authenticated migration boundary required')
            ledger._verify_lab086_locked(q)
            old = ledger.public_recovery_custody.current_locked(q)
            root = ledger.rotation_authority.current_locked(q)
            new_public.validate()
            if new_public.name != old.name or new_public.version != old.version + 1 or new_public.generation != old.generation + 1:
                raise PublicRecoveryRotationError('public recovery authority must advance exactly one')
            payload = custody_rotation_payload(old, new_public, root.authority_id)
            old_valid = accepted_public_signatures(old, payload, tuple(old_public_signatures))
            new_valid = accepted_public_signatures(new_public, payload, tuple(new_public_signatures))
            verify_public_threshold(old, payload, old_valid)
            verify_public_threshold(new_public, payload, new_valid)
            root_valid = _accepted_root_signatures(root, payload, tuple(root_signatures))
            proof = (old.authority_id, root.authority_id, root.version, root.generation, custody_sha(payload), ledger.rotation_authority._encode_signatures(root_valid))
            existing = q.execute('SELECT old_public_authority_id,root_authority_id,root_version,root_generation,intent_digest,root_signatures_json FROM provider_asymmetric_recovery_public_root_proofs WHERE new_public_authority_id=?', (new_public.authority_id,)).fetchone()
            if existing is not None and existing != proof:
                raise PublicRecoveryRotationError('public recovery root proof substitution')
            if existing is None:
                q.execute('INSERT INTO provider_asymmetric_recovery_public_root_proofs VALUES(?,?,?,?,?,?,?)', (new_public.authority_id, *proof))
            remove_public_mutation_fence_locked(q)
            try:
                ledger.public_recovery_custody.rotate_locked(q, new_public, root.authority_id, old_valid, new_valid)
            finally:
                install_public_mutation_fence_locked(q)
            assert_public_mutation_fence_locked(q)
            ledger._verify_lab086_locked(q)
            q.commit()
            return {'old_public_authority_id': old.authority_id, 'new_public_authority_id': new_public.authority_id, 'root_authority_id': root.authority_id, 'root_signers': tuple(sorted((s.signer_id for s in root_valid)))}
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()

    def verify_durable(self):
        ledger = self._ledger
        q = ledger._con()
        try:
            q.execute('BEGIN IMMEDIATE')
            self._install_fence_locked(q)
            SupportedAsymmetricHistoricalSharedAnchorLedger.verify_durable(ledger)
            ledger.public_recovery_custody.verify_durable()
            ledger._verify_lab086_locked(q)
            assert_public_mutation_fence_locked(q)
            q.commit()
            return True
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()
