import sqlite3
import tempfile
import unittest
from pathlib import Path

from experiments.anchor_attestation.protocol import (
    AttestationVerifier,
    AttestedCatchup,
    ProviderIdentity,
)
from experiments.provider_generation_history.activation import FencedActivationProvider
from experiments.provider_generation_history.activation_schema_provenance import (
    ActivationSchemaMigrationRequired,
    ProvenancedHistoricalSharedAnchorLedger,
)
from experiments.provider_generation_history.protocol import (
    GenerationDescriptor,
    HistoricalVerificationError,
)
from experiments.provider_generation_history.supported import SupportedHistoricalSharedAnchorLedger


def descriptor(generation, key):
    return GenerationDescriptor("anchor-A", generation, key.hex())


def attested(provider, generation, key):
    verifier = AttestationVerifier(
        {("anchor-A", generation): key}, ProviderIdentity("anchor-A", generation)
    )
    return AttestedCatchup(provider, verifier)


class ActivationSchemaProvenanceTests(unittest.TestCase):
    def _fixture(self):
        td = tempfile.TemporaryDirectory()
        path = Path(td.name) / "shared.db"
        key = b"provider-key-1"
        provider = FencedActivationProvider("anchor-A", 1, key, value=0)
        return td, path, key, provider, descriptor(1, key)

    def test_legitimate_legacy_requires_explicit_migration_then_restarts(self):
        td, path, key, provider, g1 = self._fixture()
        with td:
            # Build the inherited pre-LAB-090 database, then remove only the
            # activation objects to model a legitimate legacy upgrade source.
            SupportedHistoricalSharedAnchorLedger(path, attested(provider, 1, key), g1)
            q = sqlite3.connect(path)
            try:
                q.execute("DROP TRIGGER block_intent_during_provider_activation")
                q.execute("DROP TABLE provider_generation_activations")
                q.commit()
            finally:
                q.close()

            with self.assertRaises(ActivationSchemaMigrationRequired):
                ProvenancedHistoricalSharedAnchorLedger(
                    path, attested(provider, 1, key), g1
                )

            migrated = ProvenancedHistoricalSharedAnchorLedger.migrate_activation_schema_v1(
                path, attested(provider, 1, key), g1
            )
            self.assertTrue(migrated.verify_activation_schema_provenance())

            restarted = ProvenancedHistoricalSharedAnchorLedger(
                path, attested(provider, 1, key), g1
            )
            self.assertTrue(restarted.verify_activation_schema_provenance())

    def test_completed_migration_then_table_deletion_fails_closed_without_repair(self):
        td, path, key, provider, g1 = self._fixture()
        with td:
            SupportedHistoricalSharedAnchorLedger(path, attested(provider, 1, key), g1)
            q = sqlite3.connect(path)
            try:
                q.execute("DROP TRIGGER block_intent_during_provider_activation")
                q.execute("DROP TABLE provider_generation_activations")
                q.commit()
            finally:
                q.close()

            ProvenancedHistoricalSharedAnchorLedger.migrate_activation_schema_v1(
                path, attested(provider, 1, key), g1
            )

            q = sqlite3.connect(path)
            try:
                q.execute("DROP TRIGGER block_intent_during_provider_activation")
                q.execute("DROP TABLE provider_generation_activations")
                q.commit()
            finally:
                q.close()

            with self.assertRaises(HistoricalVerificationError):
                ProvenancedHistoricalSharedAnchorLedger(
                    path, attested(provider, 1, key), g1
                )
            with self.assertRaises(HistoricalVerificationError):
                ProvenancedHistoricalSharedAnchorLedger.migrate_activation_schema_v1(
                    path, attested(provider, 1, key), g1
                )

            q = sqlite3.connect(path)
            try:
                relation = q.execute(
                    "SELECT type FROM sqlite_master WHERE name='provider_generation_activations'"
                ).fetchone()
                self.assertIsNone(relation)
            finally:
                q.close()

    def test_completed_migration_then_trigger_deletion_fails_closed_without_repair(self):
        td, path, key, provider, g1 = self._fixture()
        with td:
            SupportedHistoricalSharedAnchorLedger(path, attested(provider, 1, key), g1)
            q = sqlite3.connect(path)
            try:
                q.execute("DROP TRIGGER block_intent_during_provider_activation")
                q.execute("DROP TABLE provider_generation_activations")
                q.commit()
            finally:
                q.close()

            ProvenancedHistoricalSharedAnchorLedger.migrate_activation_schema_v1(
                path, attested(provider, 1, key), g1
            )

            q = sqlite3.connect(path)
            try:
                q.execute("DROP TRIGGER block_intent_during_provider_activation")
                q.commit()
            finally:
                q.close()

            with self.assertRaises(HistoricalVerificationError):
                ProvenancedHistoricalSharedAnchorLedger(
                    path, attested(provider, 1, key), g1
                )
            with self.assertRaises(HistoricalVerificationError):
                ProvenancedHistoricalSharedAnchorLedger.migrate_activation_schema_v1(
                    path, attested(provider, 1, key), g1
                )

            q = sqlite3.connect(path)
            try:
                relation = q.execute(
                    "SELECT type FROM sqlite_master WHERE name='block_intent_during_provider_activation'"
                ).fetchone()
                self.assertIsNone(relation)
            finally:
                q.close()

    def test_partial_unmarked_activation_schema_fails_closed_without_repair(self):
        td, path, key, provider, g1 = self._fixture()
        with td:
            SupportedHistoricalSharedAnchorLedger(path, attested(provider, 1, key), g1)
            q = sqlite3.connect(path)
            try:
                # Model an interrupted/corrupted legacy installation: the table
                # remains exact, but the trigger is absent and no provenance marker
                # has ever been written. This is ambiguous and must not auto-heal.
                q.execute("DROP TRIGGER block_intent_during_provider_activation")
                q.commit()
            finally:
                q.close()

            with self.assertRaises(HistoricalVerificationError):
                ProvenancedHistoricalSharedAnchorLedger(
                    path, attested(provider, 1, key), g1
                )
            with self.assertRaises(HistoricalVerificationError):
                ProvenancedHistoricalSharedAnchorLedger.migrate_activation_schema_v1(
                    path, attested(provider, 1, key), g1
                )

            q = sqlite3.connect(path)
            try:
                table = q.execute(
                    "SELECT type FROM sqlite_master WHERE name='provider_generation_activations'"
                ).fetchone()
                trigger = q.execute(
                    "SELECT type FROM sqlite_master WHERE name='block_intent_during_provider_activation'"
                ).fetchone()
                self.assertEqual(table, ("table",))
                self.assertIsNone(trigger)
            finally:
                q.close()


if __name__ == "__main__":
    unittest.main()
