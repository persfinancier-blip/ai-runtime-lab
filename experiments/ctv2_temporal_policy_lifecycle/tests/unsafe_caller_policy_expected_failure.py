import unittest
from experiments.ctv2_temporal_log_eligibility.protocol import Policy,EvaluationMode,Evidence
from experiments.ctv2_temporal_policy_lifecycle.tests.test_protocol import trusts
from experiments.ctv2_temporal_policy_lifecycle.protocol import unsafe_evaluate
class Unsafe(unittest.TestCase):
 def test_weak_policy_should_not_pass_but_does(self):
  self.assertFalse(unsafe_evaluate(Policy(1,0,EvaluationMode.HISTORICAL),trusts(),policy_time=250,evidence=(Evidence('A','FULFILLED',50),)),'caller-selected stale weak policy was accepted')
if __name__=='__main__': unittest.main()
