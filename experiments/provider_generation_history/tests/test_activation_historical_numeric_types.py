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


class HistoricalActivationNumericTypeTests(unittest.TestCase):
    def test_restart_rejects_non_integer_historical_ticket_numbers(self):
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

            # SQLite INTEGER affinity still stores non-integral REAL values as REAL.
            # Historical COMMITTED rows are not reconciled with a live provider, so
            # verification itself must reject a ticket that cannot be byte/exactly
            # represented by the integer provider activation contract.
            q = sqlite3.connect(path)
            try:
                q.execute(
                    "UPDATE provider_generation_activations "
                    "SET expected_position=0.5, fence=1.5 "
                    "WHERE new_generation_id=?",
                    (g2.generation_id,),
                )
                q.commit()
            finally:
                q.close()

            with self.assertRaises(HistoricalVerificationError):
                SupportedHistoricalSharedAnchorLedger(
                    path, attested(p3, 3, k3), g1
                )


if __name__ == "__main__":
    unittest.main()
