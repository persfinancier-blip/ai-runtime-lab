"""Supported LAB-079 composition surface.

The generic reference coordinator proves the numeric monotonic relationship.  The
supported surface adds the stronger cross-layer invariants required by LAB-079:
the external provider must authenticate the *exact migration request* that caused
(or previously caused) the anchored position, and an external action is forbidden
when the local migration binding and durable sequence watermark disagree.
"""
import hashlib
import json

from experiments.anchor_attestation.protocol import AttestedCatchup
from experiments.sink_registry_migration_checkpoint.supported import SupportedMigrationCoordinator
from .protocol import (
    BindingState,
    MigrationAnchorCoordinator,
    MigrationAnchorPending,
    MigrationAnchorSubstitution,
    MigrationAnchorUnavailable,
    RegistryAnchorState,
)


class StrictRegistryAnchorState(RegistryAnchorState):
    """Fail closed on local sequence/binding corruption before external effects.

    The reference state object establishes the schema.  The supported boundary
    additionally treats ``migration_anchor_meta.global_sequence`` and the binding
    row as one authority: an existing binding may be reused only when both name
    the same sequence.  Confirmation repeats the check so corruption/races cannot
    turn a mismatched local snapshot into CONFIRMED state.
    """

    @staticmethod
    def _sequence_locked(q):
        row = q.execute(
            "SELECT global_sequence FROM migration_anchor_meta WHERE singleton=1"
        ).fetchone()
        if row is None or type(row[0]) is not int or row[0] < 0:
            raise MigrationAnchorSubstitution("invalid migration anchor sequence watermark")
        return row[0]

    @staticmethod
    def _validate_state_shape(state):
        if type(state.sequence) is not int or state.sequence < 1:
            raise MigrationAnchorSubstitution("invalid migration binding sequence")
        if state.status == "PENDING":
            if state.anchor_receipt_ref is not None:
                raise MigrationAnchorSubstitution("pending binding carries a receipt")
        elif state.status == "CONFIRMED":
            ref = state.anchor_receipt_ref
            if (
                not isinstance(ref, str)
                or len(ref) != 64
                or any(c not in "0123456789abcdef" for c in ref)
            ):
                raise MigrationAnchorSubstitution("confirmed binding has invalid receipt")
        else:
            raise MigrationAnchorSubstitution("invalid migration binding status")
        return state

    def prepare(self, identity, *, provider_id: str, provider_generation: int):
        q = self._connect()
        try:
            q.execute("BEGIN IMMEDIATE")
            sequence = self._sequence_locked(q)
            existing = q.execute(
                "SELECT checkpoint_id,payload_digest,sequence,status,anchor_receipt_ref,"
                "provider_id,provider_generation FROM migration_anchor_binding WHERE singleton=1"
            ).fetchone()
            if existing is not None:
                state = self._validate_state_shape(BindingState(*existing))
                expected = (
                    identity.checkpoint_id,
                    identity.payload_digest,
                    provider_id,
                    provider_generation,
                )
                actual = (
                    state.checkpoint_id,
                    state.payload_digest,
                    state.provider_id,
                    state.provider_generation,
                )
                if actual != expected:
                    raise MigrationAnchorSubstitution(
                        "existing binding names different migration/provider"
                    )
                if state.sequence != sequence:
                    raise MigrationAnchorSubstitution(
                        "migration binding/meta sequence mismatch before anchor action"
                    )
                q.commit()
                return state

            next_sequence = sequence + 1
            changed = q.execute(
                "UPDATE migration_anchor_meta SET global_sequence=? "
                "WHERE singleton=1 AND global_sequence=?",
                (next_sequence, sequence),
            ).rowcount
            if changed != 1:
                raise MigrationAnchorSubstitution("migration sequence CAS lost")
            q.execute(
                "INSERT INTO migration_anchor_binding VALUES(1,?,?,?,'PENDING',NULL,?,?)",
                (
                    identity.checkpoint_id,
                    identity.payload_digest,
                    next_sequence,
                    provider_id,
                    provider_generation,
                ),
            )
            q.commit()
            return BindingState(
                identity.checkpoint_id,
                identity.payload_digest,
                next_sequence,
                "PENDING",
                None,
                provider_id,
                provider_generation,
            )
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()

    def confirm(self, expected: BindingState, receipt_ref: str):
        if (
            not isinstance(receipt_ref, str)
            or len(receipt_ref) != 64
            or any(c not in "0123456789abcdef" for c in receipt_ref)
        ):
            raise MigrationAnchorSubstitution("invalid authenticated anchor receipt binding")
        q = self._connect()
        try:
            q.execute("BEGIN IMMEDIATE")
            sequence = self._sequence_locked(q)
            row = q.execute(
                "SELECT checkpoint_id,payload_digest,sequence,status,anchor_receipt_ref,"
                "provider_id,provider_generation FROM migration_anchor_binding WHERE singleton=1"
            ).fetchone()
            if row is None:
                raise MigrationAnchorSubstitution("binding disappeared before confirmation")
            current = self._validate_state_shape(BindingState(*row))
            if current.sequence != sequence or expected.sequence != sequence:
                raise MigrationAnchorSubstitution(
                    "migration binding/meta sequence mismatch before confirmation"
                )
            if (
                current.checkpoint_id,
                current.payload_digest,
                current.sequence,
                current.provider_id,
                current.provider_generation,
            ) != (
                expected.checkpoint_id,
                expected.payload_digest,
                expected.sequence,
                expected.provider_id,
                expected.provider_generation,
            ):
                raise MigrationAnchorSubstitution("binding changed during anchor catch-up")
            if current.status == "CONFIRMED":
                if current.anchor_receipt_ref != receipt_ref:
                    raise MigrationAnchorSubstitution(
                        "confirmed binding receipt changed on retry"
                    )
                q.commit()
                return
            changed = q.execute(
                "UPDATE migration_anchor_binding SET status='CONFIRMED',anchor_receipt_ref=? "
                "WHERE singleton=1 AND sequence=? AND status='PENDING' AND anchor_receipt_ref IS NULL",
                (receipt_ref, expected.sequence),
            ).rowcount
            if changed != 1:
                raise MigrationAnchorSubstitution("migration confirmation CAS lost")
            q.commit()
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()


