import tempfile,unittest
from experiments.sink_registry_migration_checkpoint.protocol import UnsafeAutoPromotion
from experiments.sink_registry_migration_checkpoint.tests.test_protocol import Tests
class Unsafe(Tests):
    def test_legacy_single_signature_should_not_become_threshold_authority(self):
        with tempfile.TemporaryDirectory() as td:
            s=self.store(td);q=s._con();UnsafeAutoPromotion.promote(q);q.commit();count=q.execute('SELECT COUNT(*) FROM registry_threshold_publications').fetchone()[0];q.close();self.assertEqual(count,0)
if __name__=='__main__': unittest.main()
