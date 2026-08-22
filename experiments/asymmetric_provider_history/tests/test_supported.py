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
from experiments.asymmetric_provider_history.protocol import (
    GenerationSigner,
    HistoricalVerificationError,
)
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

            before = provider.increment_calls
            confirmed = ledger.execute(intent)
            self.assertEqual(confirmed.status, "CONFIRMED")
            self.assertEqual(provider.increment_calls, before)

    def test_signed_read_cannot_substitute_for_reconcile_evidence(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "shared.db"
            _, ledger = self.ledger(path)
            intent = Intent("semantic", "component-A", "migration", {"v": 1})
            ledger.execute(intent)
            entry = ledger.entry(intent.intent_id)

            challenge = "signed-read-is-not-effect-proof"
            unsigned = {
                "kind": "READ",
                "provider_id": entry.provider_id,
                "generation": entry.provider_generation,
                "position": entry.position,
                "request_id": entry.request_id,
                "challenge": challenge,
            }
            signature = ledger.signer.sign(unsigned)

            q = sqlite3.connect(path)
            try:
                q.execute(
                    "UPDATE asymmetric_provider_receipts "
                    "SET kind='READ', challenge=?, signature=? WHERE request_id=?",
                    (challenge, signature, entry.request_id),
                )
                q.commit()
            finally:
                q.close()

            with self.assertRaises(HistoricalVerificationError):
                ledger.verify_durable()


if __name__ == "__main__":
    unittest.main()
