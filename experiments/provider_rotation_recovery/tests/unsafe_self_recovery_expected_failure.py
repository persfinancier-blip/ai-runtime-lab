import unittest
from experiments.provider_rotation_recovery.protocol import UnsafeSelfAuthorizedRecovery


class Unsafe(unittest.TestCase):
    def test_normal_authority_should_not_self_recover_but_does(self):
        self.assertFalse(UnsafeSelfAuthorizedRecovery.allows(True))


if __name__ == "__main__":
    unittest.main()
