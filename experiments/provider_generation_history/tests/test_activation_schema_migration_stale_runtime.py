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
    _completion_intent,
    _install_and_reserve_prepared,
)
from experiments.provider_generation_history.integration import IntegratedProviderHistory
from experiments.provider_generation_history.protocol import (
    CurrentGenerationRequired,
    GenerationDescriptor,
)
from experiments.provider_generation_history.supported import SupportedHistoricalSharedAnchorLedger


def descriptor(generation, key):
    return GenerationDescriptor("anchor-A", generation, key.hex())


def attested(provider, generation, key, *, keyring=None):
    if keyring is None:
        keyring = {("anchor-A", generation): key}
    verifier = AttestationVerifier(
        keyring, ProviderIdentity("anchor-A", generation)
    )
    return AttestedCatchup(provider, verifier)


class ActivationSchemaMigrationStaleRuntimeTests(unittest.TestCase):
    def test_stale_runtime_fails_before_ddl_and_marker_commit(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "shared.db"
            key1 = b"provider-key-1"
            key2 = b"provider-key-2"
            g1 = descriptor(1, key1)
            g2 = descriptor(2, key2)
            provider1 = FencedActivationProvider("anchor-A", 1, key1, value=0)

            # Establish a valid inherited authority surface, advance its durable
            # provider history to generation 2, then model the legitimate pre-LAB-090
            # activation-schema state. The runtime intentionally remains generation 1.
            SupportedHistoricalSharedAnchorLedger(
                path, attested(provider1, 1, key1), g1
            )
            history = IntegratedProviderHistory(path, g1)
            history.rotate(g2, history.make_transition(g1, g2))

            q = sqlite3.connect(path)
            try:
                q.execute("DROP TRIGGER block_intent_during_provider_activation")
                q.execute("DROP TABLE provider_generation_activations")
                q.commit()
            finally:
                q.close()

            stale = attested(
                provider1,
                1,
                key1,
                keyring={
                    ("anchor-A", 1): key1,
                    ("anchor-A", 2): key2,
                },
            )
            with self.assertRaises(CurrentGenerationRequired):
                ProvenancedHistoricalSharedAnchorLedger.migrate_activation_schema_v1(
                    path, stale, g1
                )

            # The stale runtime must be rejected before either side of the atomic
            # migration boundary becomes visible.
            q = sqlite3.connect(path)
            try:
                table = q.execute(
                    "SELECT type FROM sqlite_master WHERE name='provider_generation_activations'"
                ).fetchone()
                trigger = q.execute(
                    "SELECT type FROM sqlite_master WHERE name='block_intent_during_provider_activation'"
                ).fetchone()
                marker = q.execute(
                    "SELECT status FROM shared_anchor_intents WHERE intent_id=?",
                    (_completion_intent().intent_id,),
                ).fetchone()
                head = q.execute(
                    "SELECT generation_id,generation FROM provider_generation_head WHERE singleton=1"
                ).fetchone()
            finally:
                q.close()

            self.assertIsNone(table)
            self.assertIsNone(trigger)
            self.assertIsNone(marker)
            self.assertEqual(head, (g2.generation_id, 2))

    def test_stale_runtime_cannot_recover_existing_prepared_marker(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "shared.db"
            key1 = b"provider-key-1"
            key2 = b"provider-key-2"
            g1 = descriptor(1, key1)
            g2 = descriptor(2, key2)
            provider1 = FencedActivationProvider("anchor-A", 1, key1, value=0)
            provider2 = FencedActivationProvider("anchor-A", 2, key2, value=0)
            keyring = {
                ("anchor-A", 1): key1,
                ("anchor-A", 2): key2,
            }

            SupportedHistoricalSharedAnchorLedger(
                path, attested(provider1, 1, key1), g1
            )
            history = IntegratedProviderHistory(path, g1)
            history.rotate(g2, history.make_transition(g1, g2))

            q = sqlite3.connect(path)
            try:
                q.execute("DROP TRIGGER block_intent_during_provider_activation")
                q.execute("DROP TABLE provider_generation_activations")
                q.commit()
            finally:
                q.close()

            current = attested(provider2, 2, key2, keyring=keyring)
            prepared = _install_and_reserve_prepared(path, current, g1)
            self.assertEqual(prepared.status, "PREPARED")

            stale = attested(provider1, 1, key1, keyring=keyring)
            with self.assertRaises(CurrentGenerationRequired):
                ProvenancedHistoricalSharedAnchorLedger.migrate_activation_schema_v1(
                    path, stale, g1
                )

            q = sqlite3.connect(path)
            try:
                marker = q.execute(
                    "SELECT status FROM shared_anchor_intents WHERE intent_id=?",
                    (_completion_intent().intent_id,),
                ).fetchone()[0]
            finally:
                q.close()
            self.assertEqual(marker, "PREPARED")


if __name__ == "__main__":
    unittest.main()
