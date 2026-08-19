import tempfile,threading,unittest
from pathlib import Path
from experiments.anchor_rotation_concurrency.protocol import *

def mk(prefix,n):
 raw=[f'{prefix}-{i}'.encode() for i in range(n)]; return raw,{key_id(k):k.hex() for k in raw}
def sigs(raw,payload,idxs): return tuple(Signature(key_id(raw[i]),sign(raw[i],payload)) for i in idxs)

class ConcurrencyTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(); self.db=Path(self.tmp.name)/'state.db'
  self.old_raw,oldkeys=mk('old',3); self.a_raw,akeys=mk('A',3); self.b_raw,bkeys=mk('B',3); self.rec_raw,reckeys=mk('rec',3)
  self.old=RootState('anchor-A',1,7,2,oldkeys); self.a=RootState('anchor-A',2,7,2,akeys); self.b=RootState('anchor-A',2,7,2,bkeys); self.r=RootState('anchor-A',2,8,2,bkeys)
  self.recovery=RecoveryAuthority(3,2,reckeys); self.store=SerializedRootStore(self.db,self.old,self.recovery)
 def tearDown(self): self.tmp.cleanup()
 def rotation(self,candidate,pid):
  p0=Proposal(pid,'rotation',self.old.digest,1,7,candidate); raw=self.a_raw if candidate==self.a else self.b_raw
  return Proposal(pid,'rotation',self.old.digest,1,7,candidate,sigs(self.old_raw,p0.payload,[0,1]),sigs(raw,p0.payload,[0,1]))
 def recovery_p(self,pid='recover'):
  p0=Proposal(pid,'recovery',self.old.digest,1,7,self.r); return Proposal(pid,'recovery',self.old.digest,1,7,self.r,recovery_signatures=sigs(self.rec_raw,p0.payload,[0,1]))
 def test_competing_valid_rotations_exactly_one_successor(self):
  pa,pb=self.rotation(self.a,'A'),self.rotation(self.b,'B'); ra=self.store.activate(pa)
  with self.assertRaises(StalePredecessor): self.store.activate(pb)
  self.assertEqual(self.store.current().digest,self.a.digest); rows=self.store.activation_rows(); self.assertEqual(len(rows),1); self.assertEqual(rows[0]['receipt'],ra)
 def test_real_thread_race_exactly_one_winner(self):
  pa,pb=self.rotation(self.a,'A'),self.rotation(self.b,'B'); barrier=threading.Barrier(2); results=[]; lock=threading.Lock()
  def run(p):
   try: barrier.wait(); val=('ok',p.proposal_id,self.store.activate(p))
   except Exception as e: val=('err',p.proposal_id,type(e).__name__)
   with lock: results.append(val)
  ts=[threading.Thread(target=run,args=(x,)) for x in (pa,pb)]; [t.start() for t in ts]; [t.join(5) for t in ts]
  self.assertFalse(any(t.is_alive() for t in ts)); self.assertEqual(sum(r[0]=='ok' for r in results),1); self.assertEqual(len(self.store.activation_rows()),1)
 def test_rotation_vs_recovery_race_exactly_one(self):
  pr,pc=self.rotation(self.a,'rotate'),self.recovery_p(); self.store.activate(pc)
  with self.assertRaises(StalePredecessor): self.store.activate(pr)
  self.assertEqual(self.store.current().authority_epoch,8); self.assertEqual(len(self.store.activation_rows()),1)
 def test_crash_before_commit_leaves_predecessor_and_retry_succeeds(self):
  p=self.rotation(self.a,'A')
  with self.assertRaises(RuntimeError): self.store.activate(p,crash_before_commit=True)
  self.assertEqual(self.store.current().digest,self.old.digest); self.assertEqual(self.store.activation_rows(),[]); self.store.activate(p); self.assertEqual(self.store.current().digest,self.a.digest)
 def test_timeout_after_commit_reconciles_idempotently(self):
  p=self.rotation(self.a,'A')
  with self.assertRaises(UnknownOutcome): self.store.activate(p,timeout_after_commit=True)
  receipt=self.store.get_receipt('A'); self.assertIsNotNone(receipt); self.assertEqual(self.store.activate(p),receipt); self.assertEqual(len(self.store.activation_rows()),1)
 def test_restart_reconstructs_winner_and_stale_loser_stays_stale(self):
  pa,pb=self.rotation(self.a,'A'),self.rotation(self.b,'B'); receipt=self.store.activate(pa); restarted=SerializedRootStore(self.db,self.old,self.recovery)
  self.assertEqual(restarted.current().digest,self.a.digest); self.assertEqual(restarted.activate(pa),receipt)
  with self.assertRaises(StalePredecessor): restarted.activate(pb)
 def test_same_version_substitution_after_winner_rejected(self):
  pa,pb=self.rotation(self.a,'A'),self.rotation(self.b,'B'); self.store.activate(pa)
  with self.assertRaises(StalePredecessor): self.store.activate(pb)
  self.assertNotEqual(self.a.digest,self.b.digest)
 def test_activation_evidence_identity_stable_across_retry(self):
  p=self.rotation(self.a,'A'); r1=self.store.activate(p); r2=self.store.activate(p); row=self.store.activation_rows()[0]
  self.assertEqual(r1,r2); self.assertEqual(row['proposal_digest'],p.digest); self.assertEqual(row['predecessor_digest'],self.old.digest); self.assertEqual(row['candidate_digest'],self.a.digest)
 def test_loser_retry_cannot_overwrite_winner(self):
  pa,pb=self.rotation(self.a,'A'),self.rotation(self.b,'B'); self.store.activate(pa)
  for _ in range(3):
   with self.assertRaises(StalePredecessor): self.store.activate(pb)
  self.assertEqual(self.store.current().digest,self.a.digest)
 def test_proposal_id_reuse_with_different_transition_is_rejected(self):
  pa=self.rotation(self.a,'same-id'); self.store.activate(pa); pb=self.rotation(self.b,'same-id')
  with self.assertRaises(ProposalSubstitution): self.store.activate(pb)
  self.assertEqual(self.store.current().digest,self.a.digest)
 def test_transparency_observer_detects_split_view_across_independent_stores(self):
  pa,pb=self.rotation(self.a,'A'),self.rotation(self.b,'B'); other=SerializedRootStore(Path(self.tmp.name)/'other.db',self.old,self.recovery)
  self.store.activate(pa); other.activate(pb); observer=TransparencyObserver(); observer.observe(self.store.activation_rows()[0])
  with self.assertRaises(EquivocationDetected): observer.observe(other.activation_rows()[0])
if __name__=='__main__': unittest.main()
