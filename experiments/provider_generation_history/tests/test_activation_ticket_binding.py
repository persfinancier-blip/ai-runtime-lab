import tempfile
import unittest
from pathlib import Path

from experiments.anchor_attestation.protocol import (
    AttestationVerifier,
    AttestedCatchup,
    ProviderIdentity,
)
from experiments.provider_generation_history.activation import (
    ActivationTicket,
    FencedActivationProvider,
)
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


class WrongTicketProvider(FencedActivationProvider):
    def prepare_activation(self, *, expected_position, activation_id):
        ticket = super().prepare_activation(
            expected_position=expected_position,
            activation_id=activation_id,
        )
        return ActivationTicket(
            "wrong-provider",
            ticket.generation,
            ticket.expected_position,
            ticket.activation_id,
            ticket.fence,
        )


class ActivationTicketBindingTests(unittest.TestCase):
    def test_mismatched_prepare_ticket_cannot_rotate_durable_generation(self):
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
            p2 = WrongTicketProvider("anchor-A", 2, k2, value=0)

            with self.assertRaises(HistoricalVerificationError):
                ledger.rotate_provider(
                    g2,
                    ledger.provider_history.make_transition(g1, g2),
                    attested(p2, 2, k2),
                )

            self.assertEqual(ledger.provider_history.current().generation, 1)
            self.assertIsNone(ledger._activation_row(generation_id=g2.generation_id))


if __name__ == "__main__":
    unittest.main()
