import sqlite3
import tempfile
import unittest
from pathlib import Path

from experiments.anchor_attestation.protocol import (
    AttestationVerifier,
    AttestedCatchup,
    ProviderIdentity,
    ProviderUnavailable,
    SignedAnchorProvider,
)
from experiments.asymmetric_provider_history.protocol import GenerationSigner
from experiments.mutable_shared_anchor_writer.history_bound_operation_scoped import (
    SupportedHistoryBoundOperationScopedAsymmetricSharedAnchorLedger,
)
from experiments.shared_anchor_intent_ledger.protocol import Intent, PendingIntent


class CommitThenLoseFirstReconcile(SignedAnchorProvider):
    """Commit the increment, then make the first reconciliation unavailable."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fail_reconcile_once = True

    def reconcile_increment(self, *, challenge, request_id):
        if self.fail_reconcile_once:
            self.fail_reconcile_once = False
            raise ProviderUnavailable("first reconciliation path unavailable")
        return super().reconcile_increment(
            challenge=challenge,
            request_id=request_id,
        )


class RealStackTimeoutUnknownConvergenceTests(unittest.TestCase):
    @staticmethod
    def runtime(provider):
        key = provider.key
        attested = AttestedCatchup(
            provider,
            AttestationVerifier(
                {(provider.provider_id, provider.generation): key},
                ProviderIdentity(provider.provider_id, provider.generation),
            ),
        )
        signer = GenerationSigner.from_seed(
            provider.provider_id,
            provider.generation,
            b"\x41" * 32,
        )
        return attested, signer

    @classmethod
    def ledger(cls, path, provider):
        attested, signer = cls.runtime(provider)
        return SupportedHistoryBoundOperationScopedAsymmetricSharedAnchorLedger(
            path,
            attested,
            signer.public,
            signer,
        )

    def test_timeout_after_commit_retry_converges_without_reincrement_and_survives_restart(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "shared.db"
            provider = CommitThenLoseFirstReconcile(
                "anchor-A",
                1,
                b"current-hmac",
                value=0,
            )
            ledger = self.ledger(path, provider)
            intent = Intent(
                "real-timeout-unknown",
                "component-A",
                "migration",
                {"v": 1},
            )

            with self.assertRaises(PendingIntent):
                ledger.execute(intent, timeout_after_commit=True)

            pending = ledger.entry(intent.intent_id)
            self.assertEqual(pending.status, "PREPARED")
            self.assertIsNone(pending.receipt_binding)
            self.assertEqual(provider.value, 1)
            self.assertEqual(provider.increment_calls, 1)

            q = sqlite3.connect(path)
            try:
                self.assertEqual(
                    q.execute(
                        "SELECT COUNT(*) FROM asymmetric_provider_receipts "
                        "WHERE request_id=?",
                        (pending.request_id,),
                    ).fetchone()[0],
                    0,
                )
            finally:
                q.close()

            confirmed = ledger.execute(intent)
            self.assertEqual(confirmed.status, "CONFIRMED")
            self.assertIsNotNone(confirmed.receipt_binding)
            self.assertEqual(provider.value, 1)
            self.assertEqual(provider.increment_calls, 1)
            self.assertTrue(ledger.verify_durable())

            q = sqlite3.connect(path)
            try:
                self.assertEqual(
                    q.execute(
                        "SELECT COUNT(*) FROM asymmetric_provider_receipts "
                        "WHERE request_id=?",
                        (confirmed.request_id,),
                    ).fetchone()[0],
                    1,
                )
            finally:
                q.close()

            restarted = self.ledger(path, provider)
            after_restart = restarted.execute(intent)
            self.assertEqual(after_restart, confirmed)
            self.assertEqual(provider.value, 1)
            self.assertEqual(provider.increment_calls, 1)
            self.assertTrue(restarted.verify_durable())


if __name__ == "__main__":
    unittest.main()
