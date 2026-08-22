import tempfile
import unittest
from pathlib import Path

from experiments.anchor_attestation.protocol import (
    AttestationVerifier,
    AttestedCatchup,
    ProviderIdentity,
    SignedAnchorProvider,
)
from experiments.migration_anchor_binding.protocol import MigrationAnchorSubstitution
from experiments.migration_anchor_binding.supported import SupportedAnchoredMigration
from experiments.migration_anchor_binding.tests.test_protocol import FakeMigration
from experiments.sink_registry_migration_checkpoint.supported import SupportedMigrationCoordinator


class SequenceFencingTests(unittest.TestCase):
    @staticmethod
    def _attested(provider):
        verifier = AttestationVerifier(
            {(provider.provider_id, provider.generation): provider.key},
            ProviderIdentity(provider.provider_id, provider.generation),
        )
        return AttestedCatchup(provider, verifier)

    @staticmethod
    def _supported_fixture(migration, attested):
        # This focused corruption test uses the tiny migration fixture but keeps
        # the exact supported state/catch-up code.  Real-stack composition is
        # covered separately by test_real_stack.py.
        obj = object.__new__(SupportedAnchoredMigration)
        obj.migration = migration
        obj.attested = attested
        from experiments.migration_anchor_binding.supported import StrictRegistryAnchorState

        obj.state = StrictRegistryAnchorState(migration._con)
        return obj

    def test_meta_binding_sequence_mismatch_blocks_provider_before_increment(self):
        with tempfile.TemporaryDirectory() as td:
            migration = FakeMigration(Path(td) / "db.sqlite")
            migration.establish()
            provider = SignedAnchorProvider(value=0)
            anchored = self._supported_fixture(migration, self._attested(provider))
            anchored.prepare()

            q = migration._con()
            q.execute("UPDATE migration_anchor_meta SET global_sequence=2 WHERE singleton=1")
            q.commit()
            q.close()

            with self.assertRaises(MigrationAnchorSubstitution):
                anchored.catch_up()
            self.assertEqual(provider.value, 0)
            self.assertEqual(provider.increment_calls, 0)

    def test_sequence_change_after_external_commit_blocks_local_confirmation(self):
        with tempfile.TemporaryDirectory() as td:
            migration = FakeMigration(Path(td) / "db.sqlite")
            migration.establish()
            provider = SignedAnchorProvider(value=0)
            anchored = self._supported_fixture(migration, self._attested(provider))
            binding = anchored.prepare()

            # Model corruption/race after provider commit but before local confirm.
            request_id = anchored._request_id(binding)
            challenge = anchored.attested.challenge()
            observation = provider.increment(
                expected=0, challenge=challenge, request_id=request_id
            )
            verified = anchored.attested.verifier.verify(
                observation,
                expected_challenge=challenge,
                allowed_kinds={"INCREMENT"},
            )
            receipt = anchored._stable_receipt_binding(verified)
            q = migration._con()
            q.execute("UPDATE migration_anchor_meta SET global_sequence=2 WHERE singleton=1")
            q.commit()
            q.close()

            with self.assertRaises(MigrationAnchorSubstitution):
                anchored.state.confirm(binding, receipt)
            self.assertEqual(anchored.state.load().status, "PENDING")


if __name__ == "__main__":
    unittest.main()
