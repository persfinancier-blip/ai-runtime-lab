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


class ActivationTriggerTamperRestartTests(unittest.TestCase):
    def test_restart_rejects_tampered_activation_intent_fence_trigger(self):
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
                q.executescript(
                    """
                    DROP TRIGGER block_intent_during_provider_activation;
                    CREATE TRIGGER block_intent_during_provider_activation
                    BEFORE INSERT ON shared_anchor_intents
                    WHEN 0
                    BEGIN
                      SELECT 1;
                    END;
                    """
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
