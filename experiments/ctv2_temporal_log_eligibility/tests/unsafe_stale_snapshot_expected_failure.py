import unittest
from experiments.ctv2_temporal_log_eligibility.protocol import *
class UnsafeBaseline(unittest.TestCase):
    def test_stale_snapshot_can_bypass_later_retirement(self):
        old=AuthenticatedSnapshot('old',1,1,100,1000,(SnapshotLog('A','p','op',70,LogState.ACTIVE,80),)); ev=[Evidence('A','FULFILLED',150)]
        self.assertFalse(unsafe_current_snapshot_evaluate(old,1,ev),'unsafe caller-selected stale snapshot bypassed retirement')
if __name__=='__main__': unittest.main()
