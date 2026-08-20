import tempfile
import unittest
from pathlib import Path
from experiments.signed_history_compaction.protocol import SignedPrunableHistory, UnsafeDeleteFirst
from experiments.signed_history_compaction.tests.test_protocol import ChainBuilder

class UnsafeBaseline(unittest.TestCase):
    def test_delete_first_should_preserve_restart_but_does_not(self):
        with tempfile.TemporaryDirectory() as td:
            td=Path(td); b=ChainBuilder(td/'db').append(5); layer=SignedPrunableHistory(b.store,td/'a')
            UnsafeDeleteFirst().prune(td/'db',3)
            self.assertEqual(layer.verify_restart()['sequence'],5)

if __name__=='__main__': unittest.main()
