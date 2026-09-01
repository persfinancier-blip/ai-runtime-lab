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
    ProvenancedHistoricalSharedAnchorLedger,
    _install_and_reserve_prepared,
)
from experiments.provider_generation_history.protocol import GenerationDescriptor
from experiments.provider_generation_history.supported import SupportedHistoricalSharedAnchorLedger
from experiments.shared_anchor_intent_ledger.protocol import Intent, PendingIntent


def descriptor(generation, key):
    return GenerationDescriptor("anchor-A", generation, key.hex())


def attested(provider, generation, key):
    verifier = AttestationVerifier(
        {("anchor-A", generation): key}, ProviderIdentity("anchor-A", generation)
    )
    return AttestedCatchup(provider, verifier)


class ActivationSchemaMigrationConcurrencyTests(unittest.TestCase):
    def test_atomic_boundary_exposes_exact_ddl_only_with_prepared_marker(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "shared.db"
            key = b"provider-key-1"
            g1 = descriptor(1, key)
            provider = FencedActivationProvider("anchor-A", 1, key, value=0)
            live = SupportedHistoricalSharedAnchorLedger(
                path, attested(provider, 1, key), g1
            )

            # Recreate a legitimate pre-LAB-090 source while retaining the
            # initialized shared-anchor/provider-history ledger.
            q = sqlite3.connect(path)
            try:
                q.execute("DROP TRIGGER block_intent_during_provider_activation")
                q.execute("DROP TABLE provider_generation_activations")
                q.commit()
            finally:
                q.close()

            prepared = _install_and_reserve_prepared(
                path, attested(provider, 1, key), g1
            )
            self.assertEqual(prepared.status, "PREPARED")

            # Model a crash immediately after the atomic SQLite commit and before
            # any external anchor effect/confirmation. Both DDL objects and the
            # PREPARED provenance row must already be durable together.
            q = sqlite3.connect(path)
            try:
                table = q.execute(
                    "SELECT type FROM sqlite_master WHERE name='provider_generation_activations'"
                ).fetchone()
                trigger = q.execute(
                    "SELECT type FROM sqlite_master WHERE name='block_intent_during_provider_activation'"
                ).fetchone()
                marker = q.execute(
                    "SELECT status FROM shared_anchor_intents "
                    "WHERE intent_id='migration:provider-generation-activation-schema:v1'"
                ).fetchone()
                self.assertEqual(table, ("table",))
                self.assertEqual(trigger, ("trigger",))
                self.assertEqual(marker, ("PREPARED",))
            finally:
                q.close()

            # A different writer cannot occupy the shared-anchor tail after that
            # commit because LAB-080 sees the migration PREPARED row.
            with self.assertRaises(PendingIntent):
                live.reserve(
                    Intent(
                        "writer-during-activation-schema-migration",
                        "component-A",
                        "migration",
                        {"x": 1},
                    )
                )

            # Explicit migration is the only recovery path and confirms the exact
            # PREPARED row instead of creating a second marker.
            migrated = ProvenancedHistoricalSharedAnchorLedger.migrate_activation_schema_v1(
                path, attested(provider, 1, key), g1
            )
            self.assertTrue(migrated.verify_activation_schema_provenance())

            q = sqlite3.connect(path)
            try:
                rows = q.execute(
                    "SELECT status FROM shared_anchor_intents "
                    "WHERE intent_id='migration:provider-generation-activation-schema:v1'"
                ).fetchall()
                self.assertEqual(rows, [("CONFIRMED",)])
            finally:
                q.close()


if __name__ == "__main__":
    unittest.main()
