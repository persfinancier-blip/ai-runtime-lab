import tempfile, unittest
from experiments.transition_history_pruning.tests.test_protocol import Builder
from experiments.transition_history_pruning.protocol import UnsafeDeleteFirst

class UnsafeExpectedFailure(unittest.TestCase):
    def test_delete_first_should_preserve_restart_but_does_not(self):
        with tempfile.TemporaryDirectory() as td:
            b=Builder(td).append(5)
            UnsafeDeleteFirst().prune(b.db,3)
            self.assertEqual(b.h.verify_restart()["sequence"],5)

if __name__=="__main__": unittest.main()
