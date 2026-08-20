import unittest
from experiments.ctv2_policy_trust_bundle.protocol import UnsafeSplitHistories
class UnsafeMixAndMatch(unittest.TestCase):
    def test_independent_histories_should_not_accept_mixed_release_but_do(self):
        u=UnsafeSplitHistories(); u.update_policy(2,'policy-release-2'); u.update_trust(1,'trust-release-1')
        self.assertFalse(u.current_pair_is_coherent(),'unsafe independent histories accepted a policy/trust mix-and-match pair')
if __name__=='__main__': unittest.main()
