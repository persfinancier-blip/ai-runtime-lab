import sqlite3, tempfile, time, unittest, uuid
from pathlib import Path
from experiments.transactional_kernel.kernel import Kernel, InvalidCompletion, StaleFence

class SafeBatchingInvariantTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.path=Path(self.tmp.name)/'t.db'; self.k=Kernel(self.path)
    def tearDown(self): self.tmp.cleanup()
    def tx1(self,wid='w',owner='a',effect='effect:w'):
        with self.k.tx() as c:
            c.execute('INSERT OR IGNORE INTO work(work_id) VALUES (?)',(wid,)); r=c.execute('SELECT * FROM work WHERE work_id=?',(wid,)).fetchone(); f=r['fence']+1
            if r['phase']=='DONE':
                if r['effect_key']==effect: return r['fence']
                raise InvalidCompletion('terminal work cannot accept new effect')
            cur=c.execute("UPDATE work SET owner=?,lease_until=?,fence=?,generation=generation+2,phase='INTENT',effect_key=? WHERE work_id=? AND generation=?",(owner,time.time()+30,f,effect,wid,r['generation']))
            if cur.rowcount!=1: raise RuntimeError('claim CAS failed')
            c.execute('INSERT OR IGNORE INTO outbox VALUES (?,?,?,?,?,0)',(str(uuid.uuid4()),wid,'effect-intent',effect,'{}'))
        return f
    def tx2(self,fence,wid='w',owner='a',valid=1):
        with self.k.tx() as c:
            r=c.execute('SELECT * FROM work WHERE work_id=?',(wid,)).fetchone()
            if r['owner']!=owner or r['fence']!=fence: raise StaleFence('stale')
            c.execute("UPDATE work SET phase='CONFIRMED',effect_receipt='r' WHERE work_id=?",(wid,))
            c.execute('INSERT INTO evidence VALUES (?,?,?,?,?,?)',('ev',wid,'v1',valid,'ok',time.time()))
            e=c.execute('SELECT valid FROM evidence WHERE evidence_id=? AND work_id=?',('ev',wid)).fetchone()
            if not e or e['valid']!=1: raise InvalidCompletion('missing/invalid evidence')
            c.execute("UPDATE work SET phase='DONE',done_evidence_id='ev' WHERE work_id=? AND fence=?",(wid,fence))
    def test_intent_is_durable_before_confirmation_transaction(self):
        self.tx1(); s=self.k.state('w'); self.assertEqual(s['phase'],'INTENT'); self.assertIsNone(s['effect_receipt'])
    def test_valid_evidence_can_complete_in_second_transaction(self):
        f=self.tx1(); self.tx2(f); self.assertEqual(self.k.state('w')['phase'],'DONE')
    def test_invalid_evidence_rolls_back_confirmation_and_completion(self):
        f=self.tx1()
        with self.assertRaises(InvalidCompletion): self.tx2(f,valid=0)
        self.assertEqual(self.k.state('w')['phase'],'INTENT')
    def test_stale_fence_cannot_complete(self):
        f=self.tx1(); self.k.claim('w','a')
        with self.assertRaises(StaleFence): self.tx2(f)
    def test_late_duplicate_does_not_reopen_done(self):
        f=self.tx1(); self.tx2(f); self.tx1(); self.assertEqual(self.k.state('w')['phase'],'DONE')
if __name__=='__main__': unittest.main()
