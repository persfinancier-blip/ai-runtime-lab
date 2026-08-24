from __future__ import annotations
from experiments.anchor_attestation.protocol import AttestedCatchup
from experiments.asymmetric_provider_history.protocol import GenerationSigner, InvalidTransition, TransitionProof
from experiments.asymmetric_provider_history.supported import SupportedAsymmetricHistoricalSharedAnchorLedger
from experiments.provider_recovery_authority_lifecycle.asymmetric_custody import PublicRecoveryAuthority, accepted_public_signatures, custody_rotation_payload, sha as custody_sha, verify_public_threshold
from experiments.provider_threshold_rotation.protocol import StaleAuthority
from experiments.provider_threshold_rotation.strict import require_canonical_authority
from .migration_guard import MigrationGuardError, _digest
from .strict_fence import assert_public_mutation_fence_locked, install_public_mutation_fence_locked, remove_public_mutation_fence_locked
from .suffix import AsymmetricBreakGlassError, PublicRecoveryRotationError, SupportedAsymmetricBreakGlassLedger, _accepted_root_signatures, asymmetric_break_glass_payload

class SupportedFencedAsymmetricBreakGlassLedger:
    """Final LAB-086 surface with transaction-scoped consequential mutation.

    After the authenticated cutoff, lower LAB-082/083/085/LAB-086 mutation entry
    points are denied by SQLite triggers. Durable proof rows are evidence only;
    they are never accepted as mutation capability.

    Every consequential writer follows one pattern under ``BEGIN IMMEDIATE``:
    verify the committed lower LAB-080/082 history while the writer slot is held,
    verify complete LAB-086 history, verify its own authorization, temporarily
    remove the deny fence inside the same transaction, mutate, restore/assert the
    fence, re-verify the affected current history, then commit. A rollback/crash
    rolls the temporary schema change back with the data changes.
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
    def _verify_lower_committed_history(ledger):
        # The caller already owns BEGIN IMMEDIATE on the authoritative database,
        # so no other writer can change the committed lower history while this
        # read verifier runs on its own connection.  This closes the gap where a
        # new root/public/provider successor could previously commit over corrupt
        # LAB-080/082 durable state that only a later restart would notice.
        return SupportedAsymmetricHistoricalSharedAnchorLedger.verify_durable(ledger)

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

    def rotate_rotation_authority(self, new_authority, old_signatures, new_signatures):
        require_canonical_authority(new_authority)
        ledger = self._ledger
        q = ledger._con()
        try:
            q.execute('BEGIN IMMEDIATE')
            ledger._reject_prepared_locked(q)
            ledger._ensure_asymmetric_schema_locked(q)
            self._install_fence_locked(q)
            self._verify_lower_committed_history(ledger)
            ledger._verify_lab086_locked(q)
            remove_public_mutation_fence_locked(q)
            try:
                out = ledger.rotation_authority.rotate_authority_locked(
                    q, new_authority, tuple(old_signatures), tuple(new_signatures)
                )
            finally:
                install_public_mutation_fence_locked(q)
            assert_public_mutation_fence_locked(q)
            ledger._verify_lab086_locked(q)
            q.commit()
            return out
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()

    def rotate_provider(
        self,
        new_signer: GenerationSigner,
        continuity_proof: TransitionProof,
        new_attested: AttestedCatchup,
        threshold_signatures,
    ):
        if type(new_signer) is not GenerationSigner:
            raise TypeError('exact LAB-082 GenerationSigner required')
        if type(new_attested) is not AttestedCatchup:
            raise TypeError('exact LAB-036 AttestedCatchup required')
        ledger = self._ledger
        new = new_signer.public
        expected = new_attested.verifier.expected
        if (expected.provider_id, expected.generation) != (new.provider_id, new.generation):
            raise InvalidTransition('new LAB-036 provider does not match Ed25519 generation')
        challenge = new_attested.challenge()
        observed = new_attested.authenticated_read(
            challenge=challenge,
            request_id=f'threshold-provider-rotation-read:{new.generation}',
        )
        q = ledger._con()
        try:
            q.execute('BEGIN IMMEDIATE')
            ledger._reject_prepared_locked(q)
            ledger._ensure_asymmetric_schema_locked(q)
            self._install_fence_locked(q)
            self._verify_lower_committed_history(ledger)
            ledger._verify_lab086_locked(q)
            reserved = q.execute(
                'SELECT reserved_position FROM shared_anchor_meta WHERE singleton=1'
            ).fetchone()[0]
            if observed.position != reserved:
                raise InvalidTransition('new provider position does not match durable ledger tail')
            old = ledger.provider_history._current_locked(q)
            remove_public_mutation_fence_locked(q)
            try:
                ledger.rotation_authority.authorize_provider_rotation_locked(
                    q,
                    provider_id=old.provider_id,
                    old_generation_id=old.generation_id,
                    new_generation_id=new.generation_id,
                    signatures=tuple(threshold_signatures),
                )
                ledger.provider_history._rotate_locked(q, new, continuity_proof)
            finally:
                install_public_mutation_fence_locked(q)
            assert_public_mutation_fence_locked(q)
            ledger.provider_history._verify_durable_locked(q)
            ledger._verify_lab086_locked(q)
            q.commit()
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()
        ledger.attested = new_attested
        ledger.signer = new_signer
        ledger._require_runtime_matches_durable_head()
        return new

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
            self._verify_lower_committed_history(ledger)
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

    def recover_rotation_authority_asymmetric(self, new_authority, public_signatures):
        require_canonical_authority(new_authority)
        ledger = self._ledger
        q = ledger._con()
        try:
            q.execute('BEGIN IMMEDIATE')
            ledger._reject_prepared_locked(q)
            ledger._ensure_asymmetric_schema_locked(q)
            self._install_fence_locked(q)
            self._verify_lower_committed_history(ledger)
            ledger._verify_lab086_locked(q)
            boundary = ledger.migration_guard.verify_locked(q)
            if boundary is None:
                raise MigrationGuardError('authenticated migration boundary required')
            old = ledger.rotation_authority.current_locked(q)
            public = ledger.public_recovery_custody.current_locked(q)
            ledger._require_successor(old, new_authority)
            payload = asymmetric_break_glass_payload(
                boundary_digest=boundary['boundary_digest'],
                old_root=old,
                new_root=new_authority,
                public_authority=public,
            )
            accepted = accepted_public_signatures(
                public, payload, tuple(public_signatures)
            )
            verify_public_threshold(public, payload, accepted)
            encoded = ledger.public_recovery_custody._encode_signatures(accepted)
            intent = _digest(payload)
            remove_public_mutation_fence_locked(q)
            try:
                ledger.rotation_authority._insert_authority_locked(q, new_authority)
                changed = q.execute(
                    'UPDATE provider_rotation_authority_head SET authority_id=?,version=?,generation=? '
                    'WHERE singleton=1 AND authority_id=? AND version=? AND generation=?',
                    (
                        new_authority.authority_id,
                        new_authority.version,
                        new_authority.generation,
                        old.authority_id,
                        old.version,
                        old.generation,
                    ),
                ).rowcount
                if changed != 1:
                    raise StaleAuthority('root head changed during asymmetric recovery')
                q.execute(
                    'INSERT INTO provider_asymmetric_break_glass_proofs VALUES(?,?,?,?,?,?,?,?,?,?)',
                    (
                        new_authority.authority_id,
                        old.authority_id,
                        old.version,
                        old.generation,
                        public.authority_id,
                        public.version,
                        public.generation,
                        boundary['boundary_digest'],
                        intent,
                        encoded,
                    ),
                )
            finally:
                install_public_mutation_fence_locked(q)
            assert_public_mutation_fence_locked(q)
            ledger._verify_lab086_locked(q)
            q.commit()
            return {
                'old_rotation_authority_id': old.authority_id,
                'new_rotation_authority_id': new_authority.authority_id,
                'public_recovery_authority_id': public.authority_id,
                'public_recovery_signers': tuple(sorted(s.signer_id for s in accepted)),
                'intent_digest': intent,
            }
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
