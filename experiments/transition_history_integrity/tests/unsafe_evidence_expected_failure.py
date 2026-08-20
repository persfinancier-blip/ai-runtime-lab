import sqlite3,tempfile,unittest
from pathlib import Path
from experiments.transition_history_integrity.tests.test_protocol import Tests
from experiments.transition_history_integrity.protocol import UnsafeEvidenceReader
class UnsafeBaseline(Tests):
 def test_tampered_evidence_should_not_be_accepted_but_is(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'db';s,p1,*_=self.chain(p);q=sqlite3.connect(p);q.execute("UPDATE transitions SET predecessor_root_id='evil' WHERE sequence=1");q.commit();accepted=UnsafeEvidenceReader().reconcile(q,p1.proposal_id);q.close();self.assertIsNone(accepted,'unsafe reconciliation trusted JSON despite broken history')
if __name__=='__main__':unittest.main()
