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
from experiments.provider_generation_history.protocol import GenerationDescriptor
from experiments.provider_generation_history.supported import SupportedHistoricalSharedAnchorLedger


def descriptor(generation, key):
    return GenerationDescriptor("anchor-A", generation, key.hex())


def attested(provider, generation, key):
    verifier = AttestationVerifier(
        {("anchor-A", generation): key}, ProviderIdentity("anchor-A", generation)
    )
    return AttestedCatchup(provider, verifier)


class ActivationSchemaRestartPrecheckTests(unittest.TestCase):
    def test_legacy_startup_fails_before_reserving_provenance_marker(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "shared.db"
            key = b"provider-key-1"
            g1 = descriptor(1, key)
            provider = FencedActivationProvider("anchor-A", 1, key, value=0)
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

            q = sqlite3.connect(path)
            try:
                marker = q.execute(
                    "SELECT status FROM shared_anchor_intents WHERE intent_id=?",
                    (_completion_intent().intent_id,),
                ).fetchone()
                table = q.execute(
                    "SELECT type FROM sqlite_master WHERE name='provider_generation_activations'"
                ).fetchone()
                trigger = q.execute(
                    "SELECT type FROM sqlite_master WHERE name='block_intent_during_provider_activation'"
                ).fetchone()
            finally:
                q.close()

            self.assertIsNone(marker)
            self.assertIsNone(table)
            self.assertIsNone(trigger)


if __name__ == "__main__":
    unittest.main()
