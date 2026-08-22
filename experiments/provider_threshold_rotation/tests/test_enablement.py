import unittest

from experiments.provider_threshold_rotation.enablement import (
    ThresholdEnablement,
    verify_enablement,
)
from experiments.provider_threshold_rotation.protocol import (
    RotationAuthority,
    Signature,
    ThresholdNotMet,
    key_id,
    mac,
)


class Tests(unittest.TestCase):
    def setUp(self):
        self.raw = [b"a", b"b", b"c"]
        keys = {key_id(k): k.hex() for k in self.raw}
        self.a = RotationAuthority("rot", 1, 1, 2, keys)

    def proof(self, start=3):
        e = ThresholdEnablement("f" * 64, start, self.a.authority_id, 1, 1, ())
        sigs = tuple(
            Signature(key_id(k), mac(k, e.payload)) for k in self.raw[:2]
        )
        return ThresholdEnablement(
            e.start_provider_generation_id,
            e.start_provider_generation,
            e.authority_id,
            e.authority_version,
            e.authority_generation,
            sigs,
        )

    def test_valid_enablement(self):
        self.assertEqual(len(verify_enablement(self.a, self.proof())), 2)

    def test_cutoff_substitution_rejected(self):
        e = self.proof(3)
        changed = ThresholdEnablement(
            e.start_provider_generation_id,
            4,
            e.authority_id,
            e.authority_version,
            e.authority_generation,
            e.signatures,
        )
        with self.assertRaises(ThresholdNotMet):
            verify_enablement(self.a, changed)

    def test_authority_substitution_rejected(self):
        e = self.proof()
        changed = ThresholdEnablement(
            e.start_provider_generation_id,
            e.start_provider_generation,
            "0" * 64,
            e.authority_version,
            e.authority_generation,
            e.signatures,
        )
        with self.assertRaises(ThresholdNotMet):
            verify_enablement(self.a, changed)


if __name__ == "__main__":
    unittest.main()
