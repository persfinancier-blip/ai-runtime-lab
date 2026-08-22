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


class StrictEnablementTypes(unittest.TestCase):
    def setUp(self):
        self.raw = [b"a", b"b", b"c"]
        self.authority = RotationAuthority(
            "rot",
            1,
            1,
            2,
            {key_id(k): k.hex() for k in self.raw},
        )

    def valid(self):
        base = ThresholdEnablement(
            "f" * 64,
            1,
            self.authority.authority_id,
            1,
            1,
            (),
        )
        signatures = tuple(
            Signature(key_id(k), mac(k, base.payload)) for k in self.raw[:2]
        )
        return ThresholdEnablement(
            base.start_provider_generation_id,
            base.start_provider_generation,
            base.authority_id,
            base.authority_version,
            base.authority_generation,
            signatures,
        )

    def test_bool_provider_generation_rejected(self):
        e = self.valid()
        bad = ThresholdEnablement(
            e.start_provider_generation_id,
            True,
            e.authority_id,
            e.authority_version,
            e.authority_generation,
            e.signatures,
        )
        with self.assertRaises(ThresholdNotMet):
            verify_enablement(self.authority, bad)

    def test_bool_authority_version_rejected(self):
        e = self.valid()
        bad = ThresholdEnablement(
            e.start_provider_generation_id,
            e.start_provider_generation,
            e.authority_id,
            True,
            e.authority_generation,
            e.signatures,
        )
        with self.assertRaises(ThresholdNotMet):
            verify_enablement(self.authority, bad)

    def test_noncanonical_uppercase_digest_rejected(self):
        e = self.valid()
        bad = ThresholdEnablement(
            e.start_provider_generation_id.upper(),
            e.start_provider_generation,
            e.authority_id,
            e.authority_version,
            e.authority_generation,
            e.signatures,
        )
        with self.assertRaises(ThresholdNotMet):
            verify_enablement(self.authority, bad)


if __name__ == "__main__":
    unittest.main()
