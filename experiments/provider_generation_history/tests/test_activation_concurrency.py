import threading
import time
import unittest

from experiments.provider_generation_history.activation import (
    ActivationFenced,
    FencedActivationProvider,
)


class SlowFenceState:
    """Test double that widens the pre-fix next-fence race deterministically enough.

    The real ActivationState now serializes this state through its lock. This double
    preserves that contract while making an unlocked `next_fence += 1` overlap long
    enough for two synchronized workers to observe the same pre-reservation state.
    """

    def __init__(self):
        self._next_fence = 0
        self.pending = None
        self.committed = {}
        self.lock = threading.RLock()

    @property
    def next_fence(self):
        value = self._next_fence
        time.sleep(0.05)
        return value

    @next_fence.setter
    def next_fence(self, value):
        self._next_fence = value


class ProviderActivationConcurrencyTests(unittest.TestCase):
    def test_concurrent_distinct_prepare_has_single_winner(self):
        state = SlowFenceState()
        provider = FencedActivationProvider(
            provider_id="anchor-A",
            generation=2,
            value=10,
            activation_state=state,
        )
        start = threading.Barrier(3)
        results = []
        errors = []

        def worker(activation_id):
            start.wait()
            try:
                results.append(
                    provider.prepare_activation(
                        expected_position=10,
                        activation_id=activation_id,
                    )
                )
            except Exception as exc:  # capture exact competing outcome for assertion
                errors.append(exc)

        threads = [
            threading.Thread(target=worker, args=("rotate-2-a",)),
            threading.Thread(target=worker, args=("rotate-2-b",)),
        ]
        for thread in threads:
            thread.start()
        start.wait()
        for thread in threads:
            thread.join(timeout=2)
            self.assertFalse(thread.is_alive(), "activation prepare worker deadlocked")

        self.assertEqual(len(results), 1)
        self.assertEqual(len(errors), 1)
        self.assertIsInstance(errors[0], ActivationFenced)
        self.assertEqual(state.pending, results[0])
        self.assertEqual(results[0].fence, 1)

    def test_prepare_and_increment_share_same_provider_lock(self):
        state = SlowFenceState()
        provider = FencedActivationProvider(generation=2, value=10, activation_state=state)
        start = threading.Barrier(3)
        results = []
        errors = []

        def prepare_worker():
            start.wait()
            try:
                results.append(provider.prepare_activation(expected_position=10, activation_id="rotate-2"))
            except Exception as exc:
                errors.append(exc)

        def increment_worker():
            start.wait()
            try:
                provider.increment(expected=10, challenge="concurrent", request_id="concurrent")
                results.append("increment")
            except Exception as exc:
                errors.append(exc)

        threads = [threading.Thread(target=prepare_worker), threading.Thread(target=increment_worker)]
        for thread in threads:
            thread.start()
        start.wait()
        for thread in threads:
            thread.join(timeout=2)
            self.assertFalse(thread.is_alive(), "provider operation worker deadlocked")

        # The two operations must be serializable. Either increment linearizes first
        # and prepare then sees position 11, or prepare linearizes first and increment
        # is fenced. They must never both succeed from position 10.
        self.assertFalse(
            any(getattr(item, "activation_id", None) == "rotate-2" for item in results)
            and "increment" in results
        )
        self.assertEqual(provider.value, 10 if state.pending is not None else 11)


if __name__ == "__main__":
    unittest.main()
