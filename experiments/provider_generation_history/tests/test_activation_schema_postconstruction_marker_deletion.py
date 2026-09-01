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
)
from experiments.provider_generation_history.protocol import (
    GenerationDescriptor,
    HistoricalVerificationError,
)
from experiments.provider_generation_history.supported import SupportedHistoricalSharedAnchorLedger
from experiments.shared_anchor_intent_ledger.protocol import Intent


def descriptor(generation, key):
    return GenerationDescriptor("anchor-A", generation, key.hex())


def attested(provider, generation, key):
    verifier = AttestationVerifier(
        {("anchor-A", generation): key}, ProviderIdentity("anchor-A", generation)
    )
    return AttestedCatchup(provider, verifier)


class ActivationSchemaPostConstructionMarkerDeletionTests(unittest.TestCase):
    def test_execute_fails_closed_after_confirmed_marker_is_deleted(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "shared.db"
            key = b"provider-key-1"
            provider = FencedActivationProvider("anchor-A", 1, key, value=0)
            g1 = descriptor(1, key)

            SupportedHistoricalSharedAnchorLedger(path, attested(provider, 1, key), g1)
            q = sqlite3.connect(path)
            try:
                q.execute("DROP TRIGGER block_intent_during_provider_activation")
                q.execute("DROP TABLE provider_generation_activations")
                q.commit()
            finally:
                q.close()

            ledger = ProvenancedHistoricalSharedAnchorLedger.migrate_activation_schema_v1(
                path, attested(provider, 1, key), g1
            )

            q = sqlite3.connect(path)
            try:
                q.execute(
                    "DELETE FROM shared_anchor_intents WHERE intent_id=?",
                    (_completion_intent().intent_id,),
                )
                q.commit()
            finally:
                q.close()

            intent = Intent(
                "post-provenance-tamper",
                "post-provenance-tamper",
                "archive_checkpoint",
                {"checkpoint": 1},
            )
            with self.assertRaises(HistoricalVerificationError):
                ledger.execute(intent)

            q = sqlite3.connect(path)
            try:
                row = q.execute(
                    "SELECT 1 FROM shared_anchor_intents WHERE intent_id=?",
                    (intent.intent_id,),
                ).fetchone()
                self.assertIsNone(row)
            finally:
                q.close()


if __name__ == "__main__":
    unittest.main()
