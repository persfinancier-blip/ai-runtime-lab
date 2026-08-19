import tempfile, unittest
from pathlib import Path
from experiments.versioned_kernel.protocol import *
from experiments.versioned_kernel.sqlite_impl import SQLiteVersionedKernel

class SQLiteConformance(unittest.TestCase):
    def kernel(self,s):
        t=tempfile.TemporaryDirectory(); self.addCleanup(t.cleanup); k=SQLiteVersionedKernel(Path(t.name)/'k.db'); k.put(s); return k
    def test_pre_post_projection_matches_reference(self):
        s=v1_state(phase='UNKNOWN',effect_receipt=None); ref=migrate_v1_to_v2(s); k=self.kernel(s); got=k.migrate_v1_to_v2(s.work_id); self.assertEqual(semantic_projection(ref),semantic_projection(got)); self.assertEqual((ref.storage_version,ref.protocol_version,ref.migration_epoch,ref.fence),(got.storage_version,got.protocol_version,got.migration_epoch,got.fence))
    def test_crash_rolls_back_and_retry_succeeds(self):
        s=v1_state(); k=self.kernel(s)
        with self.assertRaises(MigrationError): k.migrate_v1_to_v2(s.work_id,crash=True)
        self.assertEqual(k.get(s.work_id).storage_version,1); a=k.migrate_v1_to_v2(s.work_id); b=k.migrate_v1_to_v2(s.work_id); self.assertEqual(a,b)
    def test_old_worker_fenced(self):
        s=v1_state(); k=self.kernel(s); m=k.migrate_v1_to_v2(s.work_id)
        with self.assertRaises(OldWorkerError): k.mutate_phase(s.work_id,0,s.fence,'DONE')
        k.mutate_phase(s.work_id,m.worker_epoch,m.fence,'DONE'); self.assertEqual(k.get(s.work_id).phase,'DONE')
    def test_future_rejected(self):
        s=migrate_v1_to_v2(v1_state()); s.storage_version=3; k=self.kernel(s)
        with self.assertRaises(FutureVersionError): k.migrate_v1_to_v2(s.work_id)
