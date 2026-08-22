import unittest
from experiments.shared_anchor_intent_ledger.protocol import UnsafeMonotonicOnly


class Unsafe(unittest.TestCase):
    def test_unrelated_higher_position_should_not_be_trusted_but_is(self):
        self.assertFalse(UnsafeMonotonicOnly.accepts(0, 1))


if __name__ == "__main__":
    unittest.main()
