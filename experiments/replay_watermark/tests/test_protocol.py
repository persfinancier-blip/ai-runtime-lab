import shutil,tempfile,unittest
from pathlib import Path
from experiments.replay_watermark.protocol import *
SECRET=b'reference-key-not-evidence'
class Tests(unittest.TestCase):
 def setUp(self): self.t=tempfile.TemporaryDirectory(); self.p=Path(self.t.name)/'db.sqlite'; self.db=WatermarkDB(self.p)
 def tearDown(self): self.t.cleanup()
 def test_restart(self):
  r=self.db.publish(SECRET,'t','d1'); self.assertTrue(WatermarkDB(self.p).verify_fresh(SECRET,r))
 def test_stale_writer(self):
  self.db.publish(SECRET,'t1','a',0)
  with self.assertRaises(StaleWrite): self.db.publish(SECRET,'t2','b',0)
 def test_concurrent_expected_sequence_only_one_wins(self):
  import threading
  results=[]
  def w(task):
   try: self.db.publish(SECRET,task,task,0); results.append('ok')
   except StaleWrite: results.append('stale')
  a=threading.Thread(target=w,args=('a',)); b=threading.Thread(target=w,args=('b',)); a.start(); b.start(); a.join(); b.join()
  self.assertEqual(sorted(results),['ok','stale'])
  self.assertEqual(self.db.state()['global_sequence'],1)
 def test_older_record_rejected(self):
  r1=self.db.publish(SECRET,'t','a'); r2=self.db.publish(SECRET,'t','b'); self.assertFalse(self.db.verify_fresh(SECRET,r1)); self.assertTrue(self.db.verify_fresh(SECRET,r2))
 def test_rotation_fences_old(self):
  r=self.db.publish(SECRET,'t','a'); self.db.rotate(1,2,2); self.assertFalse(self.db.verify_fresh(SECRET,r))
 def test_duplicate_current(self):
  r=self.db.publish(SECRET,'t','a'); self.assertTrue(self.db.verify_fresh(SECRET,r)); self.assertTrue(self.db.verify_fresh(SECRET,r))
 def test_crash_transaction_rolls_back_together(self):
  before=self.db.state(); c=self.db.connect(); c.execute('BEGIN IMMEDIATE'); e,k,g=c.execute('SELECT authority_epoch,key_generation,global_sequence FROM authority WHERE singleton=1').fetchone(); c.execute('UPDATE authority SET global_sequence=? WHERE singleton=1',(g+1,)); c.execute('INSERT INTO task_watermark VALUES(?,?,?,?,?,?)',('x',g+1,e,k,'d','bad')); c.execute('ROLLBACK'); c.close(); self.assertEqual(before,self.db.state())
 def test_snapshot_rollback_detected_with_anchor(self):
  r1=self.db.publish(SECRET,'t','a'); anchor=Anchor(self.db.state()['global_sequence']); backup=Path(self.t.name)/'backup.sqlite'; shutil.copy2(self.p,backup); self.db.publish(SECRET,'t','b'); anchor.advance(self.db.state()['global_sequence']); shutil.copy2(backup,self.p); db2=WatermarkDB(self.p)
  with self.assertRaises(AnchorMismatch): db2.verify_fresh(SECRET,r1,anchor)
 def test_snapshot_rollback_not_detectable_sql_alone(self):
  r1=self.db.publish(SECRET,'t','a'); backup=Path(self.t.name)/'backup2.sqlite'; shutil.copy2(self.p,backup); self.db.publish(SECRET,'t','b'); shutil.copy2(backup,self.p); self.assertTrue(WatermarkDB(self.p).verify_fresh(SECRET,r1,None))
 def test_evidence_has_no_secret(self):
  evidence={'anchor_value':Anchor(7).read(),'status':'ok'}; self.assertNotIn('reference-key',str(evidence))
