import sqlite3
import tempfile
import unittest
from pathlib import Path

from experiments.anchor_attestation.protocol import (
    AttestationVerifier,
    AttestedCatchup,
    ProviderIdentity,
    SignedAnchorProvider,
)
from experiments.provider_generation_history.protocol import (
    GenerationDescriptor,
    HistoricalVerificationError,
)
from experiments.provider_generation_history.supported import SupportedHistoricalSharedAnchorLedger
from experiments.shared_anchor_intent_ledger.protocol import Intent


class AuditRegressionTests(unittest.TestCase):
    def test_restart_rejects_corrupt_persisted_historical_receipt_binding(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "shared.db"
            key = b"provider-key-1"
            provider = SignedAnchorProvider("anchor-A", 1, key, value=0)
            attested = AttestedCatchup(
                provider,
                AttestationVerifier(
                    {("anchor-A", 1): key}, ProviderIdentity("anchor-A", 1)
                ),
            )
            bootstrap = GenerationDescriptor("anchor-A", 1, key.hex())
            ledger = SupportedHistoricalSharedAnchorLedger(path, attested, bootstrap)
            ledger.execute(Intent("old", "component-A", "migration", {"v": 1}))

            q = sqlite3.connect(path)
            q.execute(
                "UPDATE historical_provider_receipts SET stable_binding=?",
                ("0" * 64,),
            )
            q.commit()
            q.close()

            with self.assertRaises(HistoricalVerificationError):
                SupportedHistoricalSharedAnchorLedger(path, attested, bootstrap)


if __name__ == "__main__":
    unittest.main()
