import hashlib, sqlite3, tempfile, threading, unittest
from pathlib import Path
from dataclasses import dataclass
from experiments.sink_registry_binding.protocol import *

@dataclass(frozen=True)
class Req:
    request_id:str; payload:str; credential_generation:int=1
    task_id:str="task"; scope:str="scope"
    @property
    def digest(self):
        return hashlib.sha256(f"{self.request_id}|{self.task_id}|{self.scope}|{self.credential_generation}|{self.payload}".encode()).hexdigest()
@dataclass(frozen=True)
class CapPlan:
    sink_id:str; effect_key:str
class Journal:
    def __init__(self,p):
        self.p=str(p); q=self._con(); q.executescript("""CREATE TABLE broker_meta(singleton INTEGER PRIMARY KEY,credential_generation INTEGER); INSERT INTO broker_meta VALUES(1,1);
        CREATE TABLE broker_requests(
        request_id TEXT PRIMARY KEY, request_digest TEXT, task_id TEXT, scope TEXT, credential_generation INTEGER,
        effect_key TEXT, status TEXT, receipt TEXT,
        capability_sink_id TEXT, capability_generation INTEGER, capability_claim_digest TEXT,
        capability_probe_generation INTEGER, capability_issuer_id TEXT, capability_policy TEXT,
        capability_key_created_at INTEGER, registry_entry_digest TEXT, registry_generation INTEGER);"""); q.close()
    def _con(self):
        q=sqlite3.connect(self.p,timeout=5,isolation_level=None,check_same_thread=False);q.execute("PRAGMA busy_timeout=5000");return q
    @staticmethod
    def _effect_key(r): return "effect:"+r.request_id
    def confirm(self,r,receipt):
        q=self._con();q.execute("UPDATE broker_requests SET status='CONFIRMED',receipt=? WHERE request_id=?",(receipt,r.request_id));q.close()
    def mark_unknown(self,r):
        q=self._con();q.execute("UPDATE broker_requests SET status='UNKNOWN' WHERE request_id=?",(r.request_id,));q.close()
class Bound:
    def __init__(self,j):self.journal=j
    def reserve(self,r,c,now=0):
        q=self.journal._con();q.execute("BEGIN IMMEDIATE");row=q.execute("SELECT status,receipt,effect_key FROM broker_requests WHERE request_id=?",(r.request_id,)).fetchone()
        if row:q.commit();q.close();return row[0],CapPlan(c["sink_id"],row[2]),row[1]
        ek="effect:"+r.request_id;q.execute("""INSERT INTO broker_requests(
        request_id,request_digest,task_id,scope,credential_generation,effect_key,status,receipt,
        capability_sink_id,capability_generation,capability_claim_digest,capability_probe_generation,
        capability_issuer_id,capability_policy,capability_key_created_at,registry_entry_digest,registry_generation)
        VALUES(?,?,?,?,?,?,'INTENT',NULL,?,1,?,1,'test-issuer','SAFE_RETRY_RECONCILE',0,NULL,NULL)""",
        (r.request_id,r.digest,r.task_id,r.scope,r.credential_generation,ek,c["sink_id"],"a"*64));q.commit();q.close();return "INTENT",CapPlan(c["sink_id"],ek),None
    def verify_durable(self):return True
class Sink:
    def __init__(self):self.effects={};self.count=0
    def apply(self,k,p,s,timeout_after_commit=False):
        if k not in self.effects:self.count+=1;self.effects[k]=f"r{self.count}"
        if timeout_after_commit:
            class UnknownOutcome(Exception):pass
            raise UnknownOutcome()
        return self.effects[k]
    def lookup(self,k):return self.effects.get(k)

