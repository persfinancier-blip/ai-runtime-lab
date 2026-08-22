import sqlite3
import tempfile
import unittest
from pathlib import Path

from experiments.anchor_attestation.protocol import (
    AttestationVerifier,
    AttestedCatchup,
    ProviderIdentity,
    SignedAnchorProvider,
)
from experiments.sink_capability_contract import protocol as cap
from experiments.sink_registry_migration_checkpoint.supported import (
    SupportedMigrationCoordinator,
)
from experiments.sink_registry_migration_checkpoint.tests.test_supported_and_crash import (
    SupportedSurfaceTests,
)
from experiments.sink_registry_threshold_publication.protocol import (
    make_envelope,
    publication_entry,
    sign_publication,
)
from experiments.transactional_broker_journal.protocol import Request

from experiments.migration_anchor_binding.protocol import (
    MigrationAnchorPending,
    MigrationRollbackDetected,
)
from experiments.migration_anchor_binding.supported import SupportedAnchoredMigration


class RealStackBindingTests(unittest.TestCase):
    @staticmethod
    def _attested(provider):
        verifier = AttestationVerifier(
            {(provider.provider_id, provider.generation): provider.key},
            ProviderIdentity(provider.provider_id, provider.generation),
        )
        return AttestedCatchup(provider, verifier)

    @staticmethod
    def _migration(td):
        helper = SupportedSurfaceTests()
        registry = helper._registry(td)
        migration = SupportedMigrationCoordinator(registry)
        checkpoint = migration.preview(cutoff_sequence=0)
        migration.migrate(checkpoint, helper._proof(registry, checkpoint))
        return registry, migration, checkpoint

    @staticmethod
    def _snapshot(db_path, snapshot_path):
        source = sqlite3.connect(db_path)
        target = sqlite3.connect(snapshot_path)
        try:
            source.backup(target)
        finally:
            target.close()
            source.close()

    @staticmethod
    def _restore(snapshot_path, db_path):
        source = sqlite3.connect(snapshot_path)
        target = sqlite3.connect(db_path)
        try:
            source.backup(target)
        finally:
            target.close()
            source.close()

    def test_real_supported_migration_confirm_restart_and_timeout_reconcile(self):
        with tempfile.TemporaryDirectory() as td:
            registry, migration, _ = self._migration(td)
            provider = SignedAnchorProvider(value=0)
            anchored = SupportedAnchoredMigration(migration, self._attested(provider))
            state = anchored.catch_up(timeout_after_commit=True)
            self.assertEqual((state.status, state.sequence), ("CONFIRMED", 1))
            self.assertEqual((provider.value, provider.increment_calls), (1, 1))

            restarted = SupportedAnchoredMigration(migration, self._attested(provider))
            self.assertTrue(restarted.verify_restart())
            again = restarted.catch_up()
            self.assertEqual(again.anchor_receipt_ref, state.anchor_receipt_ref)
            self.assertEqual(provider.increment_calls, 1)
            self.assertTrue(migration.verify_mixed_history())
            self.assertTrue(registry.journal.verify_durable())

    def test_unrelated_preexisting_anchor_position_does_not_confirm_real_migration(self):
        with tempfile.TemporaryDirectory() as td:
            _, migration, _ = self._migration(td)
            provider = SignedAnchorProvider(value=1)
            anchored = SupportedAnchoredMigration(migration, self._attested(provider))
            with self.assertRaises(MigrationAnchorPending):
                anchored.catch_up()
            state = anchored.state.load()
            self.assertEqual((state.sequence, state.status), (1, "PENDING"))
            self.assertEqual(provider.increment_calls, 0)

    def test_restoring_real_pre_migration_sqlite_snapshot_is_detected(self):
        with tempfile.TemporaryDirectory() as td:
            helper = SupportedSurfaceTests()
            registry = helper._registry(td)
            db_path = Path(registry.journal.path)
            snapshot = Path(td) / "pre-migration.sqlite"
            self._snapshot(db_path, snapshot)

            migration = SupportedMigrationCoordinator(registry)
            checkpoint = migration.preview(cutoff_sequence=0)
            migration.migrate(checkpoint, helper._proof(registry, checkpoint))
            provider = SignedAnchorProvider(value=0)
            anchored = SupportedAnchoredMigration(migration, self._attested(provider))
            anchored.catch_up()
            self.assertEqual(provider.value, 1)

            self._restore(snapshot, db_path)
            restored_migration = SupportedMigrationCoordinator(registry)
            restored = SupportedAnchoredMigration(
                restored_migration, self._attested(provider)
            )
            with self.assertRaises(MigrationRollbackDetected):
                restored.verify_restart()

    def test_first_real_threshold_successor_preserves_anchored_restart(self):
        with tempfile.TemporaryDirectory() as td:
            registry, migration, _ = self._migration(td)
            provider = SignedAnchorProvider(value=0)
            anchored = SupportedAnchoredMigration(migration, self._attested(provider))
            anchored.catch_up()

            root = registry.lifecycle.current()
            signer_keys = [
                bytes.fromhex(value)
                for _, value in sorted(root.keys.items())
            ][: root.threshold]
            entry = publication_entry(
                root,
                sink_id="sink-A",
                generation=1,
                adapter_digest="a" * 64,
                endpoint_origin="https://sink.example",
                operation_profile="write",
            )
            envelope = make_envelope(
                root,
                entry,
                tuple(sign_publication(entry, key) for key in signer_keys),
            )
            claim = cap.CapabilityClaim(
                "sink-A", 1, True, True, True, True, 3600, "lab079-real-stack"
            )
            probe_sink = cap.SimulatedSink(
                idempotent=True, request_bound=True, reconcile=True
            )
            capability = cap.VerifiedCapability(
                claim, registry.bound.verifier.attest(claim, probe_sink)
            )
            request = Request("post-migration", "task", "write", 1, "payload")
            status, _, plan, _ = registry.reserve(
                request, capability, envelope, now=1
            )
            self.assertEqual(status, "INTENT")
            self.assertEqual(plan.entry_digest, envelope.entry.entry_digest)
            registry.journal.confirm(request, "receipt:post-migration")

            self.assertTrue(migration.verify_mixed_history())
            restarted = SupportedAnchoredMigration(migration, self._attested(provider))
            self.assertTrue(restarted.verify_restart())


if __name__ == "__main__":
    unittest.main()
