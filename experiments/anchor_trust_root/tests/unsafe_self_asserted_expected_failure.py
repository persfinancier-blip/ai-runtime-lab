import unittest
from experiments.anchor_trust_root.protocol import *
class U(unittest.TestCase):
 def test_self_asserted_key_should_not_authorize(self):
  p={"position":9}; evil=b"evil"; self.assertFalse(UnsafeSelfAsserted().verify(p,mac(evil,p),evil))
