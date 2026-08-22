import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from experiments.anchor_threshold_root.protocol import RecoveryAuthority, RootState, key_id
from experiments.sink_capability_contract import protocol as cap
from experiments.sink_registry_migration_checkpoint.integration import RealMigrationCoordinator
from experiments.sink_registry_migration_checkpoint.supported import SupportedMigrationCoordinator
from experiments.sink_registry_migration_checkpoint.tests.test_real_integration import (
    RealIntegrationTests,
)
from experiments.sink_registry_authority_lifecycle.audit_fixes import (
    ConsistentDurableRegistryAuthority as DurableRegistryAuthority,
)
from experiments.sink_registry_threshold_publication.supported import (
    ThresholdLifecycleRegistryBoundJournal,
)
from experiments.transactional_broker_journal.capability import CapabilityBoundJournal
from experiments.transactional_broker_journal.protocol import TransactionalJournal


def _keys(prefix, count=3):
    raw = [f"{prefix}-{i}".encode() for i in range(count)]
    return raw, {key_id(k): k.hex() for k in raw}


class SupportedSurfaceTests(unittest.TestCase):
    def _registry(self, td):
        _, root_keys = _keys("root")
        root = RootState("sink-registry", 1, 1, 2, root_keys)
        _, recovery_keys = _keys("recovery", 4)
        recovery = RecoveryAuthority(1, 3, recovery_keys)
        probe = cap.ProbeAuthority(issuer_id="probe", key=b"probe", generation=1)
        path = Path(td) / "journal.db"
        journal = TransactionalJournal(path, 1)
        bound = CapabilityBoundJournal(journal, probe)
        lifecycle = DurableRegistryAuthority(path, root, recovery)
        return ThresholdLifecycleRegistryBoundJournal(bound, lifecycle)

    def _proof(self, registry, checkpoint):
        q = registry.journal._con()
        try:
            authority_id = q.execute(
                "SELECT authority_id FROM registry_authority_head WHERE singleton=1"
            ).fetchone()[0]
            body = json.loads(
                q.execute(
                    "SELECT body FROM registry_authorities WHERE authority_id=?",
                    (authority_id,),
                ).fetchone()[0]
            )
        finally:
            q.close()
        keys = [bytes.fromhex(value) for _, value in sorted(body["keys"].items())]
        return __import__(
            "experiments.sink_registry_migration_checkpoint.integration",
            fromlist=["RealMigrationProof", "sign_checkpoint"],
        ).RealMigrationProof(
            checkpoint.checkpoint_id,
            checkpoint.terminal_authority_id,
            checkpoint.terminal_authority_version,
            tuple(
                __import__(
                    "experiments.sink_registry_migration_checkpoint.integration",
                    fromlist=["sign_checkpoint"],
                ).sign_checkpoint(checkpoint, key)
                for key in keys[: body["threshold"]]
            ),
        )

    def test_exact_final_lab077_journal_is_accepted(self):
        with tempfile.TemporaryDirectory() as td:
            registry = self._registry(td)
            coordinator = SupportedMigrationCoordinator(registry)
            self.assertIs(coordinator.registry, registry)

    def test_subclass_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            registry = self._registry(td)

            class LessAudited(ThresholdLifecycleRegistryBoundJournal):
                pass

            fake = object.__new__(LessAudited)
            fake.__dict__.update(registry.__dict__)
            with self.assertRaises(TypeError):
                SupportedMigrationCoordinator(fake)

    def test_duck_typed_registry_is_rejected(self):
        class Duck:
            journal = object()
            lifecycle = object()

        with self.assertRaises(TypeError):
            SupportedMigrationCoordinator(Duck())

    def test_idempotent_retry_reauthenticates_historical_authority(self):
        with tempfile.TemporaryDirectory() as td:
            registry = self._registry(td)
            coordinator = SupportedMigrationCoordinator(registry)
            checkpoint = coordinator.preview(cutoff_sequence=0)
            proof = self._proof(registry, checkpoint)
            coordinator.migrate(checkpoint, proof)

            q = registry.journal._con()
            try:
                authority_id = q.execute(
                    "SELECT authority_id FROM registry_authority_head WHERE singleton=1"
                ).fetchone()[0]
                q.execute(
                    "UPDATE registry_authorities SET body='{}' WHERE authority_id=?",
                    (authority_id,),
                )
                q.commit()
            finally:
                q.close()

            with self.assertRaises(Exception):
                coordinator.migrate(checkpoint, proof)


class CrashAndRestartTests(RealIntegrationTests):
    def test_sql_abort_during_checkpoint_insert_leaves_no_partial_migration(self):
        checkpoint = self.coordinator.preview(cutoff_sequence=1)
        proof = self.proof(checkpoint)
        q = self.registry.journal._con()
        try:
            q.execute(
                "CREATE TRIGGER abort_migration BEFORE INSERT ON registry_migration_checkpoint_v2 "
                "BEGIN SELECT RAISE(ABORT, 'simulated crash before commit'); END"
            )
            q.commit()
        finally:
            q.close()

        with self.assertRaises(Exception):
            self.coordinator.migrate(checkpoint, proof)

        q = self.registry.journal._con()
        try:
            self.assertEqual(
                q.execute("SELECT COUNT(*) FROM registry_migration_checkpoint_v2").fetchone()[0],
                0,
            )
            q.execute("DROP TRIGGER abort_migration")
            q.commit()
        finally:
            q.close()

        self.coordinator.migrate(checkpoint, proof)
        self.assertTrue(self.coordinator.verify_mixed_history())

    def test_restart_after_first_threshold_successor(self):
        self.test_first_threshold_successor_after_migration()
        restarted = RealMigrationCoordinator(self.registry)
        self.assertTrue(restarted.verify_mixed_history())


if __name__ == "__main__":
    unittest.main()
