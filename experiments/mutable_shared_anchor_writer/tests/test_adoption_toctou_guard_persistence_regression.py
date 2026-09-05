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
from experiments.asymmetric_provider_history.integration import (
    AsymmetricHistoricalSharedAnchorLedger,
)
from experiments.asymmetric_provider_history.protocol import (
    GenerationSigner,
    HistoricalVerificationError,
)
from experiments.mutable_shared_anchor_writer.history_bound_operation_scoped import (
    SupportedHistoryBoundOperationScopedAsymmetricSharedAnchorLedger,
)
from experiments.shared_anchor_intent_ledger.protocol import Intent


class CorruptAfterFirstVerifyLedger(
    SupportedHistoryBoundOperationScopedAsymmetricSharedAnchorLedger
):
    """Deterministically model a lower writer racing first LAB-091 adoption."""

    def __init__(self, *args, **kwargs):
        self._lab091_verify_calls = 0
        super().__init__(*args, **kwargs)

    def verify_durable(self):
        result = super().verify_durable()
        self._lab091_verify_calls += 1
        if self._lab091_verify_calls == 1:
            q = sqlite3.connect(self.path)
            try:
                q.execute(
                    "UPDATE asymmetric_provider_receipts SET signature=?",
                    ("00" * 64,),
                )
                q.commit()
            finally:
                q.close()
        return result


class AdoptionToctouGuardPersistenceRegressionTests(unittest.TestCase):
    @staticmethod
    def attested():
        key = b"lab091-adoption-toctou-hmac"
        provider = SignedAnchorProvider("anchor-A", 1, key, value=0)
        verifier = AttestationVerifier(
            {("anchor-A", 1): key},
            ProviderIdentity("anchor-A", 1),
        )
        return AttestedCatchup(provider, verifier)

    def test_corruption_after_first_verify_does_not_persist_lab091_guards(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "shared.db"
            signer = GenerationSigner.from_seed("anchor-A", 1, b"\x21" * 32)
            attested = self.attested()

            lower = AsymmetricHistoricalSharedAnchorLedger(
                path, attested, signer.public, signer
            )
            lower.execute(Intent("first", "component-A", "migration", {"n": 1}))

            with self.assertRaises(HistoricalVerificationError):
                CorruptAfterFirstVerifyLedger(path, attested, signer.public, signer)

            q = sqlite3.connect(path)
            try:
                lab091_triggers = q.execute(
                    "SELECT name FROM sqlite_master "
                    "WHERE type='trigger' AND name LIKE 'lab091_%' ORDER BY name"
                ).fetchall()
            finally:
                q.close()
            self.assertEqual(lab091_triggers, [])


if __name__ == "__main__":
    unittest.main()
