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
    CurrentGenerationRequired,
    GenerationDescriptor,
)
from experiments.provider_generation_history.supported import SupportedHistoricalSharedAnchorLedger
from experiments.shared_anchor_intent_ledger.protocol import Intent


def descriptor(generation, key):
    return GenerationDescriptor("anchor-A", generation, key.hex())


def attested(provider, generation, key):
    verifier = AttestationVerifier(
        {("anchor-A", generation): key}, ProviderIdentity("anchor-A", generation)
    )
    return AttestedCatchup(provider, verifier)


class RotateDuringReauthenticationLedger(SupportedHistoricalSharedAnchorLedger):
    def arm_rotation(self, new, proof, new_attested):
        self._rotation_during_reauth = (new, proof, new_attested)

    def _reauthenticate(self, entry):
        binding = super()._reauthenticate(entry)
        pending = getattr(self, "_rotation_during_reauth", None)
        if pending is not None:
            self._rotation_during_reauth = None
            self.rotate_provider(*pending)
        return binding


class VerifyComponentRotationRaceTests(unittest.TestCase):
    def test_rotation_before_watermark_commit_rejects_stale_generation_read(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "shared.db"
            k1 = b"provider-key-1"
            k2 = b"provider-key-2"
            g1 = descriptor(1, k1)
            g2 = descriptor(2, k2)
            p1 = FencedActivationProvider("anchor-A", 1, k1, value=0)
            ledger = RotateDuringReauthenticationLedger(
                path, attested(p1, 1, k1), g1
            )

            ledger.execute(Intent("i1", "component-A", "migration", {"x": 1}))
            self.assertEqual(ledger.watermark("component-A"), 0)

            p2 = FencedActivationProvider("anchor-A", 2, k2, value=1)
            ledger.arm_rotation(
                g2,
                ledger.provider_history.make_transition(g1, g2),
                attested(p2, 2, k2),
            )

            with self.assertRaises(CurrentGenerationRequired):
                ledger.verify_component("component-A")

            self.assertEqual(ledger.provider_history.current().generation, 2)
            self.assertEqual(ledger.watermark("component-A"), 0)


if __name__ == "__main__":
    unittest.main()