def ad(x):return hashlib.sha256(x.encode()).hexdigest()
class Tests(unittest.TestCase):
    def setUp(self):
        self.auth=RegistryAuthority("issuer",b"k",1)
    def entry(self,g=1,adapter="good",endpoint="https://a.example",pred=None,profile="charge"):
        e=RegistryEntry("sink-A",g,ad(adapter),endpoint,profile,pred,"issuer",1)
        return self.auth.issue(e)
    def setup(self,td):
        j=Journal(Path(td)/"j.db");r=RegistryBoundJournal(Bound(j),self.auth);return j,r
    def runtime(self,sink,adapter="good",endpoint="https://a.example",profile="charge"):
        return RuntimeAdapter(ad(adapter),endpoint,profile,sink)
    def test_attacker_adapter_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            j,r=self.setup(td);e=self.entry();s=Sink();w=RegistryBrokerWorker(r,self.runtime(s,"evil"),b"x")
            with self.assertRaises(RegistryBindingError):w.process(Req("1","p"),{"sink_id":"sink-A"},e,now=0)
            self.assertEqual(s.count,0)
    def test_endpoint_substitution_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            j,r=self.setup(td);e=self.entry();s=Sink();w=RegistryBrokerWorker(r,self.runtime(s,endpoint="https://evil"),b"x")
            with self.assertRaises(RegistryBindingError):w.process(Req("1","p"),{"sink_id":"sink-A"},e,now=0)
    def test_rollback_rejected_after_restart(self):
        with tempfile.TemporaryDirectory() as td:
            j,r=self.setup(td);e1=self.entry();r.observe(e1);e2=self.entry(2,pred=e1.entry_digest,endpoint="https://b.example");r.observe(e2)
            r2=RegistryBoundJournal(Bound(j),self.auth)
            with self.assertRaises(RegistryRollback):r2.observe(e1)
    def test_same_generation_substitution(self):
        with tempfile.TemporaryDirectory() as td:
            j,r=self.setup(td);e=self.entry();r.observe(e)
            with self.assertRaises(RegistrySubstitution):r.observe(self.entry(endpoint="https://other"))
    def test_head_change_before_binding_fails(self):
        with tempfile.TemporaryDirectory() as td:
            j,r=self.setup(td);e1=self.entry();r.observe(e1)
            e2=self.entry(2,pred=e1.entry_digest,endpoint="https://b.example");r.observe(e2)
            with self.assertRaises(RegistryRollback):r.reserve(Req("1","p"),{"sink_id":"sink-A"},e1,now=0)
    def test_old_intent_never_executes_on_rotated_endpoint(self):
        with tempfile.TemporaryDirectory() as td:
            j,r=self.setup(td);e1=self.entry();s=Sink()
            r.reserve(Req("1","p"),{"sink_id":"sink-A"},e1,now=0)
            e2=self.entry(2,pred=e1.entry_digest,endpoint="https://b.example");r.observe(e2)
            with self.assertRaises(HistoricalExecutionBlocked):r.verify_runtime(DurableRegistryPlan("sink-A",e1.entry_digest,1),self.runtime(s,endpoint="https://b.example"))
    def test_unknown_compatible_successor_reconciles_only(self):
        with tempfile.TemporaryDirectory() as td:
            j,r=self.setup(td);e1=self.entry();s=Sink();w1=RegistryBrokerWorker(r,self.runtime(s),b"x")
            with self.assertRaises(Exception):w1.process(Req("1","p"),{"sink_id":"sink-A"},e1,now=0,timeout_after_commit=True)
            e2=self.entry(2,pred=e1.entry_digest,endpoint="https://b.example");r.observe(e2)
            w2=RegistryBrokerWorker(r,self.runtime(s,endpoint="https://b.example"),b"x")
            out=w2.process(Req("1","p"),{"sink_id":"sink-A"},e2,now=1)
            self.assertEqual(out[0],"RECONCILED");self.assertEqual(s.count,1)
    def test_unknown_incompatible_successor_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            j,r=self.setup(td);e1=self.entry();s=Sink();w=RegistryBrokerWorker(r,self.runtime(s),b"x")
            with self.assertRaises(Exception):w.process(Req("1","p"),{"sink_id":"sink-A"},e1,now=0,timeout_after_commit=True)
            e2=self.entry(2,pred=e1.entry_digest,endpoint="https://b.example");r.observe(e2)
            e3=self.entry(3,pred=e2.entry_digest,endpoint="https://c.example");r.observe(e3)
            with self.assertRaises(HistoricalExecutionBlocked):RegistryBrokerWorker(r,self.runtime(s,endpoint="https://c.example"),b"x").process(Req("1","p"),{"sink_id":"sink-A"},e3,now=2)
            self.assertEqual(s.count,1)
    def test_confirmed_receipt_survives_rotation_without_runtime_use(self):
        with tempfile.TemporaryDirectory() as td:
            j,r=self.setup(td);e1=self.entry();s=Sink();w=RegistryBrokerWorker(r,self.runtime(s),b"x")
            self.assertEqual(w.process(Req("1","p"),{"sink_id":"sink-A"},e1,now=0)[0],"COMMITTED")
            e2=self.entry(2,pred=e1.entry_digest,endpoint="https://b.example");r.observe(e2)
            bad=RegistryBrokerWorker(r,self.runtime(Sink(),"evil","https://evil"),b"x")
            self.assertEqual(bad.process(Req("1","p"),{"sink_id":"sink-A"},e2,now=1)[0],"ALREADY_COMMITTED")
    def test_relational_corruption_detected(self):
        with tempfile.TemporaryDirectory() as td:
            j,r=self.setup(td);e=self.entry();r.reserve(Req("1","p"),{"sink_id":"sink-A"},e,now=0)
            q=j._con();q.execute("UPDATE broker_requests SET registry_generation=99");q.close()
            with self.assertRaises(CorruptRegistry):r.verify_durable()
    def test_concurrent_registry_update_vs_reservation_serializes(self):
        with tempfile.TemporaryDirectory() as td:
            j,r=self.setup(td);e1=self.entry();r.observe(e1);e2=self.entry(2,pred=e1.entry_digest,endpoint="https://b.example")
            errors=[]
            def a():
                try:r.reserve(Req("1","p"),{"sink_id":"sink-A"},e1,now=0)
                except Exception as x:errors.append(type(x).__name__)
            def b():
                try:r.observe(e2)
                except Exception as x:errors.append(type(x).__name__)
            t1=threading.Thread(target=a);t2=threading.Thread(target=b);t1.start();t2.start();t1.join();t2.join()
            q=j._con();row=q.execute("SELECT registry_generation FROM broker_requests WHERE request_id='1'").fetchone();q.close()
            self.assertTrue(row is None or row[0]==1)
    def test_unsafe_string_only_executes_attacker(self):
        s=Sink();runtime=self.runtime(s,"evil","https://evil")
        UnsafeStringOnly().execute("sink-A",runtime,"e","p",b"x")
        self.assertEqual(s.count,1)
if __name__=="__main__":unittest.main()
