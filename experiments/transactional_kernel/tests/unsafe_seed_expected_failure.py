import sqlite3, tempfile, unittest
from pathlib import Path
from experiments.transactional_kernel.kernel import Kernel, unsafe_split_complete

class UnsafeSplitTransaction(unittest.TestCase):
    def test_split_completion_should_never_commit_done_with_invalid_evidence(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'k.db'; k=Kernel(p); k.ensure_work('w')
            f,_=k.claim('w','a'); k.prepare_intent('w','a',f,'ek'); k.confirm_effect('w','a',f,'r'); k.append_evidence('w','ev','v1')
            self.assertTrue(unsafe_split_complete(p,'w','ev'))
            k.invalidate('ev')
            c=sqlite3.connect(p,isolation_level=None); c.execute("update work set phase='DONE',done_evidence_id='ev' where work_id='w'"); c.close()
            c=sqlite3.connect(p); valid=c.execute("select valid from evidence where evidence_id='ev'").fetchone()[0]; c.close()
            self.assertFalse(k.state('w')['phase']=='DONE' and valid==0, 'unsafe split transaction committed invalid DONE')

if __name__=='__main__': unittest.main()
