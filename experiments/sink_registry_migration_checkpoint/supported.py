"""Supported LAB-078 migration surface.

The migration ceremony may only be composed with the final audited LAB-077
threshold-publication journal.  The lower-level ``RealMigrationCoordinator``
remains available in the experiment package for regression/audit work, but it is
not an authority-bearing supported entry point.
"""

from experiments.sink_registry_migration_checkpoint.integration import (
    RealMigrationCoordinator,
    RealMigrationError,
    RealMigrationNotEstablished,
    RealMigrationPending,
    RealMigrationProof,
    RealMigrationSubstitution,
    RealMigrationThreshold,
    sign_checkpoint,
)
from experiments.sink_registry_threshold_publication.supported import (
    ThresholdLifecycleRegistryBoundJournal,
)


class SupportedMigrationCoordinator(RealMigrationCoordinator):
    """Exact-type composition with the final audited LAB-077 journal.

    Supported migration never treats the idempotent INSERT/lookup path as proof
    of authority.  After either a fresh commit or an exact retry, re-run the
    mixed-history verifier so the stored checkpoint signatures and historical
    authority material are reauthenticated before reporting success.
    """

    def __init__(self, registry):
        if type(registry) is not ThresholdLifecycleRegistryBoundJournal:
            raise TypeError(
                "supported LAB-078 migration requires the exact final LAB-077 journal"
            )
        super().__init__(registry)

    def migrate(self, checkpoint, proof):
        checkpoint_id = super().migrate(checkpoint, proof)
        self.verify_mixed_history()
        return checkpoint_id


__all__ = [
    "RealMigrationError",
    "RealMigrationNotEstablished",
    "RealMigrationPending",
    "RealMigrationProof",
    "RealMigrationSubstitution",
    "RealMigrationThreshold",
    "SupportedMigrationCoordinator",
    "sign_checkpoint",
]