class SupportedAnchoredMigration(MigrationAnchorCoordinator):
    def __init__(self, migration, attested_catchup):
        if type(migration) is not SupportedMigrationCoordinator:
            raise TypeError("LAB-079 requires exact audited LAB-078 migration surface")
        if type(attested_catchup) is not AttestedCatchup:
            raise TypeError("LAB-079 requires exact LAB-036 authenticated anchor surface")
        super().__init__(migration, attested_catchup)
        self.state = StrictRegistryAnchorState(migration._con)

    @staticmethod
    def _request_id(binding):
        return f"migration-anchor:{binding.sequence}:{binding.checkpoint_id}"

    @staticmethod
    def _stable_receipt_binding(observation):
        """Stable identity derived only *after* authenticating the observation.

        LAB-036 challenges are intentionally fresh, so its per-observation
        ``receipt_ref`` changes across reauthentication.  Persist a stable digest
        of the authenticated provider/generation/position/request tuple instead.
        The digest is not treated as authentication by itself; every use first
        verifies a fresh signed provider observation.
        """
        payload = {
            "provider_id": observation.provider_id,
            "generation": observation.generation,
            "position": observation.position,
            "request_id": observation.request_id,
        }
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()

    def _exact_external_receipt(self, binding):
        """Reauthenticate the provider's durable result for this exact request."""
        challenge = self.attested.challenge()
        obs = self.attested.provider.reconcile_increment(
            challenge=challenge,
            request_id=self._request_id(binding),
        )
        if obs is None:
            raise MigrationAnchorPending(
                "anchor position has no authenticated result for this migration request"
            )
        verified = self.attested.verifier.verify(
            obs,
            expected_challenge=challenge,
            allowed_kinds={"RECONCILE"},
        )
        if (
            verified.position != binding.sequence
            or verified.request_id != self._request_id(binding)
        ):
            raise MigrationAnchorSubstitution(
                "authenticated anchor result names different migration position/request"
            )
        return self._stable_receipt_binding(verified)

    def catch_up(self, *, timeout_after_commit=False):
        binding = self.prepare()
        request_id = self._request_id(binding)
        try:
            # This performs the normal authenticated numeric catch-up. If the
            # provider is already at the target position LAB-036 may return a READ
            # receipt; that is deliberately *not* enough for this supported layer.
            self.attested.catch_up_one(
                db_sequence=binding.sequence,
                request_id=request_id,
                timeout_after_commit=timeout_after_commit,
            )
            exact_receipt = self._exact_external_receipt(binding)
        except MigrationAnchorPending:
            raise
        except Exception as exc:
            raise MigrationAnchorPending(str(exc)) from exc
        self.state.confirm(binding, exact_receipt)
        return self.state.load()

    def verify_restart(self):
        # First prove the local checkpoint/binding and the current authenticated
        # numeric anchor relation using the generic coordinator.
        super().verify_restart()
        binding = self.state.load()
        if binding is None:
            raise MigrationAnchorPending("migration anchor binding is missing")
        self.state._validate_state_shape(binding)
        try:
            exact_receipt = self._exact_external_receipt(binding)
        except MigrationAnchorPending:
            raise
        except Exception as exc:
            raise MigrationAnchorUnavailable(str(exc)) from exc
        if exact_receipt != binding.anchor_receipt_ref:
            raise MigrationAnchorSubstitution(
                "stored migration receipt does not match authenticated request-specific binding"
            )
        return True
