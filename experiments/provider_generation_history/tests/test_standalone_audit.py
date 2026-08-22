import sqlite3
import tempfile
import unittest
from pathlib import Path

from experiments.provider_generation_history.protocol import (
    DurableProviderHistory,
    GenerationDescriptor,
    HistoricalReceipt,
    HistoricalVerificationError,
    mac,
)


class StandaloneAuditTests(unittest.TestCase):
    def test_restart_rejects_corrupt_standalone_receipt_binding(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "history.db"
            key = b"provider-key-1"
            bootstrap = GenerationDescriptor("anchor-A", 1, key.hex())
            history = DurableProviderHistory(path, bootstrap)
            unsigned = HistoricalReceipt(
                "anchor-A", 1, 1, "req-1", "RECONCILE", "challenge", ""
            )
            receipt = HistoricalReceipt(
                unsigned.provider_id,
                unsigned.generation,
                unsigned.position,
                unsigned.request_id,
                unsigned.kind,
                unsigned.challenge,
                mac(key, unsigned.unsigned),
            )
            history.store_receipt(receipt)

            q = sqlite3.connect(path)
            q.execute(
                "UPDATE historical_provider_receipts SET stable_binding=? WHERE request_id=?",
                ("0" * 64, receipt.request_id),
            )
            q.commit()
            q.close()

            with self.assertRaises(HistoricalVerificationError):
                DurableProviderHistory(path, bootstrap)
            with self.assertRaises(HistoricalVerificationError):
                history.load_receipt(receipt.request_id)


if __name__ == "__main__":
    unittest.main()
