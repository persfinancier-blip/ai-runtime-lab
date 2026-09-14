from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from experiments.anchor_attestation.protocol import (
    AttestationVerifier,
    AttestedCatchup,
    ProviderIdentity,
    SignedAnchorProvider,
)
from experiments.provider_generation_history.protocol import (
    GenerationDescriptor,
    PendingRotationBlocked,
)
from experiments.provider_generation_history.supported import (
    SupportedHistoricalSharedAnchorLedger,
)


def descriptor(generation: int, key: bytes) -> GenerationDescriptor:
    return GenerationDescriptor("anchor-A", generation, key.hex())


def attested(provider, generation: int, key: bytes) -> AttestedCatchup:
    verifier = AttestationVerifier(
        {("anchor-A", generation): key},
        ProviderIdentity("anchor-A", generation),
    )
    return AttestedCatchup(provider, verifier)


class ProviderHistoryCapabilitySurfaceTests(unittest.TestCase):
    def test_public_history_alias_cannot_drive_locked_rotation(self):
        """Delegating the supported ledger must not leak coordinator mutation helpers."""
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "ledger.sqlite"
            k1 = b"provider-key-1"
            k2 = b"provider-key-2"
            g1 = descriptor(1, k1)
            g2 = descriptor(2, k2)

            provider = SignedAnchorProvider("anchor-A", 1, k1, value=0)
            ledger = SupportedHistoricalSharedAnchorLedger(
                path,
                attested(provider, 1, k1),
                g1,
            )

            # The supported public history surface intentionally blocks rotate().
            with self.assertRaises(PendingRotationBlocked):
                ledger.provider_history.rotate(g2, ledger.provider_history.make_transition(g1, g2))

            # It must also be impossible to recover the live coordinator-only strategy
            # from the public alias and invoke its transaction-internal rotation helper.
            # Pre-fix, provider_history exposes the exact live strategy and this call
            # durably advances the history head without rotate_provider().
            history = ledger.provider_history
            q = ledger._con()
            try:
                q.execute("BEGIN IMMEDIATE")
                with self.assertRaises((AttributeError, PendingRotationBlocked)):
                    history._rotate_locked(q, g2, history.make_transition(g1, g2))
                q.rollback()
            finally:
                q.close()

            self.assertEqual(ledger.provider_history.current().generation, 1)
            self.assertEqual(
                ledger._descriptor_from_attested(ledger.attested).generation,
                1,
            )


if __name__ == "__main__":
    unittest.main()
