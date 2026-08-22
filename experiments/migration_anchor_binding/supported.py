"""Supported LAB-079 composition surface.

The generic reference coordinator proves the numeric monotonic relationship.  The
supported surface adds the stronger cross-layer invariant required by LAB-079:
the external provider must also authenticate that the *exact migration request*
caused (or previously caused) the anchored position.  A plain authenticated READ
of the same numeric position is not sufficient evidence of checkpoint binding.
"""
from experiments.anchor_attestation.protocol import AttestedCatchup, receipt_ref
from experiments.sink_registry_migration_checkpoint.supported import SupportedMigrationCoordinator
from .protocol import (
    MigrationAnchorCoordinator,
    MigrationAnchorPending,
    MigrationAnchorSubstitution,
    MigrationAnchorUnavailable,
)


class SupportedAnchoredMigration(MigrationAnchorCoordinator):
    def __init__(self, migration, attested_catchup):
        if type(migration) is not SupportedMigrationCoordinator:
            raise TypeError("LAB-079 requires exact audited LAB-078 migration surface")
        if type(attested_catchup) is not AttestedCatchup:
            raise TypeError("LAB-079 requires exact LAB-036 authenticated anchor surface")
        super().__init__(migration, attested_catchup)

    @staticmethod
    def _request_id(binding):
        return f"migration-anchor:{binding.sequence}:{binding.checkpoint_id}"

    def _exact_external_receipt(self, binding):
        """Reauthenticate the provider's durable result for this exact request.

        LAB-036's provider reconciliation record is request-bound and signed.  It
        is therefore stronger than observing only that the global counter happens
        to equal ``binding.sequence``.  The fresh challenge prevents replay of an
        old observation while ``request_id`` binds the observation to the exact
        migration checkpoint used for the increment.
        """
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
        return receipt_ref(verified)

    def catch_up(self, *, timeout_after_commit=False):
        binding = self.prepare()
        request_id = self._request_id(binding)
        try:
            # This performs the normal authenticated numeric catch-up.  If the
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
        try:
            exact_receipt = self._exact_external_receipt(binding)
        except MigrationAnchorPending:
            raise
        except Exception as exc:
            raise MigrationAnchorUnavailable(str(exc)) from exc
        if exact_receipt != binding.anchor_receipt_ref:
            raise MigrationAnchorSubstitution(
                "stored migration receipt does not match authenticated request-specific receipt"
            )
        return True
