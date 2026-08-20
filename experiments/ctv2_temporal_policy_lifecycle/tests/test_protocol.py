import unittest
from dataclasses import replace
from experiments.ctv2_temporal_log_eligibility.protocol import AuthenticatedLifecycleHistory,AuthenticatedSnapshot,SnapshotLog,LogState,Evidence,EvaluationMode,Policy
from experiments.ctv2_temporal_policy_lifecycle.protocol import AuthenticatedPolicyHistory,PolicySnapshot,PolicyRollback,PolicyIntervalConflict,PolicyCompatibilityError,ReplayMismatch,evaluate,replay

def trusts():
 h=AuthenticatedLifecycleHistory(); h.add_accepted(AuthenticatedSnapshot('t1',1,1,10,1000,(SnapshotLog('A','p','op1',1,LogState.ACTIVE,1),SnapshotLog('B','p','op2',1,LogState.ACTIVE,1)))); h.add_accepted(AuthenticatedSnapshot('t2',2,2,200,1000,(SnapshotLog('A','p','op1',1,LogState.ACTIVE,1),SnapshotLog('B','p','op2',1,LogState.ACTIVE,1)))); return h
def policies():
 h=AuthenticatedPolicyHistory(); h.add_accepted(PolicySnapshot('ct',1,1,10,1000,10,200,1,0,EvaluationMode.HISTORICAL,1,1)); h.add_accepted(PolicySnapshot('ct',2,2,150,1000,200,None,2,2,EvaluationMode.CURRENT_POLICY,2,None)); return h
EV=(Evidence('A','FULFILLED',50),Evidence('B','FULFILLED',50))
class T(unittest.TestCase):
 def test_selects_by_time(self): self.assertEqual(evaluate(policies(),trusts(),policy_time=100,evidence=EV).policy_version,1); self.assertEqual(evaluate(policies(),trusts(),policy_time=250,evidence=EV).policy_version,2)
 def test_no_downgrade(self): self.assertFalse(evaluate(policies(),trusts(),policy_time=250,evidence=(EV[0],)).compliant)
 def test_future_not_rewrite(self):
  d=evaluate(policies(),trusts(),policy_time=100,evidence=EV); self.assertEqual(replay(d,policies(),trusts(),EV),d)
 def test_replay_exact(self):
  d=evaluate(policies(),trusts(),policy_time=250,evidence=EV); self.assertEqual(replay(d,policies(),trusts(),EV),d)
 def test_interval_join(self):
  h=AuthenticatedPolicyHistory(); h.add_accepted(PolicySnapshot('p',1,1,10,1000,10,200,1,0,EvaluationMode.HISTORICAL,1,None))
  with self.assertRaises(PolicyIntervalConflict): h.add_accepted(PolicySnapshot('p',2,2,20,1000,201,None,1,0,EvaluationMode.HISTORICAL,1,None))
 def test_policy_lineage_substitution(self):
  h=AuthenticatedPolicyHistory(); h.add_accepted(PolicySnapshot('p',1,1,10,1000,10,200,1,0,EvaluationMode.HISTORICAL,1,None))
  with self.assertRaises(Exception): h.add_accepted(PolicySnapshot('evil',2,2,20,1000,200,None,1,0,EvaluationMode.HISTORICAL,1,None))
 def test_rollback(self):
  with self.assertRaises(PolicyRollback): policies().add_accepted(PolicySnapshot('ct',2,3,300,1000,300,None,1,0,EvaluationMode.HISTORICAL,1,None))
 def test_substitution(self):
  d=evaluate(policies(),trusts(),policy_time=100,evidence=EV)
  with self.assertRaises(Exception): replay(replace(d,policy_digest='0'*64),policies(),trusts(),EV)
 def test_persists_ids(self):
  d=evaluate(policies(),trusts(),policy_time=250,evidence=EV); self.assertEqual((d.policy_version,d.policy_generation,d.trust_version,d.trust_generation),(2,2,2,2))
 def test_future_policy_not_early(self): self.assertEqual(evaluate(policies(),trusts(),policy_time=199,evidence=EV).policy_version,1)
 def test_mix_match(self):
  h=AuthenticatedPolicyHistory(); h.add_accepted(PolicySnapshot('p',1,1,10,1000,10,None,1,0,EvaluationMode.HISTORICAL,2,2))
  with self.assertRaises(PolicyCompatibilityError): evaluate(h,trusts(),policy_time=100,evidence=EV)
 def test_evidence_change_breaks_replay(self):
  d=evaluate(policies(),trusts(),policy_time=250,evidence=EV)
  with self.assertRaises(ReplayMismatch): replay(d,policies(),trusts(),(EV[0],))
 def test_expiry(self):
  h=AuthenticatedPolicyHistory(); h.add_accepted(PolicySnapshot('p',1,1,10,50,10,None,1,0,EvaluationMode.HISTORICAL,1,None))
  with self.assertRaises(Exception): evaluate(h,trusts(),policy_time=100,evidence=EV)
if __name__=='__main__': unittest.main()
