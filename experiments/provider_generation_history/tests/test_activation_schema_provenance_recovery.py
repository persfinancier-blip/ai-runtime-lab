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
    _completion_intent,
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


class ActivationSchemaProvenanceRecoveryTests(unittest.TestCase):
    def _fixture(self):
        td = tempfile.TemporaryDirectory()
        path = Path(td.name) / "shared.db"
        key = b"provider-key-1"
        provider = FencedActivationProvider("anchor-A", 1, key, value=0)
        return td, path, key, provider, descriptor(1, key)

    def test_unmarked_mismatched_trigger_fails_closed_without_repair(self):
        td, path, key, provider, g1 = self._fixture()
        with td:
            SupportedHistoricalSharedAnchorLedger(path, attested(provider, 1, key), g1)
            q = sqlite3.connect(path)
            try:
                q.execute("DROP TRIGGER block_intent_during_provider_activation")
                q.execute(
                    "CREATE TRIGGER block_intent_during_provider_activation "
                    "BEFORE INSERT ON shared_anchor_intents BEGIN "
                    "SELECT RAISE(ABORT,'mismatched activation trigger'); END"
                )
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
                sql = q.execute(
                    "SELECT sql FROM sqlite_master WHERE type='trigger' AND name=?",
                    ("block_intent_during_provider_activation",),
                ).fetchone()[0]
                self.assertIn("mismatched activation trigger", sql)
            finally:
                q.close()

    def test_completed_migration_then_mismatched_trigger_fails_closed_without_repair(self):
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
                q.execute(
                    "CREATE TRIGGER block_intent_during_provider_activation "
                    "BEFORE INSERT ON shared_anchor_intents BEGIN "
                    "SELECT RAISE(ABORT,'post-completion mismatch'); END"
                )
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
                sql = q.execute(
                    "SELECT sql FROM sqlite_master WHERE type='trigger' AND name=?",
                    ("block_intent_during_provider_activation",),
                ).fetchone()[0]
                self.assertIn("post-completion mismatch", sql)
            finally:
                q.close()

    def test_prepared_completion_marker_recovers_only_through_explicit_migration(self):
        td, path, key, provider, g1 = self._fixture()
        with td:
            legacy = SupportedHistoricalSharedAnchorLedger(
                path, attested(provider, 1, key), g1
            )
            prepared = legacy.reserve(_completion_intent())
            self.assertEqual(prepared.status, "PREPARED")

            with self.assertRaises(ActivationSchemaMigrationRequired):
                ProvenancedHistoricalSharedAnchorLedger(
                    path, attested(provider, 1, key), g1
                )

            q = sqlite3.connect(path)
            try:
                status = q.execute(
                    "SELECT status FROM shared_anchor_intents WHERE intent_id=?",
                    (_completion_intent().intent_id,),
                ).fetchone()[0]
                self.assertEqual(status, "PREPARED")
            finally:
                q.close()

            migrated = ProvenancedHistoricalSharedAnchorLedger.migrate_activation_schema_v1(
                path, attested(provider, 1, key), g1
            )
            self.assertTrue(migrated.verify_activation_schema_provenance())

            q = sqlite3.connect(path)
            try:
                status = q.execute(
                    "SELECT status FROM shared_anchor_intents WHERE intent_id=?",
                    (_completion_intent().intent_id,),
                ).fetchone()[0]
                self.assertEqual(status, "CONFIRMED")
            finally:
                q.close()


if __name__ == "__main__":
    unittest.main()
