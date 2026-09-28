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


class PrematureReleaseProvider(FencedActivationProvider):
    """Models a faulty provider that drops its fence before coordinator acknowledgement."""

    def commit_activation(self, ticket, *, timeout_after_commit=False):
        status = super().commit_activation(ticket, timeout_after_commit=timeout_after_commit)
        if status == "COMMITTED_FENCED":
            return self.release_activation(ticket)
        return status


class PrematureReleaseTests(unittest.TestCase):
    def test_rotation_fails_closed_if_provider_releases_before_sql_ack(self):
        k1 = b"provider-key-1"
        k2 = b"provider-key-2"
        g1 = descriptor(1, k1)
        g2 = descriptor(2, k2)

        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "shared.db"
            p1 = FencedActivationProvider("anchor-A", 1, k1, value=0)
            ledger = SupportedHistoricalSharedAnchorLedger(
                path, attested(p1, 1, k1), g1
            )
            p2 = PrematureReleaseProvider("anchor-A", 2, k2, value=0)

            with self.assertRaisesRegex(
                HistoricalVerificationError,
                "must remain fenced until durable acknowledgement",
            ):
                ledger.rotate_provider(
                    g2,
                    ledger.provider_history.make_transition(g1, g2),
                    attested(p2, 2, k2),
                )

            row = ledger._activation_row(generation_id=g2.generation_id)
            self.assertEqual(row[6], "SQL_COMMITTED")
            ticket = ledger._ticket_from_row(row)
            self.assertEqual(p2.activation_status(ticket), "RELEASED")

            with self.assertRaisesRegex(
                HistoricalVerificationError,
                "released before durable acknowledgement",
            ):
                SupportedHistoricalSharedAnchorLedger(
                    path, attested(p2, 2, k2), g1
                )


if __name__ == "__main__":
    unittest.main()
