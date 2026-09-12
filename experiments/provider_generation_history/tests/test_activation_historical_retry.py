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
    InvalidTransition,
)
from experiments.provider_generation_history.supported import SupportedHistoricalSharedAnchorLedger


def descriptor(generation, key):
    return GenerationDescriptor("anchor-A", generation, key.hex())


def attested(provider, generation, key):
    verifier = AttestationVerifier(
        {("anchor-A", generation): key}, ProviderIdentity("anchor-A", generation)
    )
    return AttestedCatchup(provider, verifier)


class HistoricalActivationRetryTests(unittest.TestCase):
    def test_historical_activation_retry_fails_before_runtime_mutation(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "shared.db"
            k1 = b"provider-key-1"
            k2 = b"provider-key-2"
            k3 = b"provider-key-3"
            g1 = descriptor(1, k1)
            g2 = descriptor(2, k2)
            g3 = descriptor(3, k3)

            p1 = FencedActivationProvider("anchor-A", 1, k1, value=0)
            ledger = SupportedHistoricalSharedAnchorLedger(
                path, attested(p1, 1, k1), g1
            )
            p2 = FencedActivationProvider("anchor-A", 2, k2, value=0)
            ledger.rotate_provider(
                g2,
                ledger.provider_history.make_transition(g1, g2),
                attested(p2, 2, k2),
            )
            p3 = FencedActivationProvider("anchor-A", 3, k3, value=0)
            ledger.rotate_provider(
                g3,
                ledger.provider_history.make_transition(g2, g3),
                attested(p3, 3, k3),
            )

            self.assertEqual(ledger.provider_history.current().generation, 3)
            self.assertIs(ledger.attested.provider, p3)

            with self.assertRaises(InvalidTransition):
                ledger.rotate_provider(
                    g2,
                    ledger.provider_history.make_transition(g1, g2),
                    attested(p2, 2, k2),
                )

            self.assertEqual(ledger.provider_history.current().generation, 3)
            self.assertIs(ledger.attested.provider, p3)
            self.assertEqual(ledger._descriptor_from_attested(ledger.attested).generation, 3)


if __name__ == "__main__":
    unittest.main()
