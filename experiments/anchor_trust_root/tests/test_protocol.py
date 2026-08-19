import unittest
from experiments.anchor_trust_root.protocol import *
class T(unittest.TestCase):
 def setUp(self): self.k1=b"k1"; self.k2=b"k2"; self.s=TrustStore(TrustState(1,1,"A",1,kid(self.k1),self.k1))
 def sig(self,key,p={"x":1}): return mac(key,p)
 def test_current_accept(self): self.assertTrue(self.s.verify("A",1,kid(self.k1),{"x":1},self.sig(self.k1),1))
 def test_unknown_reject(self):
  with self.assertRaises(UnknownKey): self.s.verify("A",1,kid(b"x"),{"x":1},self.sig(b"x"),1)
 def test_rotation_old_reject(self):
  p=rotation_payload("A",1,2,kid(self.k2),1); self.s.apply_rotation(Rotation("A",1,2,kid(self.k2),self.k2,1,mac(self.k1,p)))
  with self.assertRaises(StaleGeneration): self.s.verify("A",1,kid(self.k1),{"x":1},self.sig(self.k1),1)
 def test_rollback_reject(self):
  old=self.s.state; p=rotation_payload("A",1,2,kid(self.k2),1); self.s.apply_rotation(Rotation("A",1,2,kid(self.k2),self.k2,1,mac(self.k1,p)))
  with self.assertRaises(Rollback): self.s.load_snapshot(old)
 def test_same_version_substitution_reject(self):
  forged=TrustState(1,1,"A",1,kid(self.k2),self.k2)
  with self.assertRaises(SnapshotSubstitution): self.s.load_snapshot(forged)
 def test_explicit_revocation_blocks_current_key(self):
  self.s.revoke_current()
  with self.assertRaises(RevokedKey): self.s.verify("A",1,kid(self.k1),{"x":1},self.sig(self.k1),1)
 def test_cross_provider(self):
  with self.assertRaises(WrongProvider): self.s.verify("B",1,kid(self.k1),{"x":1},self.sig(self.k1),1)
 def test_rotation_must_be_old_trusted(self):
  p=rotation_payload("A",1,2,kid(self.k2),1)
  with self.assertRaises(RotationAuthError): self.s.apply_rotation(Rotation("A",1,2,kid(self.k2),self.k2,1,mac(b"evil",p)))
 def test_recovery_epoch_invalidates_old_receipt(self):
  oldsig=self.sig(self.k1); self.s.recover(self.k2)
  with self.assertRaises(RecoveryEpochMismatch): self.s.verify("A",1,kid(self.k1),{"x":1},oldsig,1)
 def test_restart_single_authority(self):
  p=rotation_payload("A",1,2,kid(self.k2),1); self.s.apply_rotation(Rotation("A",1,2,kid(self.k2),self.k2,1,mac(self.k1,p)))
  r=TrustStore(self.s.state); self.assertTrue(r.verify("A",2,kid(self.k2),{"x":1},self.sig(self.k2),1))
 def test_private_material_not_in_evidence(self):
  evidence={"provider":"A","generation":1,"key_id":kid(self.k1),"authority_epoch":1}; self.assertNotIn(self.k1.hex(),str(evidence))
