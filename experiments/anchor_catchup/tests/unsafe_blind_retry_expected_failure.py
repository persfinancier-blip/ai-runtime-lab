import unittest
from experiments.anchor_catchup.protocol import MonotonicAnchor,UnsafeBlindRetry
class Unsafe(unittest.TestCase):
 def test_blind_retry_overshoots(self):
  a=MonotonicAnchor(); UnsafeBlindRetry(a).run(); self.assertEqual(a.read(),1,'blind retry double-incremented anchor')
if __name__=='__main__': unittest.main()
