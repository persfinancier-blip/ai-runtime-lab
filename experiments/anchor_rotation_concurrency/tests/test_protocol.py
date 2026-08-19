import tempfile, threading, unittest
from pathlib import Path
from experiments.anchor_rotation_concurrency.protocol import Proposal,Root,RotationDB,SameVersionSubstitution,StaleProposal,UnknownCommitOutcome

def root(version=1,epoch=7,suffix='old',threshold=2): return Root('anchor-A',version,epoch,threshold,(f'{suffix}-k1',f'{suffix}-k2',f'{suffix}-k3'))
def proposal(pid,old,candidate,kind='rotation',signers=('s1','s2')): return Proposal(pid,kind,old.digest,old.version,old.authority_epoch,candidate,tuple(signers))
class T(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(); self.dbpath=Path(self.tmp.name)/'roots.db'; self.initial=root(); self.db=RotationDB(self.dbpath,self.initial)
 def tearDown(self): self.tmp.cleanup()
 def test_two_valid_rotations_exactly_one_activates(self):
  a=proposal('A',self.initial,root(2,7,'A')); b=proposal('B',self.initial,root(2,7,'B')); barrier=threading.Barrier(3); outcomes=[]; lock=threading.Lock()
  def run(p):
   barrier.wait()
   try:v=('ok',RotationDB(self.dbpath).activate(p).proposal_id)
   except Exception as e:v=(type(e).__name__,p.proposal_id)
   with lock:outcomes.append(v)
  ts=[threading.Thread(target=run,args=(p,)) for p in (a,b)]; [t.start() for t in ts]; barrier.wait(); [t.join() for t in ts]
  self.assertEqual(sum(x[0]=='ok' for x in outcomes),1); self.assertEqual(self.db.transition_count(),1)
 def test_loser_retry_cannot_overwrite(self):
  a=proposal('A',self.initial,root(2,7,'A')); b=proposal('B',self.initial,root(2,7,'B')); self.db.activate(a)
  with self.assertRaises(StaleProposal):self.db.activate(b)
  self.assertEqual(self.db.active()[0].digest,a.candidate.digest)
 def test_recovery_races_rotation(self):
  rot=proposal('R',self.initial,root(2,7,'rot')); rec=proposal('X',self.initial,root(2,8,'rec'),'recovery',('r1','r2')); barrier=threading.Barrier(3); out=[]
  def run(p):
   barrier.wait()
   try:out.append(('ok',RotationDB(self.dbpath).activate(p).proposal_id))
   except Exception as e:out.append((type(e).__name__,p.proposal_id))
  a=threading.Thread(target=run,args=(rot,));b=threading.Thread(target=run,args=(rec,));a.start();b.start();barrier.wait();a.join();b.join();self.assertEqual(sum(x[0]=='ok' for x in out),1);self.assertEqual(self.db.transition_count(),1)
 def test_crash_before_commit(self):
  a=proposal('A',self.initial,root(2,7,'A'))
  with self.assertRaises(RuntimeError):self.db.activate(a,crash_before_commit=True)
  self.assertEqual(self.db.transition_count(),0); self.assertEqual(self.db.active()[1],0); self.assertEqual(self.db.activate(a).proposal_id,'A')
 def test_timeout_after_commit_reconcile(self):
  a=proposal('A',self.initial,root(2,7,'A'))
  with self.assertRaises(UnknownCommitOutcome):self.db.activate(a,timeout_after_commit=True)
  self.assertEqual(self.db.transition_count(),1); self.assertEqual(self.db.activate(a).proposal_id,'A'); self.assertEqual(self.db.transition_count(),1)
 def test_restart(self):
  a=proposal('A',self.initial,root(2,7,'A'));r=self.db.activate(a);db=RotationDB(self.dbpath);active,seq=db.active();self.assertEqual(active.digest,a.candidate.digest);self.assertEqual(seq,r.transition_seq)
 def test_same_version_substitution(self):
  with self.assertRaises(SameVersionSubstitution):self.db.activate(proposal('S',self.initial,root(1,7,'sub')))
 def test_proposal_id_reuse_changed_content(self):
  a=proposal('P',self.initial,root(2,7,'A'));self.db.activate(a); altered=Proposal('P','rotation',self.initial.digest,1,7,root(2,7,'B'),('s1','s2'))
  with self.assertRaises(SameVersionSubstitution):self.db.activate(altered)
 def test_evidence(self):
  a=proposal('A',self.initial,root(2,7,'A'),signers=('old1','old2','new1'));r=self.db.activate(a);self.assertEqual(r.proposal_digest,a.digest);self.assertEqual(set(r.signer_ids),{'old1','old2','new1'})
 def test_competing_proposals_remain_observable(self):
  a=proposal('A',self.initial,root(2,7,'A'),signers=('old1','old2','newA'));b=proposal('B',self.initial,root(2,7,'B'),signers=('old2','old3','newB'));self.db.activate(a)
  with self.assertRaises(StaleProposal):self.db.activate(b)
  conflicts=self.db.equivocation_candidates(self.initial.digest);self.assertEqual(len(conflicts),1);self.assertEqual(conflicts[0]['overlapping_signers'],('old2',))
if __name__=='__main__':unittest.main()
