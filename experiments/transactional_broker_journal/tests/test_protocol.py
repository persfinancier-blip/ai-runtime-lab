import sqlite3
import tempfile
import threading
import unittest
from pathlib import Path

from experiments.transactional_broker_journal.protocol import *


class Tests(unittest.TestCase):
    def setup(self, td, generation=1):
        root=Path(td)
        journal=TransactionalJournal(root/'journal.db',generation)
        sink=IdempotentSink(root/'sink.db')
        return journal,sink

    def test_unsafe_concurrent_duplicate_applies_twice(self):
        unsafe=UnsafeCheckThenApply(); req=Request('r','task','read',1,'payload'); barrier=threading.Barrier(2)
        out=[]
        threads=[threading.Thread(target=lambda: out.append(unsafe.process_with_barrier(req,barrier))) for _ in range(2)]
        [t.start() for t in threads]; [t.join(5) for t in threads]
        self.assertEqual(unsafe.apply_count,2)

    def test_corrected_identical_concurrent_requests_commit_once(self):
        with tempfile.TemporaryDirectory() as td:
            journal,sink=self.setup(td); req=Request('r','task','read',1,'payload')
            workers=[BrokerWorker(TransactionalJournal(Path(td)/'journal.db',1),sink,b'secret') for _ in range(2)]
            out=[]; errors=[]; gate=threading.Barrier(3)
            def run(w):
                gate.wait()
                try: out.append(w.process(req))
                except Exception as e: errors.append(e)
            threads=[threading.Thread(target=run,args=(w,)) for w in workers]
            [t.start() for t in threads]; gate.wait(); [t.join(5) for t in threads]
            self.assertFalse(errors); self.assertEqual(len(out),2)
            self.assertEqual(sink.apply_count(),1)
            self.assertEqual(out[0].receipt,out[1].receipt)
            self.assertTrue(journal.verify_durable())

    def test_different_payloads_same_id_race_has_one_winner(self):
        with tempfile.TemporaryDirectory() as td:
            journal,sink=self.setup(td)
            a=Request('r','task','read',1,'a'); b=Request('r','task','read',1,'b')
            out=[]; errors=[]; gate=threading.Barrier(3)
            def run(req):
                gate.wait()
                try: out.append(BrokerWorker(TransactionalJournal(Path(td)/'journal.db',1),sink,b'secret').process(req))
                except Exception as e: errors.append(e)
            ts=[threading.Thread(target=run,args=(x,)) for x in (a,b)]
            [t.start() for t in ts]; gate.wait(); [t.join(5) for t in ts]
            self.assertEqual(len(out),1); self.assertEqual(len(errors),1)
            self.assertIsInstance(errors[0],RequestConflict); self.assertEqual(sink.apply_count(),1)

    def test_rotation_before_reservation_rejects_old_generation(self):
        with tempfile.TemporaryDirectory() as td:
            journal,sink=self.setup(td); journal.rotate()
            with self.assertRaises(StaleCredential):
                BrokerWorker(journal,sink,b'new').process(Request('r','task','read',1,'x'))
            self.assertEqual(sink.apply_count(),0)

    def test_reservation_before_rotation_blocks_rotation_until_confirmed(self):
        with tempfile.TemporaryDirectory() as td:
            journal,sink=self.setup(td); req=Request('r','task','read',1,'x')
            status,key,_=journal.reserve(req); self.assertEqual(status,'INTENT')
            with self.assertRaises(PendingEffects):
                journal.rotate()
            out=BrokerWorker(journal,sink,b'old').process(req)
            self.assertIn(out.outcome,{'COMMITTED','RECONCILED'})
            self.assertEqual(sink.apply_count(),1)
            self.assertEqual(journal.rotate(),2)

    def test_unknown_blocks_rotation_until_reconciled(self):
        with tempfile.TemporaryDirectory() as td:
            journal,sink=self.setup(td); req=Request('r','task','read',1,'x')
            with self.assertRaises(UnknownOutcome):
                BrokerWorker(journal,sink,b'old').process(req,timeout_after_commit=True)
            with self.assertRaises(PendingEffects):
                journal.rotate()
            out=BrokerWorker(journal,sink,b'old').process(req)
            self.assertEqual(out.outcome,'RECONCILED')
            self.assertEqual(journal.rotate(),2)

    def test_rotation_vs_reservation_has_safe_serial_outcome(self):
        for _ in range(20):
            with tempfile.TemporaryDirectory() as td:
                journal,sink=self.setup(td); req=Request('r','task','read',1,'x')
                gate=threading.Barrier(3); outcomes=[]; lock=threading.Lock()
                def reserve():
                    gate.wait()
                    try: result=('reserve', journal.reserve(req)[0])
                    except Exception as e: result=('reserve', type(e).__name__)
                    with lock: outcomes.append(result)
                def rotate():
                    gate.wait()
                    try: result=('rotate', journal.rotate())
                    except Exception as e: result=('rotate', type(e).__name__)
                    with lock: outcomes.append(result)
                a=threading.Thread(target=reserve); b=threading.Thread(target=rotate)
                a.start(); b.start(); gate.wait(); a.join(5); b.join(5)
                self.assertEqual(len(outcomes),2)
                values=dict(outcomes)
                if values['rotate']==2:
                    self.assertEqual(values['reserve'],'StaleCredential')
                else:
                    self.assertEqual(values['reserve'],'INTENT')
                    self.assertEqual(values['rotate'],'PendingEffects')

    def test_crash_after_intent_before_effect_is_resumable(self):
        with tempfile.TemporaryDirectory() as td:
            journal,sink=self.setup(td); req=Request('r','task','read',1,'x')
            journal.reserve(req)
            out=BrokerWorker(TransactionalJournal(Path(td)/'journal.db',1),sink,b's').process(req)
            self.assertEqual(out.outcome,'COMMITTED'); self.assertEqual(sink.apply_count(),1)

    def test_unknown_after_sink_commit_reconciles_without_duplicate(self):
        with tempfile.TemporaryDirectory() as td:
            journal,sink=self.setup(td); req=Request('r','task','read',1,'x'); w=BrokerWorker(journal,sink,b's')
            with self.assertRaises(UnknownOutcome): w.process(req,timeout_after_commit=True)
            self.assertEqual(sink.apply_count(),1)
            out=BrokerWorker(TransactionalJournal(Path(td)/'journal.db',1),IdempotentSink(Path(td)/'sink.db'),b's').process(req)
            self.assertEqual(out.outcome,'RECONCILED'); self.assertEqual(sink.apply_count(),1)

    def test_concurrent_retry_after_unknown_deduplicates(self):
        with tempfile.TemporaryDirectory() as td:
            journal,sink=self.setup(td); req=Request('r','task','read',1,'x')
            with self.assertRaises(UnknownOutcome): BrokerWorker(journal,sink,b's').process(req,timeout_after_commit=True)
            out=[]; errors=[]; gate=threading.Barrier(3)
            def run():
                gate.wait()
                try: out.append(BrokerWorker(TransactionalJournal(Path(td)/'journal.db',1),IdempotentSink(Path(td)/'sink.db'),b's').process(req))
                except Exception as e: errors.append(e)
            ts=[threading.Thread(target=run) for _ in range(2)]
            [t.start() for t in ts]; gate.wait(); [t.join(5) for t in ts]
            self.assertFalse(errors); self.assertEqual(len(out),2); self.assertEqual(sink.apply_count(),1)
            self.assertEqual(out[0].receipt,out[1].receipt)

    def test_restart_generation_is_explicit(self):
        with tempfile.TemporaryDirectory() as td:
            journal,sink=self.setup(td); journal.rotate()
            with self.assertRaises(StaleCredential):
                TransactionalJournal(Path(td)/'journal.db',1)
            self.assertEqual(TransactionalJournal(Path(td)/'journal.db',2).generation(),2)

    def test_durable_journal_contains_no_raw_secret(self):
        with tempfile.TemporaryDirectory() as td:
            secret=b'never-persist-secret'; journal,sink=self.setup(td)
            BrokerWorker(journal,sink,secret).process(Request('r','task','read',1,'x'))
            self.assertNotIn(secret,Path(td,'journal.db').read_bytes())
            self.assertNotIn(secret,Path(td,'sink.db').read_bytes())

    def test_verify_durable_detects_corrupt_receipt_state(self):
        with tempfile.TemporaryDirectory() as td:
            journal,sink=self.setup(td); req=Request('r','task','read',1,'x'); journal.reserve(req)
            q=sqlite3.connect(Path(td)/'journal.db')
            q.execute("PRAGMA ignore_check_constraints=ON")
            q.execute("UPDATE broker_requests SET receipt='forged' WHERE request_id='r'")
            q.commit(); q.close()
            with self.assertRaises(CorruptJournal): journal.verify_durable()


if __name__=='__main__':
    unittest.main()
