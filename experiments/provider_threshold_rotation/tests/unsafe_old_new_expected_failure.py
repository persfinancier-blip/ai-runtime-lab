import unittest
from experiments.provider_threshold_rotation.protocol import UnsafeOldAndNewOnly


class Unsafe(unittest.TestCase):
    def test_compromised_old_and_attacker_new_should_not_be_enough_but_is(self):
        self.assertFalse(UnsafeOldAndNewOnly.allows(True, True))


if __name__ == "__main__":
    unittest.main()
