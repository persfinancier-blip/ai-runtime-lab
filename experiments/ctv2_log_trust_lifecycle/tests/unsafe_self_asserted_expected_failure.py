import unittest
from experiments.ctv2_log_trust_lifecycle.protocol import unsafe_evaluate
class UnsafeTrustBaseline(unittest.TestCase):
 def test_self_asserted_trust_and_operator_diversity_should_fail_but_passes(self):
  claims=[{'log_id':'log-a','operator_id':'operator-A','trusted':True,'status':'FULFILLED'},{'log_id':'log-b','operator_id':'operator-B','trusted':True,'status':'FULFILLED'}]
  self.assertFalse(unsafe_evaluate(2,2,claims),'caller self-asserted trust/operator metadata satisfied policy')
if __name__=='__main__': unittest.main()
