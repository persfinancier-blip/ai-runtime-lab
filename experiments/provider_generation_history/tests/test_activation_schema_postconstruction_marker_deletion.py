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
    HistoricalReceipt,
    HistoricalVerificationError,
    mac,
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
    def _migrated(self):
        td = tempfile.TemporaryDirectory()
        path = Path(td.name) / "shared.db"
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
        return td, path, key, provider, g1, ledger

    def _delete_marker(self, path):
        q = sqlite3.connect(path)
        try:
            q.execute(
                "DELETE FROM shared_anchor_intents WHERE intent_id=?",
                (_completion_intent().intent_id,),
            )
            q.commit()
        finally:
            q.close()

    def test_execute_fails_closed_after_confirmed_marker_is_deleted(self):
        td, path, key, provider, g1, ledger = self._migrated()
        with td:
            self._delete_marker(path)

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

    def test_rotate_provider_fails_closed_after_confirmed_marker_is_deleted(self):
        td, path, key1, provider1, g1, ledger = self._migrated()
        with td:
            self._delete_marker(path)
            key2 = b"provider-key-2"
            g2 = descriptor(2, key2)
            provider2 = FencedActivationProvider("anchor-A", 2, key2, value=1)

            with self.assertRaises(HistoricalVerificationError):
                ledger.rotate_provider(
                    g2,
                    ledger.provider_history.make_transition(g1, g2),
                    attested(provider2, 2, key2),
                )

            self.assertEqual(ledger.provider_history.current().generation, 1)
            self.assertIsNone(ledger._activation_row(generation_id=g2.generation_id))

    def test_verify_component_does_not_advance_watermark_after_marker_deletion(self):
        td, path, key, provider, g1, ledger = self._migrated()
        with td:
            component_id = "post-provenance-component"
            self.assertEqual(ledger.verify_component(component_id), 1)
            self.assertEqual(ledger.watermark(component_id), 1)

            ledger.execute(
                Intent(
                    "pre-tamper-confirmed",
                    component_id,
                    "archive_checkpoint",
                    {"checkpoint": 2},
                )
            )
            self._delete_marker(path)

            with self.assertRaises(HistoricalVerificationError):
                ledger.verify_component(component_id)
            self.assertEqual(ledger.watermark(component_id), 1)

    def test_direct_provider_receipt_store_fails_closed_after_marker_deletion(self):
        td, path, key, provider, g1, ledger = self._migrated()
        with td:
            self._delete_marker(path)
            unsigned = {
                "provider_id": "anchor-A",
                "generation": 1,
                "position": 1,
                "request_id": "post-provenance-direct-receipt",
                "kind": "RECONCILE",
                "challenge": "post-provenance-direct-receipt-challenge",
            }
            receipt = HistoricalReceipt(
                unsigned["provider_id"],
                unsigned["generation"],
                unsigned["position"],
                unsigned["request_id"],
                unsigned["kind"],
                unsigned["challenge"],
                mac(key, unsigned),
            )

            with self.assertRaises(HistoricalVerificationError):
                ledger.provider_history.store_receipt(receipt)

            q = sqlite3.connect(path)
            try:
                row = q.execute(
                    "SELECT 1 FROM historical_provider_receipts WHERE request_id=?",
                    (receipt.request_id,),
                ).fetchone()
                self.assertIsNone(row)
            finally:
                q.close()


if __name__ == "__main__":
    unittest.main()
