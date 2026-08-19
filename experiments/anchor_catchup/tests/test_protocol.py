import tempfile,threading,unittest
from pathlib import Path
from experiments.anchor_catchup.protocol import *
S1=b'authority-key-generation-1'; S2=b'authority-key-generation-2'
class T(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(); self.db=CatchupDB(Path(self.tmp.name)/'s.db'); self.a=MonotonicAnchor(); self.p=CatchupProtocol(self.db,self.a,{(1,1):S1,(2,2):S2})
 def tearDown(self): self.tmp.cleanup()
 def pub(self): return self.db.publish(S1,task_id='task-A',payload_digest='sha256:aaa')
 def test_success(self): self.pub(); e=self.p.reconcile(); self.assertEqual((e.sequence,e.anchor_position),(1,1)); self.assertTrue(self.p.consequential_continuation_allowed())
 def test_restart(self): self.pub(); p2=CatchupProtocol(self.db,self.a,{(1,1):S1}); self.assertFalse(p2.consequential_continuation_allowed()); p2.reconcile(); self.assertTrue(p2.consequential_continuation_allowed())
 def test_unknown_reconcile_no_retry(self):
  self.pub();
  with self.assertRaises(AnchorUnknownOutcome): self.p.reconcile(timeout_after_commit=True)
  calls=self.a.increment_calls; self.assertEqual(self.a.read(),1); e=self.p.reconcile(); self.assertEqual(e.outcome,'ALREADY_ALIGNED'); self.assertEqual(self.a.increment_calls,calls)
 def test_duplicate(self): self.pub(); self.p.reconcile(); calls=self.a.increment_calls; self.p.reconcile(); self.assertEqual(self.a.increment_calls,calls)
 def test_concurrent(self):
  self.pub(); barrier=threading.Barrier(2); errs=[]
  def worker():
   try:
    observed=self.a.read(); barrier.wait(2)
    try:self.a.increment(expected=observed)
    except AnchorConflict: pass
    CatchupProtocol(self.db,self.a,{(1,1):S1}).reconcile()
   except Exception as e: errs.append(e)
  ts=[threading.Thread(target=worker) for _ in range(2)]; [t.start() for t in ts]; [t.join() for t in ts]; self.assertFalse(errs,errs); self.assertEqual(self.a.read(),1)
 def test_anchor_ahead(self): self.pub(); self.a.value=2; self.assertRaises(AnchorMismatch,self.p.reconcile); self.assertFalse(self.p.consequential_continuation_allowed())
 def test_bad_proof(self):
  self.pub(); c=self.db.connect(); c.execute("UPDATE anchor_intent SET proof_mac='forged' WHERE sequence=1"); c.close(); self.assertRaises(ProofError,self.p.reconcile); self.assertEqual(self.a.read(),0)
 def test_one_pending(self): self.pub(); self.assertRaises(PendingAnchor,self.db.publish,S1,task_id='task-B',payload_digest='b')
 def test_rotation_fenced(self):
  self.pub(); self.assertRaises(PendingAnchor,self.db.rotate,S2,expected_epoch=1,new_epoch=2,new_key_generation=2); self.p.reconcile(); self.db.rotate(S2,expected_epoch=1,new_epoch=2,new_key_generation=2); self.assertEqual(self.db.authority(),(2,2,2)); self.assertFalse(self.p.consequential_continuation_allowed()); self.p.reconcile(); self.assertTrue(self.p.consequential_continuation_allowed())
 def test_old_confirmed_record_cannot_substitute_for_rotation_anchor(self):
  old=self.pub(); self.p.reconcile(); self.db.rotate(S2,expected_epoch=1,new_epoch=2,new_key_generation=2); self.assertEqual(self.a.read(),1); self.assertFalse(self.p.consequential_continuation_allowed()); current=self.db.intent(2); self.assertNotEqual((old.authority_epoch,old.key_generation),(current.authority_epoch,current.key_generation)); self.p.reconcile(); self.assertEqual(self.a.read(),2)
 def test_unavailable(self):
  self.pub(); self.a.available=False; self.assertRaises(AnchorUnavailable,self.p.reconcile); self.assertEqual(self.db.intent(1).status,'PENDING'); self.assertFalse(self.p.consequential_continuation_allowed()); self.a.available=True; self.p.reconcile(); self.assertTrue(self.p.consequential_continuation_allowed())
 def test_evidence_no_secret(self):
  self.pub(); e=self.p.reconcile(); self.assertNotIn(S1.decode(),repr(e)); self.assertEqual(len(e.proof_ref),64)
 def test_gap_gt_one(self):
  self.pub(); c=self.db.connect(); c.execute('UPDATE authority SET global_sequence=2 WHERE singleton=1'); c.close(); self.assertRaises(ProofError,self.p.reconcile)
if __name__=='__main__': unittest.main()
