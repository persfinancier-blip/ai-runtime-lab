import unittest
from experiments.sink_capability_contract.protocol import *
class Unsafe(unittest.TestCase):
    def test_no_duplicate_expected(self):
        s=SimulatedSink(idempotent=False,request_bound=False,reconcile=False); UnsafeGenericRetry().execute({'op':'charge'},s); self.assertEqual(len(s.effects),1)
if __name__=='__main__': unittest.main()
