import unittest
from experiments.ctv2_observer_registry.protocol import *
class U(unittest.TestCase):
 def test_sybil_should_not_make_quorum_but_does(self):
  class E:
   def __init__(self,i): self.observer_id=i
  self.assertFalse(UnsafeSelfAssertedMembership().quorum([E("s1"),E("s2")],2))
if __name__=="__main__":unittest.main()
