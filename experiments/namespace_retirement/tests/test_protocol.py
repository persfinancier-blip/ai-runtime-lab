import shutil, tempfile, unittest
from pathlib import Path
from experiments.namespace_retirement.protocol import *

class Tests(unittest.TestCase):
    def setUp(self):
        self.key=b"retirement-key"; self.chain="c"*64
        self.td=tempfile.TemporaryDirectory(); self.root=Path(self.td.name)
        self.old_path=self.root/"old"; self.new_path=self.root/"new"
        self.old_path.mkdir(); self.new_path.mkdir()
        self.old=issue_record(generation=1,path=self.old_path,object_id="obj-old",archive_chain_commitment=self.chain,predecessor_id=None,key=self.key)
        self.new=issue_record(generation=2,path=self.new_path,object_id="obj-new",archive_chain_commitment=self.chain,predecessor_id=self.old.record_id,key=self.key)
        self.permit=issue_retirement_permit(self.old,self.new,7,self.key)
        self.ledger=RetirementLedger(); self.ledger.records[self.old.record_id]=self.old; self.ledger.activate(self.new)
        self.engine=RetirementEngine(self.ledger,key=self.key,policy_generation=7)
    def tearDown(self): self.td.cleanup()
    def reacquire(self,r): return "REACQUIRED"
    def audit(self,r): return True
    def cleanup(self,r):
        count=sum(1 for _ in Path(r.path).iterdir()); shutil.rmtree(r.path); return count

    def test_successful_retirement_is_bound_to_superseded_generation(self):
        (self.old_path/"x").write_text("x")
        rec=self.engine.retire(self.old,self.permit,reacquire=self.reacquire,audit_successor=self.audit,cleanup=self.cleanup)
        self.assertEqual(rec.status,"RETIRED"); self.assertFalse(self.old_path.exists()); self.assertTrue(self.new_path.exists())

    def test_current_generation_cannot_be_retired(self):
        u={"predecessor_record_id":self.new.record_id,"successor_record_id":self.new.record_id,
           "predecessor_generation":2,"successor_generation":2,
           "archive_chain_commitment":self.chain,"policy_generation":7}
        p=RetirementPermit(**u, mac=mac(self.key,u))
        self.assertEqual(self.engine.classify(self.new,p,reacquire=self.reacquire,audit_successor=self.audit),"CURRENT_GENERATION_PROTECTED")

    def test_stale_policy_generation_rejected(self):
        engine=RetirementEngine(self.ledger,key=self.key,policy_generation=8)
        self.assertEqual(engine.classify(self.old,self.permit,reacquire=self.reacquire,audit_successor=self.audit),"STALE_PERMIT")

    def test_wrong_successor_pair_rejected(self):
        other=issue_record(generation=2,path=self.root/"other",object_id="x",archive_chain_commitment=self.chain,predecessor_id="wrong",key=self.key)
        self.ledger.records[other.record_id]=other; self.ledger.current_record_id=other.record_id
        self.assertEqual(self.engine.classify(self.old,self.permit,reacquire=self.reacquire,audit_successor=self.audit),"STALE_PERMIT")

    def test_successor_chain_must_audit(self):
        self.assertEqual(self.engine.classify(self.old,self.permit,reacquire=self.reacquire,audit_successor=lambda r:False),"SUCCESSOR_AUDIT_FAILED")

    def test_strong_reacquisition_unavailable_is_non_destructive(self):
        self.assertEqual(self.engine.classify(self.old,self.permit,reacquire=lambda r:"UNSUPPORTED_STRONG_REACQUISITION",audit_successor=self.audit),"RETIREMENT_UNSUPPORTED")
        self.assertTrue(self.old_path.exists())

    def test_replaced_path_not_cleaned(self):
        self.assertEqual(self.engine.classify(self.old,self.permit,reacquire=lambda r:"PATH_REPLACED",audit_successor=self.audit),"DETACHED_OBJECT_FOUND")
        self.assertTrue(self.old_path.exists())

    def test_retry_is_idempotent(self):
        calls=[]
        first=self.engine.retire(self.old,self.permit,reacquire=self.reacquire,audit_successor=self.audit,cleanup=lambda r:(calls.append(1) or 0))
        second=self.engine.retire(self.old,self.permit,reacquire=self.reacquire,audit_successor=self.audit,cleanup=lambda r:(calls.append(1) or 0))
        self.assertEqual(first,second); self.assertEqual(len(calls),1)

    def test_generation_change_after_permit_fails_closed(self):
        newer=issue_record(generation=3,path=self.root/"v3",object_id="v3",archive_chain_commitment=self.chain,predecessor_id=self.new.record_id,key=self.key)
        self.ledger.activate(newer)
        self.assertEqual(self.engine.classify(self.old,self.permit,reacquire=self.reacquire,audit_successor=self.audit),"STALE_PERMIT")

    def test_unsafe_path_retirement_can_delete_current_namespace(self):
        p=self.root/"unsafe-current"; p.mkdir(); UnsafePathRetirement().retire(p); self.assertFalse(p.exists())

if __name__=="__main__": unittest.main()
