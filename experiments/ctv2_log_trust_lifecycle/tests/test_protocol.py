import unittest
from experiments.ctv2_log_trust_lifecycle.protocol import *
ROOT=b'pinned-trust-root'; OPS=(Operator('op-a','Operator A'),Operator('op-b','Operator B'))
LOG_A=LogEntry('log-a','ed25519:key-a','op-a',LogState.ACTIVE,100); LOG_B=LogEntry('log-b','ed25519:key-b','op-b',LogState.ACTIVE,100)
def snapshot(version=1,generation=1,issued_at=100,expires_at=1000,logs=(LOG_A,LOG_B),operators=OPS,key=ROOT): return sign_snapshot(key,version=version,generation=generation,issued_at=issued_at,expires_at=expires_at,operators=operators,logs=logs)
class TrustLifecycleTests(unittest.TestCase):
 def test_authenticated_snapshot_drives_operator_diversity(self):
  s=snapshot(); life=TrustLifecycle(ROOT); life.accept(s); d=evaluate(Policy(2,2),s,expected_snapshot_id=s.snapshot_id,evidence=(Evidence('log-a','FULFILLED'),Evidence('log-b','FULFILLED'))); self.assertTrue(d.compliant); self.assertEqual(d.fulfilled_operators,('op-a','op-b'))
 def test_unknown_log_cannot_self_promote(self):
  s=snapshot(); d=evaluate(Policy(1,1),s,expected_snapshot_id=s.snapshot_id,evidence=(Evidence('attacker-log','FULFILLED'),)); self.assertFalse(d.compliant); self.assertEqual(d.ignored_logs,('attacker-log',))
 def test_caller_cannot_self_assert_operator_identity(self):
  s=snapshot(); d=evaluate(Policy(2,2),s,expected_snapshot_id=s.snapshot_id,evidence=(Evidence('log-a','FULFILLED'),Evidence('log-a','FULFILLED'))); self.assertFalse(d.compliant); self.assertEqual(d.fulfilled_operators,('op-a',))
 def test_rollback_rejected(self):
  life=TrustLifecycle(ROOT); life.accept(snapshot(2,2,200));
  with self.assertRaises(SnapshotRollback): life.accept(snapshot(1,1,100))
 def test_same_coordinate_substitution_rejected(self):
  life=TrustLifecycle(ROOT); life.accept(snapshot())
  with self.assertRaises(SnapshotSubstitution): life.accept(snapshot(logs=(LOG_A,)))
 def test_forged_snapshot_rejected(self):
  s=snapshot(); forged=SignedSnapshot(**{**s.__dict__,'authenticator':'00'*32})
  with self.assertRaises(SnapshotAuthError): TrustLifecycle(ROOT).accept(forged)
 def test_distrust_stops_future_counting_but_history_is_attributable(self):
  life=TrustLifecycle(ROOT); old=snapshot(); life.accept(old); oldd=evaluate(Policy(2,2),old,expected_snapshot_id=old.snapshot_id,evidence=(Evidence('log-a','FULFILLED'),Evidence('log-b','FULFILLED'))); dead=LogEntry('log-a','ed25519:key-a','op-a',LogState.DISTRUSTED,200); new=snapshot(2,2,200,logs=(dead,LOG_B)); life.accept(new); newd=evaluate(Policy(2,2),new,expected_snapshot_id=new.snapshot_id,evidence=(Evidence('log-a','FULFILLED'),Evidence('log-b','FULFILLED'))); self.assertTrue(oldd.compliant); self.assertEqual(life.get(oldd.snapshot_id).logs[0].operator_id,'op-a'); self.assertFalse(newd.compliant); self.assertIn('log-a',newd.ignored_logs)
 def test_operator_reassignment_requires_new_generation_and_preserves_history(self):
  life=TrustLifecycle(ROOT); old=snapshot(); life.accept(old); moved=LogEntry('log-a','ed25519:key-a','op-b',LogState.ACTIVE,200); new=snapshot(2,2,200,logs=(moved,LOG_B)); life.accept(new); self.assertEqual(life.get(old.snapshot_id).logs[0].operator_id,'op-a'); self.assertEqual({x.log_id:x.operator_id for x in new.logs}['log-a'],'op-b')
 def test_profile_is_immutable_for_log_id(self):
  life=TrustLifecycle(ROOT); life.accept(snapshot()); changed=LogEntry('log-a','ed25519:DIFFERENT','op-a',LogState.ACTIVE,200)
  with self.assertRaises(ImmutableProfileError): life.accept(snapshot(2,2,200,logs=(changed,LOG_B)))
 def test_exact_snapshot_identity_is_required(self):
  s=snapshot()
  with self.assertRaises(SnapshotBindingError): evaluate(Policy(1,1),s,expected_snapshot_id='wrong',evidence=(Evidence('log-a','FULFILLED'),))
 def test_duplicate_log_and_operator_rejected(self):
  with self.assertRaises(SnapshotMalformed): snapshot(logs=(LOG_A,LOG_A))
  with self.assertRaises(SnapshotMalformed): snapshot(operators=(OPS[0],OPS[0]))
 def test_unknown_operator_membership_rejected(self):
  orphan=LogEntry('log-x','ed25519:key-x','op-missing',LogState.ACTIVE,100)
  with self.assertRaises(SnapshotMalformed): snapshot(logs=(orphan,))
 def test_distrusted_log_cannot_reactivate(self):
  life=TrustLifecycle(ROOT); dead=LogEntry('log-a','ed25519:key-a','op-a',LogState.DISTRUSTED,100); life.accept(snapshot(logs=(dead,LOG_B))); alive=LogEntry('log-a','ed25519:key-a','op-a',LogState.ACTIVE,200)
  with self.assertRaises(SnapshotMalformed): life.accept(snapshot(2,2,200,logs=(alive,LOG_B)))
 def test_expired_snapshot_rejected_at_acceptance(self):
  with self.assertRaises(SnapshotRollback): TrustLifecycle(ROOT).accept(snapshot(),now=1001)
 def test_future_lifecycle_timestamp_rejected(self):
  future=LogEntry('log-x','ed25519:key-x','op-a',LogState.ACTIVE,101)
  with self.assertRaises(SnapshotMalformed): snapshot(logs=(future,))
 def test_retired_log_cannot_reactivate(self):
  life=TrustLifecycle(ROOT); retired=LogEntry('log-a','ed25519:key-a','op-a',LogState.RETIRED,100); life.accept(snapshot(logs=(retired,LOG_B))); alive=LogEntry('log-a','ed25519:key-a','op-a',LogState.ACTIVE,200)
  with self.assertRaises(SnapshotMalformed): life.accept(snapshot(2,2,200,logs=(alive,LOG_B)))
 def test_strict_integer_validation_rejects_bool(self):
  s=snapshot(); bad=SignedSnapshot(**{**s.__dict__,'generation':True})
  with self.assertRaises(SnapshotMalformed): TrustLifecycle(ROOT).accept(bad)
if __name__=='__main__': unittest.main()
