import json,sqlite3,tempfile,unittest
from pathlib import Path
from experiments.transition_history_integrity.protocol import *
def auth(kind,v,g,prefix,n=3,t=2):
 raw=[f'{prefix}-{i}'.encode() for i in range(n)];return Authority(kind,v,g,t,{kid(k):k.hex() for k in raw}),raw
def sigs(keys,p,n=2):return tuple(Sig(kid(k),sign(k,p)) for k in keys[:n])
class Tests(unittest.TestCase):
 def setUp(self):self.root,self.rk=auth('root',1,1,'r1');self.rec,self.ck=auth('recovery',1,1,'c1')
 def store(self,p):return HistoryStore(p,self.root,self.rec)
 def rotation(self,pid='rot1'):
  n,nk=auth('recovery',2,2,'c2');z=rotation_payload(self.root,self.rec,n);return Proposal(pid,'rotate_recovery',self.root.authority_id,self.rec.authority_id,n,sigs(self.ck,z),sigs(nk,z),sigs(self.rk,z)),n,nk
 def chain(self,path):
  s=self.store(path);p1,nrec,nk=self.rotation();s.commit(p1);nroot,_=auth('root',2,2,'r2');z=recovery_payload(self.root,nroot,nrec);p2=Proposal('recover2','recover_root',self.root.authority_id,nrec.authority_id,nroot,sigs(nk,z));s.commit(p2);return s,p1,p2,nroot,nrec
 def test_restart_reverifies_complete_history(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'db';s,*_=self.chain(p);e=s.verify_history();self.assertEqual(self.store(p).verify_history(),e);self.assertEqual(e['sequence'],2)
 def test_tampered_predecessor_fails(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'db';s,*_=self.chain(p);q=sqlite3.connect(p);q.execute("UPDATE transitions SET predecessor_root_id='evil' WHERE sequence=2");q.commit();q.close();self.assertRaises(IntegrityError,s.verify_history)
 def test_tampered_successor_fails(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'db';s,*_=self.chain(p);q=sqlite3.connect(p);q.execute("UPDATE transitions SET successor_recovery_id='evil' WHERE sequence=1");q.commit();q.close();self.assertRaises(IntegrityError,s.verify_history)
 def test_tampered_signature_fails(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'db';s,*_=self.chain(p);q=sqlite3.connect(p);raw=json.loads(q.execute('SELECT proof_json FROM transitions WHERE sequence=1').fetchone()[0]);raw['sig1'][0]['signature']='00'*32;q.execute('UPDATE transitions SET proof_json=? WHERE sequence=1',(json.dumps(raw,sort_keys=True,separators=(',',':')),));q.commit();q.close();self.assertRaises(ThresholdError,s.verify_history)
 def test_missing_transition_row_fails(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'db';s,*_=self.chain(p);q=sqlite3.connect(p);q.execute('DELETE FROM transitions WHERE sequence=1');q.commit();q.close();self.assertRaises(IntegrityError,s.verify_history)
 def test_head_history_mismatch_fails(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'db';s,*_=self.chain(p);q=sqlite3.connect(p);q.execute('UPDATE head SET sequence=99');q.commit();q.close();self.assertRaises(IntegrityError,s.verify_history)
 def test_unknown_reconciliation_requires_verified_history(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'db';s=self.store(p);proposal,_,_=self.rotation('unknown');self.assertRaises(UnknownOutcome,s.commit,proposal,True);self.assertEqual(s.reconcile_verified(proposal)['proposal_id'],'unknown');q=sqlite3.connect(p);raw=json.loads(q.execute("SELECT proof_json FROM transitions WHERE proposal_id='unknown'").fetchone()[0]);raw['sig3'][0]['signature']='ff'*32;q.execute("UPDATE transitions SET proof_json=? WHERE proposal_id='unknown'",(json.dumps(raw,sort_keys=True,separators=(',',':')),));q.commit();q.close();self.assertRaises(ThresholdError,s.reconcile_verified,proposal)
 def test_proof_material_is_durable(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'db';s,p1,*_=self.chain(p);q=sqlite3.connect(p);raw=json.loads(q.execute('SELECT proof_json FROM transitions WHERE sequence=1').fetchone()[0]);q.close();self.assertGreaterEqual(len(raw['sig1']),2);self.assertGreaterEqual(len(raw['sig2']),2);self.assertGreaterEqual(len(raw['sig3']),2);self.assertEqual(raw['transition_digest'],p1.transition_digest)
 def test_unsafe_reader_accepts_broken_history(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'db';s,p1,*_=self.chain(p);q=sqlite3.connect(p);q.execute("UPDATE transitions SET predecessor_root_id='evil' WHERE sequence=1");q.commit();self.assertIsNotNone(UnsafeEvidenceReader().reconcile(q,p1.proposal_id));q.close();self.assertRaises(IntegrityError,s.verify_history)
if __name__=='__main__':unittest.main()
