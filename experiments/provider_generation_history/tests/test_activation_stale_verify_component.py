import tempfile
import unittest
from pathlib import Path

from experiments.anchor_attestation.protocol import (
    AttestationVerifier,
    AttestedCatchup,
    ProviderIdentity,
    ProviderUnavailable,
)
from experiments.provider_generation_history.activation import (
    ActivationState,
    FencedActivationProvider,
)
from experiments.provider_generation_history.protocol import (
    CurrentGenerationRequired,
    GenerationDescriptor,
)
from experiments.provider_generation_history.supported import SupportedHistoricalSharedAnchorLedger


def descriptor(generation, key):
    return GenerationDescriptor("anchor-A", generation, key.hex())


def attested(provider, generation, key):
    verifier = AttestationVerifier(
        {("anchor-A", generation): key}, ProviderIdentity("anchor-A", generation)
    )
    return AttestedCatchup(provider, verifier)


class UnavailableOnFirstReleaseProvider(FencedActivationProvider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fail_release_once = True

    def release_activation(self, ticket):
        if self.fail_release_once:
            self.fail_release_once = False
            raise ProviderUnavailable("simulated outage after durable coordinator acknowledgement")
        return super().release_activation(ticket)


class StaleRuntimeVerifyComponentTests(unittest.TestCase):
    def test_failed_release_stale_runtime_cannot_verify_component(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "shared.db"
            k1 = b"provider-key-1"
            k2 = b"provider-key-2"
            g1 = descriptor(1, k1)
            g2 = descriptor(2, k2)

            p1 = FencedActivationProvider("anchor-A", 1, k1, value=0)
            ledger = SupportedHistoricalSharedAnchorLedger(
                path, attested(p1, 1, k1), g1
            )
            state = ActivationState()
            p2 = UnavailableOnFirstReleaseProvider(
                "anchor-A", 2, k2, value=0, activation_state=state
            )

            with self.assertRaises(ProviderUnavailable):
                ledger.rotate_provider(
                    g2,
                    ledger.provider_history.make_transition(g1, g2),
                    attested(p2, 2, k2),
                )

            self.assertEqual(ledger.provider_history.current().generation, 2)
            self.assertIs(ledger.attested.provider, p1)

            with self.assertRaises(CurrentGenerationRequired):
                ledger.verify_component("component-A")


if __name__ == "__main__":
    unittest.main()
