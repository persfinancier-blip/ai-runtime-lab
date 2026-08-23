import unittest
from experiments.provider_recovery_authority_lifecycle.protocol import UnsafeRecoveryOnlySwap


class Unsafe(unittest.TestCase):
    def test_recovery_quorum_should_not_self_replace_but_does(self):
        self.assertFalse(UnsafeRecoveryOnlySwap.allows(True))


if __name__ == "__main__":
    unittest.main()
