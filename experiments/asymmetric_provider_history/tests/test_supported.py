import sqlite3
import tempfile
import threading
import unittest
from pathlib import Path

from experiments.anchor_attestation.protocol import (
    AttestationVerifier,
    AttestedCatchup,
    ProviderIdentity,
    SignedAnchorProvider,
)
from experiments.asymmetric_provider_history.protocol import GenerationSigner
from experiments.asymmetric_provider_history.supported import (
    SupportedAsymmetricHistoricalSharedAnchorLedger,
)
from experiments.shared_anchor_intent_ledger.protocol import Intent


class SupportedSurfaceTests(unittest.TestCase):
    @staticmethod
    def ledger(path):
        key = b"current-hmac"
        provider = SignedAnchorProvider("anchor-A", 1, key, value=0)
        attested = AttestedCatchup(
            provider,
            AttestationVerifier(
                {("anchor-A", 1): key}, ProviderIdentity("anchor-A", 1)
            ),
        )
        signer = GenerationSigner.from_seed("anchor-A", 1, b"\x31" * 32)
        return provider, SupportedAsymmetricHistoricalSharedAnchorLedger(
            path, attested, signer.public, signer
        )

    def test_concurrent_reconciliation_converges_on_first_durable_receipt(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "shared.db"
            provider, ledger = self.ledger(path)
            intent = Intent("race", "component-A", "migration", {"v": 1})
            entry = ledger.reserve(intent)

            # Commit the external effect but intentionally leave the SQL ledger
            # PREPARED, reproducing the crash/reconciliation window.
            ledger.attested.catch_up_one(
                db_sequence=entry.position,
                request_id=entry.request_id,
            )

            barrier = threading.Barrier(3)
            results = []
            errors = []

            def reconcile():
                barrier.wait()
                try:
                    results.append(ledger._reauthenticate(entry))
                except Exception as exc:
                    errors.append(exc)

            workers = [threading.Thread(target=reconcile) for _ in range(2)]
            for worker in workers:
                worker.start()
            barrier.wait()
            for worker in workers:
                worker.join(5)

            self.assertFalse(any(worker.is_alive() for worker in workers))
            self.assertEqual(errors, [])
            self.assertEqual(len(results), 2)
            self.assertEqual(results[0], results[1])

            q = sqlite3.connect(path)
            try:
                self.assertEqual(
                    q.execute(
                        "SELECT COUNT(*) FROM asymmetric_provider_receipts WHERE request_id=?",
                        (entry.request_id,),
                    ).fetchone()[0],
                    1,
                )
            finally:
                q.close()

            # A normal retry consumes the durable receipt and completes without a
            # second external increment.
            before = provider.increment_calls
            confirmed = ledger.execute(intent)
            self.assertEqual(confirmed.status, "CONFIRMED")
            self.assertEqual(provider.increment_calls, before)


if __name__ == "__main__":
    unittest.main()
