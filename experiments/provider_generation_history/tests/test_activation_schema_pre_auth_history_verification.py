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


def descriptor(generation, key):
    return GenerationDescriptor("anchor-A", generation, key.hex())


def attested(provider, generation, key):
    verifier = AttestationVerifier(
        {("anchor-A", generation): key}, ProviderIdentity("anchor-A", generation)
    )
    return AttestedCatchup(provider, verifier)


class ActivationSchemaPreAuthHistoryVerificationTests(unittest.TestCase):
    def test_corrupt_provider_history_fails_before_missing_marker_receipt_is_recreated(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "shared.db"
            key1 = b"provider-key-1"
            key2 = b"provider-key-2"
            g1 = descriptor(1, key1)
            g2 = descriptor(2, key2)
            provider = FencedActivationProvider("anchor-A", 1, key1, value=0)
            runtime = attested(provider, 1, key1)

            SupportedHistoricalSharedAnchorLedger(path, runtime, g1)
            q = sqlite3.connect(path)
            try:
                q.execute("DROP TRIGGER block_intent_during_provider_activation")
                q.execute("DROP TABLE provider_generation_activations")
                q.commit()
            finally:
                q.close()

            ProvenancedHistoricalSharedAnchorLedger.migrate_activation_schema_v1(
                path, runtime, g1
            )

            q = sqlite3.connect(path)
            try:
                request_id = q.execute(
                    "SELECT request_id FROM shared_anchor_intents WHERE intent_id=?",
                    (_completion_intent().intent_id,),
                ).fetchone()[0]
                q.execute(
                    "DELETE FROM historical_provider_receipts WHERE request_id=?",
                    (request_id,),
                )
                # A valid-looking orphan successor is deliberately outside the
                # receipt's generation. Receipt-only verification can miss it,
                # while complete provider-history verification must reject it.
                q.execute(
                    "INSERT INTO provider_generations VALUES(?,?,?,?)",
                    (g2.generation_id, g2.provider_id, g2.generation, g2.verification_key_hex),
                )
                q.commit()
            finally:
                q.close()

            with self.assertRaises(HistoricalVerificationError):
                ProvenancedHistoricalSharedAnchorLedger(path, runtime, g1)

            q = sqlite3.connect(path)
            try:
                receipt = q.execute(
                    "SELECT 1 FROM historical_provider_receipts WHERE request_id=?",
                    (request_id,),
                ).fetchone()
            finally:
                q.close()
            self.assertIsNone(receipt)

    def test_corrupt_historical_activation_fails_before_missing_marker_receipt_is_recreated(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "shared.db"
            key1 = b"provider-key-1"
            g1 = descriptor(1, key1)
            provider = FencedActivationProvider("anchor-A", 1, key1, value=0)
            runtime = attested(provider, 1, key1)

            SupportedHistoricalSharedAnchorLedger(path, runtime, g1)
            q = sqlite3.connect(path)
            try:
                q.execute("DROP TRIGGER block_intent_during_provider_activation")
                q.execute("DROP TABLE provider_generation_activations")
                q.commit()
            finally:
                q.close()

            ProvenancedHistoricalSharedAnchorLedger.migrate_activation_schema_v1(
                path, runtime, g1
            )

            q = sqlite3.connect(path)
            try:
                request_id = q.execute(
                    "SELECT request_id FROM shared_anchor_intents WHERE intent_id=?",
                    (_completion_intent().intent_id,),
                ).fetchone()[0]
                q.execute(
                    "DELETE FROM historical_provider_receipts WHERE request_id=?",
                    (request_id,),
                )
                # COMMITTED avoids the SQL_COMMITTED trigger fence, but the row is
                # invalid because its generation has no provider-history descriptor.
                q.execute(
                    "INSERT INTO provider_generation_activations VALUES(?,?,?,?,?,?,'COMMITTED')",
                    (
                        "provider-activation:missing-generation:0",
                        "missing-generation",
                        "anchor-A",
                        99,
                        0,
                        1,
                    ),
                )
                q.commit()
            finally:
                q.close()

            with self.assertRaises(HistoricalVerificationError):
                ProvenancedHistoricalSharedAnchorLedger(path, runtime, g1)

            q = sqlite3.connect(path)
            try:
                receipt = q.execute(
                    "SELECT 1 FROM historical_provider_receipts WHERE request_id=?",
                    (request_id,),
                ).fetchone()
            finally:
                q.close()
            self.assertIsNone(receipt)


if __name__ == "__main__":
    unittest.main()
