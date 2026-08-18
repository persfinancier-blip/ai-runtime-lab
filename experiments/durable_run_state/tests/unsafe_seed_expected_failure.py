import unittest

from experiments.durable_run_state.protocol import UnsafeCounter, UnknownOutcome


class UnsafeBaseline(unittest.TestCase):
    def test_naive_retry_should_not_duplicate_but_does(self):
        counter = UnsafeCounter()
        try:
            counter.apply_then_timeout()
        except UnknownOutcome:
            counter.apply()
        self.assertEqual(counter.count, 1, "unsafe retry duplicated the external side effect")


if __name__ == "__main__":
    unittest.main()
