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


class OrphanActivationRestartTests(unittest.TestCase):
    def test_restart_rejects_activation_without_generation_history(self):
        """An orphan SQL_COMMITTED activation must not disappear through INNER JOIN.

        The activation table has no foreign-key constraint. If an orphan unresolved
        row is accepted at restart, the persisted block_intent_during_provider_activation
        trigger still sees it and globally blocks future writers even though activation
        verification silently skipped the row.
        """
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "shared.db"
            key = b"provider-key-1"
            g1 = descriptor(1, key)
            provider = FencedActivationProvider("anchor-A", 1, key, value=0)
            SupportedHistoricalSharedAnchorLedger(
                path, attested(provider, 1, key), g1
            )

            q = sqlite3.connect(path)
            try:
                q.execute(
                    "INSERT INTO provider_generation_activations VALUES(?,?,?,?,?,?,'SQL_COMMITTED')",
                    (
                        "provider-activation:orphan-generation:0",
                        "orphan-generation",
                        "anchor-A",
                        2,
                        0,
                        1,
                    ),
                )
                q.commit()
            finally:
                q.close()

            with self.assertRaises(HistoricalVerificationError):
                SupportedHistoricalSharedAnchorLedger(
                    path, attested(provider, 1, key), g1
                )


if __name__ == "__main__":
    unittest.main()
