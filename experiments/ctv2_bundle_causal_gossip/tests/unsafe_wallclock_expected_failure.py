import unittest
from experiments.ctv2_bundle_causal_gossip.protocol import Unsafe
class T(unittest.TestCase):
 def test_bad(self): self.assertEqual(Unsafe().classify(100,200),"CURRENT")
if __name__=="__main__":unittest.main()
