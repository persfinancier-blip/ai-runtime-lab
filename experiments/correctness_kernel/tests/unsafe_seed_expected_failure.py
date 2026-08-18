import tempfile
import unittest

from experiments.correctness_kernel.kernel import Kernel
from experiments.memory_safety.memory_safety import Memory


class UnsafeComposition(unittest.TestCase):
    def test_narrative_must_not_be_authoritative_completion(self):
        with tempfile.TemporaryDirectory() as root:
            kernel = Kernel(root)
            kernel.memory.add(
                Memory.make("status", "done successfully", 1.0, trust="verified")
            )
            self.assertFalse(
                kernel.naive_done_from_narrative("status"),
                "seeded bug: downstream completion trusted advisory narrative",
            )


if __name__ == "__main__":
    unittest.main()
