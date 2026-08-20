import unittest
from experiments.ctv2_temporal_log_eligibility.protocol import *
def L(log,op,state,since,profile='p1',op_since=None): return SnapshotLog(log,profile,op,op_since if op_since is not None else since,state,since)
def S(id,v,t,logs,exp=1000): return AuthenticatedSnapshot(id,v,v,t,exp,tuple(logs))
class TemporalTests(unittest.TestCase):
    def history(self):
        h=AuthenticatedLifecycleHistory(); h.add_accepted(S('s1',1,100,[L('A','op1',LogState.ACTIVE,80,op_since=70),L('B','op2',LogState.ACTIVE,90,op_since=75)])); h.add_accepted(S('s2',2,200,[L('A','op1',LogState.RETIRED,180,op_since=70),L('B','op3',LogState.ACTIVE,90,op_since=170)])); h.add_accepted(S('s3',3,300,[L('A','op1',LogState.DISTRUSTED,250,op_since=70),L('B','op3',LogState.RETIRED,280,op_since=170)])); return h
    def test_active_interval_historical_contributes(self):
        d=evaluate(self.history(),Policy(1,1,EvaluationMode.HISTORICAL),policy_time=300,evidence=[Evidence('A','FULFILLED',150)]); self.assertTrue(d.compliant); self.assertEqual(d.fulfilled_operators,('op1',))
    def test_before_activation_does_not_contribute(self):
        d=evaluate(self.history(),Policy(1,0,EvaluationMode.HISTORICAL),policy_time=300,evidence=[Evidence('A','FULFILLED',70)]); self.assertFalse(d.compliant)
    def test_after_retirement_current_policy_does_not_contribute(self):
        d=evaluate(self.history(),Policy(1,0,EvaluationMode.CURRENT_POLICY),policy_time=220,evidence=[Evidence('A','FULFILLED',150)]); self.assertFalse(d.compliant)
    def test_later_retirement_does_not_rewrite_historical_attribution(self):
        d=evaluate(self.history(),Policy(1,1,EvaluationMode.HISTORICAL),policy_time=300,evidence=[Evidence('A','FULFILLED',150)]); self.assertTrue(d.compliant)
    def test_operator_reassignment_resolved_at_evidence_time(self):
        old=evaluate(self.history(),Policy(1,1,EvaluationMode.HISTORICAL),policy_time=300,evidence=[Evidence('B','FULFILLED',150)]); new=evaluate(self.history(),Policy(1,1,EvaluationMode.HISTORICAL),policy_time=300,evidence=[Evidence('B','FULFILLED',180)]); self.assertEqual(old.fulfilled_operators,('op2',)); self.assertEqual(new.fulfilled_operators,('op3',))
    def test_boundaries_are_start_inclusive_end_exclusive(self):
        h=self.history(); before=evaluate(h,Policy(1,0,EvaluationMode.HISTORICAL),policy_time=300,evidence=[Evidence('A','FULFILLED',179)]); at=evaluate(h,Policy(1,0,EvaluationMode.HISTORICAL),policy_time=300,evidence=[Evidence('A','FULFILLED',180)]); self.assertTrue(before.compliant); self.assertFalse(at.compliant)
    def test_stale_snapshot_cherry_pick_rejected(self):
        with self.assertRaises(SnapshotCherryPick): evaluate(self.history(),Policy(1,0,EvaluationMode.CURRENT_POLICY),policy_time=300,requested_snapshot_id='s1',evidence=[Evidence('A','FULFILLED',150)])
    def test_frozen_metadata_rejected(self):
        h=AuthenticatedLifecycleHistory(); h.add_accepted(S('s1',1,100,[L('A','op',LogState.ACTIVE,80)],exp=150))
        with self.assertRaises(FreezeOrRollback): evaluate(h,Policy(1,0,EvaluationMode.HISTORICAL),policy_time=151,evidence=[Evidence('A','FULFILLED',120)])
    def test_decision_persists_policy_evidence_and_snapshot_identity(self):
        d=evaluate(self.history(),Policy(1,1,EvaluationMode.HISTORICAL),policy_time=300,evidence=[Evidence('A','FULFILLED',150)]); self.assertEqual((d.policy_time,d.authority_snapshot_id,d.authority_snapshot_version,d.authority_snapshot_generation),(300,'s3',3,3)); self.assertEqual(d.evidence_times,(('A',150),))
    def test_current_policy_uses_new_distrust_even_for_old_evidence(self):
        d=evaluate(self.history(),Policy(1,0,EvaluationMode.CURRENT_POLICY),policy_time=300,evidence=[Evidence('A','FULFILLED',150)]); self.assertFalse(d.compliant)
    def test_historical_operator_diversity_not_current_operator_diversity(self):
        d=evaluate(self.history(),Policy(2,2,EvaluationMode.HISTORICAL),policy_time=300,evidence=[Evidence('A','FULFILLED',150),Evidence('B','FULFILLED',150)]); self.assertTrue(d.compliant); self.assertEqual(d.fulfilled_operators,('op1','op2'))
    def test_same_timestamp_conflicting_state_is_rejected_at_compile(self):
        h=AuthenticatedLifecycleHistory(); h.add_accepted(S('s1',1,100,[L('A','op',LogState.ACTIVE,80)])); h.add_accepted(S('s2',2,200,[L('A','op',LogState.RETIRED,80)]))
        with self.assertRaises(HistoryConflict): evaluate(h,Policy(1,0,EvaluationMode.HISTORICAL),policy_time=200,evidence=[Evidence('A','FULFILLED',90)])
    def test_future_evidence_rejected(self):
        with self.assertRaises(Malformed): evaluate(self.history(),Policy(1,0,EvaluationMode.HISTORICAL),policy_time=200,evidence=[Evidence('A','FULFILLED',201)])
    def test_operator_boundary_is_start_inclusive_end_exclusive(self):
        h=self.history(); before=evaluate(h,Policy(1,1,EvaluationMode.HISTORICAL),policy_time=300,evidence=[Evidence('B','FULFILLED',169)]); at=evaluate(h,Policy(1,1,EvaluationMode.HISTORICAL),policy_time=300,evidence=[Evidence('B','FULFILLED',170)]); self.assertEqual(before.fulfilled_operators,('op2',)); self.assertEqual(at.fulfilled_operators,('op3',))
    def test_bool_time_rejected(self):
        with self.assertRaises(Malformed): evaluate(self.history(),Policy(1,0,EvaluationMode.HISTORICAL),policy_time=True,evidence=[])
if __name__=='__main__': unittest.main()
