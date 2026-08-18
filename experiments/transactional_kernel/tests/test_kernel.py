import sqlite3, tempfile, threading, time, unittest
from pathlib import Path
from experiments.transactional_kernel.kernel import Kernel, Conflict, StaleFence, InvalidCompletion, unsafe_split_complete

class T(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory(); self.p=Path(self.t.name)/'k.db'; self.k=Kernel(self.p); self.k.ensure_work('w')
 def tearDown(self): self.t.cleanup()
 def test_01_claim_race_one_owner(self):
  got=[]
  def f(o):
   try: got.append((o,self.k.claim('w',o,ttl=2)))
   except Conflict: pass
  ts=[threading.Thread(target=f,args=(x,)) for x in ('a','b')]; [x.start() for x in ts]; [x.join() for x in ts]
  self.assertEqual(len(got),1)
 def test_02_stale_fence_rejected(self):
  f,_=self.k.claim('w','a',ttl=-1); f2,_=self.k.claim('w','b'); self.assertGreater(f2,f)
  with self.assertRaises(StaleFence): self.k.prepare_intent('w','a',f,'e')
 def test_03_completion_invalidation_serializes(self):
  f,_=self.k.claim('w','a'); self.k.prepare_intent('w','a',f,'ek'); self.k.confirm_effect('w','a',f,'r'); self.k.append_evidence('w','ev','v1')
  self.k.invalidate('ev')
  with self.assertRaises(InvalidCompletion): self.k.complete('w','a',f,'ev')
 def test_04_duplicate_delivery_one_effect_identity(self):
  f,_=self.k.claim('w','a'); self.k.prepare_intent('w','a',f,'ek'); self.k.prepare_intent('w','a',f,'ek')
  c=sqlite3.connect(self.p); n=c.execute("select count(*) from outbox where dedupe_key='ek'").fetchone()[0]; c.close(); self.assertEqual(n,1)
 def test_05_crash_between_intent_confirmation_resumable(self):
  f,_=self.k.claim('w','a',ttl=-1); self.k.prepare_intent('w','a',f,'ek'); self.assertEqual(self.k.state('w')['phase'],'INTENT')
  f2,_=self.k.claim('w','b'); self.k.mark_unknown('w','b',f2); self.assertEqual(self.k.state('w')['phase'],'UNKNOWN')
 def test_06_rollback_no_partial_state(self):
  f,_=self.k.claim('w','a'); before=self.k.state('w')
  with self.assertRaises(RuntimeError):
   with self.k.tx() as c:
    c.execute("update work set phase='DONE' where work_id='w'"); c.execute("insert into outbox values ('x','w','k','d','{}',0)"); raise RuntimeError()
  after=self.k.state('w'); self.assertEqual(after['phase'],before['phase'])
  c=sqlite3.connect(self.p); self.assertEqual(c.execute("select count(*) from outbox where event_id='x'").fetchone()[0],0); c.close()
 def test_07_lock_conflict_retry_converges(self):
  hold=sqlite3.connect(self.p,timeout=.1,isolation_level=None,check_same_thread=False); hold.execute('begin immediate')
  errs=[]
  def tryclaim():
   try:self.k.claim('w','b')
   except Exception as e: errs.append(e)
  t=threading.Thread(target=tryclaim); t.start(); t.join(); self.assertTrue(errs); hold.rollback(); hold.close()
  self.k.claim('w','b'); self.assertEqual(self.k.state('w')['owner'],'b')
 def test_08_generation_fence_atomic(self):
  b=self.k.state('w'); f,g=self.k.claim('w','a'); a=self.k.state('w'); self.assertEqual((a['fence'],a['generation']),(f,g)); self.assertEqual(f,b['fence']+1); self.assertEqual(g,b['generation']+1)
 def test_09_restart_reconstructs(self):
  f,_=self.k.claim('w','a'); self.k.prepare_intent('w','a',f,'ek'); s=self.k.state('w'); k2=Kernel(self.p); self.assertEqual(k2.state('w'),s)
 def test_10_unsafe_split_can_create_invalid_done(self):
  f,_=self.k.claim('w','a'); self.k.prepare_intent('w','a',f,'ek'); self.k.confirm_effect('w','a',f,'r'); self.k.append_evidence('w','ev','v1')
  self.assertTrue(unsafe_split_complete(self.p,'w','ev')); self.k.invalidate('ev')
  c=sqlite3.connect(self.p,isolation_level=None); c.execute("update work set phase='DONE',done_evidence_id='ev' where work_id='w'"); c.close()
  self.assertEqual(self.k.state('w')['phase'],'DONE')
  c=sqlite3.connect(self.p); self.assertEqual(c.execute("select valid from evidence where evidence_id='ev'").fetchone()[0],0); c.close()
 def test_11_corrected_prevents_invalid_done(self):
  f,_=self.k.claim('w','a'); self.k.prepare_intent('w','a',f,'ek'); self.k.confirm_effect('w','a',f,'r'); self.k.append_evidence('w','ev','v1'); self.k.invalidate('ev')
  with self.assertRaises(InvalidCompletion): self.k.complete('w','a',f,'ev')
 def test_12_state_outbox_atomic(self):
  f,_=self.k.claim('w','a'); self.k.prepare_intent('w','a',f,'ek'); s=self.k.state('w'); c=sqlite3.connect(self.p); n=c.execute("select count(*) from outbox where dedupe_key='ek'").fetchone()[0]; c.close(); self.assertEqual(s['phase'],'INTENT'); self.assertEqual(n,1)
 def test_13_duplicate_after_done_does_not_reopen_terminal_state(self):
  f,_=self.k.claim('w','a'); self.k.prepare_intent('w','a',f,'ek'); self.k.confirm_effect('w','a',f,'r'); self.k.append_evidence('w','ev','v1'); self.k.complete('w','a',f,'ev'); self.k.prepare_intent('w','a',f,'ek'); self.assertEqual(self.k.state('w')['phase'],'DONE')

if __name__=='__main__': unittest.main()
