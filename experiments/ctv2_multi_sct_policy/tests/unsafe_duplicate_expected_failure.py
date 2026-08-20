import unittest
from experiments.ctv2_multi_sct_policy.protocol import unsafe_count_claims
class Unsafe(unittest.TestCase):
 def test_duplicate(self): self.assertFalse(unsafe_count_claims(2,[{'log_id':'x','status':'FULFILLED'},{'log_id':'x','status':'FULFILLED'}]))
if __name__=='__main__': unittest.main()
