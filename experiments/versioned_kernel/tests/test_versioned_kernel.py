import unittest
from dataclasses import asdict
from experiments.versioned_kernel.protocol import *

class VersionedKernelTests(unittest.TestCase):
    def test_classification_matrix(self):
        s=v1_state(); self.assertEqual(classify_state(s),'MIGRATE'); s2=migrate_v1_to_v2(s); self.assertEqual(classify_state(s2),'ACCEPT'); s3=s2.clone(); s3.protocol_version=1; self.assertEqual(classify_state(s3),'TRANSLATE'); sf=s2.clone(); sf.storage_version=99; self.assertEqual(classify_state(sf),'REJECT')
    def test_v1_to_v2_preserves_semantics_and_identity(self):
        s=v1_state(); m=migrate_v1_to_v2(s); self.assertEqual(semantic_projection(s),semantic_projection(m)); self.assertGreater(m.migration_epoch,s.migration_epoch); self.assertGreater(m.fence,s.fence)
    def test_future_version_hard_rejected(self):
        s=v1_state(); s.storage_version=3
        with self.assertRaises(FutureVersionError): migrate_v1_to_v2(s)
    def test_old_worker_fenced_after_migration(self):
        s=v1_state(); k=VersionedKernel(s); m=k.migrate()
        with self.assertRaises(OldWorkerError): k.load_for_worker(1,0)
        with self.assertRaises(OldWorkerError): k.mutate_phase(0,s.fence,'DONE')
        k.mutate_phase(m.worker_epoch,m.fence,'DONE'); self.assertEqual(k.state.phase,'DONE')
    def test_migration_crash_retry_is_idempotent(self):
        s=v1_state(); k=VersionedKernel(s)
        with self.assertRaises(MigrationError): k.migrate(crash=True)
        self.assertEqual(asdict(k.state),asdict(s)); a=k.migrate(); b=k.migrate(); self.assertEqual(asdict(a),asdict(b))
    def test_identity_survives(self):
        s=v1_state(); m=migrate_v1_to_v2(s); self.assertEqual((m.effect_receipt,m.evidence_id,m.effect_key,m.artifact_version),(s.effect_receipt,s.evidence_id,s.effect_key,s.artifact_version))
    def test_trace_translation_and_rejection(self):
        old=['claim','intent','effect_unknown','effect_ok','evidence','done','invalidate']; expected=['claim','prepare_effect','mark_unknown','confirm_effect','append_evidence','complete','invalidate']; self.assertEqual(translate_trace(old,from_protocol=1),expected)
        with self.assertRaises(TraceTranslationError): translate_action('removed_without_mapping',from_protocol=1)
    def test_pre_post_semantic_projection_conforms(self):
        s=v1_state(phase='UNKNOWN',effect_receipt=None); self.assertEqual(semantic_projection(s),semantic_projection(migrate_v1_to_v2(s)))
    def test_seeded_unsafe_is_corrupt(self):
        s=v1_state(); bad=unsafe_migrate_v1_to_v2(s); self.assertNotEqual(semantic_projection(s),semantic_projection(bad)); self.assertEqual(bad.migration_epoch,s.migration_epoch)
    def test_new_state_rejected_by_old_worker(self):
        k=VersionedKernel(migrate_v1_to_v2(v1_state()))
        with self.assertRaises(OldWorkerError): k.load_for_worker(1,k.state.worker_epoch)
    def test_rolling_overlap(self):
        s=v1_state(); k=VersionedKernel(s); self.assertEqual(k.load_for_worker(2,0).storage_version,1); m=k.migrate(); self.assertEqual(k.load_for_worker(2,m.worker_epoch).storage_version,2)
