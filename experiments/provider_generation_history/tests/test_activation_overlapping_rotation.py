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
    GenerationDescriptor,
    PendingRotationBlocked,
)
from experiments.provider_generation_history.supported import SupportedHistoricalSharedAnchorLedger


def descriptor(generation, key):
    return GenerationDescriptor("anchor-A", generation, key.hex())


def attested(provider, generation, key):
    verifier = AttestationVerifier(
        {("anchor-A", generation): key}, ProviderIdentity("anchor-A", generation)
    )
    return AttestedCatchup(provider, verifier)


class UnavailableOnFirstCommitProvider(FencedActivationProvider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fail_once = True

    def commit_activation(self, ticket, *, timeout_after_commit=False):
        if self.fail_once:
            self.fail_once = False
            raise ProviderUnavailable("leave first activation SQL_COMMITTED")
        return super().commit_activation(ticket, timeout_after_commit=timeout_after_commit)


class OverlappingRotationTests(unittest.TestCase):
    def test_unresolved_activation_blocks_next_provider_rotation(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "shared.db"
            k1 = b"provider-key-1"
            k2 = b"provider-key-2"
            k3 = b"provider-key-3"
            g1 = descriptor(1, k1)
            g2 = descriptor(2, k2)
            g3 = descriptor(3, k3)

            p1 = FencedActivationProvider("anchor-A", 1, k1, value=0)
            ledger = SupportedHistoricalSharedAnchorLedger(path, attested(p1, 1, k1), g1)

            state2 = ActivationState()
            p2 = UnavailableOnFirstCommitProvider(
                "anchor-A", 2, k2, value=0, activation_state=state2
            )
            with self.assertRaises(ProviderUnavailable):
                ledger.rotate_provider(
                    g2,
                    ledger.provider_history.make_transition(g1, g2),
                    attested(p2, 2, k2),
                )

            row2 = ledger._activation_row(generation_id=g2.generation_id)
            self.assertEqual(row2[6], "SQL_COMMITTED")
            self.assertEqual(ledger.provider_history.current().generation, 2)

            p3 = FencedActivationProvider("anchor-A", 3, k3, value=0)
            with self.assertRaises(PendingRotationBlocked):
                ledger.rotate_provider(
                    g3,
                    ledger.provider_history.make_transition(g2, g3),
                    attested(p3, 3, k3),
                )

            self.assertIsNone(p3.activation_state.pending)
            self.assertEqual(ledger.provider_history.current().generation, 2)
            self.assertIsNone(ledger._activation_row(generation_id=g3.generation_id))
            self.assertEqual(ledger._activation_row(generation_id=g2.generation_id)[6], "SQL_COMMITTED")


if __name__ == "__main__":
    unittest.main()
