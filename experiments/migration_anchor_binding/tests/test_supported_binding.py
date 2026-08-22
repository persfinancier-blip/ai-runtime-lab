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
from experiments.migration_anchor_binding.protocol import (
    MigrationAnchorCoordinator,
    MigrationAnchorPending,
    MigrationAnchorSubstitution,
)
from experiments.migration_anchor_binding.supported import SupportedAnchoredMigration
from experiments.migration_anchor_binding.tests.test_protocol import FakeMigration


class SupportedBindingTests(unittest.TestCase):
    @staticmethod
    def attested(provider):
        verifier = AttestationVerifier(
            {(provider.provider_id, provider.generation): provider.key},
            ProviderIdentity(provider.provider_id, provider.generation),
        )
        return AttestedCatchup(provider, verifier)

    @staticmethod
    def unit_surface(migration, attested):
        # Bypass only the exact LAB-078 constructor guard so these focused tests
        # exercise the supported request-binding methods against the small SQL
        # migration fixture.  The separate real-integration gate exercises the
        # actual LAB-078/LAB-077 stack.
        obj = object.__new__(SupportedAnchoredMigration)
        MigrationAnchorCoordinator.__init__(obj, migration, attested)
        return obj

    def test_unrelated_existing_anchor_position_is_not_confirmation(self):
        with tempfile.TemporaryDirectory() as td:
            migration = FakeMigration(Path(td) / "db.sqlite")
            migration.establish()
            # Position 1 was reached by something else; there is deliberately no
            # provider result for the migration-specific request ID.
            provider = SignedAnchorProvider(value=1)
            coordinator = self.unit_surface(migration, self.attested(provider))
            with self.assertRaises(MigrationAnchorPending):
                coordinator.catch_up()
            state = coordinator.state.load()
            self.assertEqual((state.sequence, state.status), (1, "PENDING"))

    def test_exact_request_increment_confirms_and_survives_verifier_restart(self):
        with tempfile.TemporaryDirectory() as td:
            migration = FakeMigration(Path(td) / "db.sqlite")
            migration.establish()
            provider = SignedAnchorProvider(value=0)
            first = self.unit_surface(migration, self.attested(provider))
            state = first.catch_up()
            self.assertEqual((state.sequence, state.status, provider.value), (1, "CONFIRMED", 1))
            self.assertTrue(first.verify_restart())

            # New verifier instance models restart while the external provider's
            # request-result record remains durable.
            restarted = self.unit_surface(migration, self.attested(provider))
            self.assertTrue(restarted.verify_restart())

    def test_tampered_local_receipt_is_rejected_even_when_counter_matches(self):
        with tempfile.TemporaryDirectory() as td:
            migration = FakeMigration(Path(td) / "db.sqlite")
            migration.establish()
            provider = SignedAnchorProvider(value=0)
            coordinator = self.unit_surface(migration, self.attested(provider))
            coordinator.catch_up()
            q = sqlite3.connect(migration.path)
            q.execute(
                "UPDATE migration_anchor_binding SET anchor_receipt_ref=? WHERE singleton=1",
                ("0" * 64,),
            )
            q.commit()
            q.close()
            restarted = self.unit_surface(migration, self.attested(provider))
            with self.assertRaises(MigrationAnchorSubstitution):
                restarted.verify_restart()

    def test_timeout_after_commit_still_binds_exact_request_once(self):
        with tempfile.TemporaryDirectory() as td:
            migration = FakeMigration(Path(td) / "db.sqlite")
            migration.establish()
            provider = SignedAnchorProvider(value=0)
            coordinator = self.unit_surface(migration, self.attested(provider))
            state = coordinator.catch_up(timeout_after_commit=True)
            self.assertEqual((state.status, provider.value, provider.increment_calls), ("CONFIRMED", 1, 1))
            again = coordinator.catch_up()
            self.assertEqual(again.anchor_receipt_ref, state.anchor_receipt_ref)
            self.assertEqual(provider.increment_calls, 1)


if __name__ == "__main__":
    unittest.main()
