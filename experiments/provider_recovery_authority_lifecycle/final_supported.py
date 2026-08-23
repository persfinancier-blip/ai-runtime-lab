from __future__ import annotations

from .public_custody_supported import SupportedPublicRecoveryAuthorityLifecycleLedger


class SupportedRecoveryCustodyLedger(SupportedPublicRecoveryAuthorityLifecycleLedger):
    """Final LAB-085 supported surface.

    A write-excluding transaction is held across the inherited symmetric history,
    public custody history, and binding verification. This prevents a concurrent
    authority writer from changing transition bytes between otherwise-correct
    verification passes that would have observed different SQLite snapshots.
    """

    def verify_durable(self):
        if getattr(self, "_lab085_custody_initializing", False):
            return SupportedPublicRecoveryAuthorityLifecycleLedger.verify_durable(self)
        if not hasattr(self, "public_recovery_custody"):
            return SupportedPublicRecoveryAuthorityLifecycleLedger.verify_durable(self)

        guard = self._con()
        try:
            guard.execute("BEGIN IMMEDIATE")
            # The inherited verifier opens read-only connections. BEGIN IMMEDIATE
            # prevents any other writer from committing while those reads and the
            # final binding check are in progress, so they describe one stable
            # authoritative history rather than a mix of snapshots.
            SupportedPublicRecoveryAuthorityLifecycleLedger.verify_durable(self)
            self._verify_custody_bindings_locked(guard)
            guard.commit()
            return True
        except:
            if guard.in_transaction:
                guard.rollback()
            raise
        finally:
            guard.close()
