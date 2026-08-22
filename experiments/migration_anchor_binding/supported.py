"""Supported LAB-079 composition surface."""
from experiments.anchor_attestation.protocol import AttestedCatchup
from experiments.sink_registry_migration_checkpoint.supported import SupportedMigrationCoordinator
from .protocol import MigrationAnchorCoordinator


class SupportedAnchoredMigration(MigrationAnchorCoordinator):
    def __init__(self, migration, attested_catchup):
        if type(migration) is not SupportedMigrationCoordinator:
            raise TypeError("LAB-079 requires exact audited LAB-078 migration surface")
        if type(attested_catchup) is not AttestedCatchup:
            raise TypeError("LAB-079 requires exact LAB-036 authenticated anchor surface")
        super().__init__(migration, attested_catchup)
