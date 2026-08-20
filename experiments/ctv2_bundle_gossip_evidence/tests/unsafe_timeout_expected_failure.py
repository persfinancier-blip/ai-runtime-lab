import unittest
from experiments.ctv2_bundle_gossip_evidence.protocol import UnsafeTimeoutClassifier
class Unsafe(unittest.TestCase):
 def test_timeout_not_split(self): self.assertNotEqual(UnsafeTimeoutClassifier().classify_timeout(),'SPLIT_VIEW')
if __name__=='__main__': unittest.main()
