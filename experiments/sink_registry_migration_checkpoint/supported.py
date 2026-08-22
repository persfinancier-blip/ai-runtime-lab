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
    """Exact-type composition with the final audited LAB-077 journal."""

    def __init__(self, registry):
        if type(registry) is not ThresholdLifecycleRegistryBoundJournal:
            raise TypeError(
                "supported LAB-078 migration requires the exact final LAB-077 journal"
            )
        super().__init__(registry)


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
