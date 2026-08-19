import unittest
from experiments.egress_taint.policy import Destination, EgressRequest, Sensitivity, authorize, source, unsafe_transform_drop_taint

class UnsafeSeed(unittest.TestCase):
    def test_taint_loss_must_not_enable_exfiltration_but_does(self):
        secret = source("TOP-SECRET", Sensitivity.SECRET, "vault")
        leaked = unsafe_transform_drop_taint(secret, "summary containing TOP-SECRET")
        evil = Destination("attacker.example", "untrusted", Sensitivity.SECRET)
        decision = authorize(EgressRequest(leaked, evil, "publish", None, 1))
        self.assertFalse(decision.allowed, "unsafe transform dropped taint and enabled exfiltration")

if __name__ == '__main__':
    unittest.main()
