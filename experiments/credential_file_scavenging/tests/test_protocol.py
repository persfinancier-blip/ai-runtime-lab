import json,os,tempfile,unittest
from pathlib import Path
from experiments.credential_file_scavenging.protocol import *
from experiments.supervisor_restart.protocol import Generations,launch

SECRET=b'super-secret-test-value'
class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.root=Path(self.tmp.name); self.creds=self.root/'creds'; self.creds.mkdir(); self.store=CredentialLeaseStore(self.root/'leases.db',audit_key=b'audit-key')
    def tearDown(self): self.tmp.cleanup()
    def create(self,**kw): return self.store.create_named_fallback(task_id='task-1',credential_id='api',scope='seller-read',secret=SECRET,directory=self.creds,**kw)
    def test_creation_order_reaches_ready_with_strong_identity(self):
        l=self.create(); self.assertEqual(l.status,'READY'); self.assertIsNotNone(l.file); self.assertTrue(l.file.handle_hex)
    def test_crash_after_secret_write_is_reclaimable_from_allocated_lease(self):
        with self.assertRaises(SimulatedCreationCrash) as ctx:self.create(simulate_crash_after_secret_write=True)
        lease_id=str(ctx.exception); l=self.store.load(lease_id); self.assertEqual(l.status,'ALLOCATED'); self.assertEqual((self.creds/l.name).read_bytes(),SECRET)
        ev=self.store.cleanup(lease_id,expected_cleanup_generation=self.store.cleanup_generation()); self.assertEqual(ev['outcome'],'UNLINKED')
    def test_partial_secret_write_crash_is_reclaimable_by_strong_identity(self):
        with self.assertRaises(SimulatedCreationCrash) as ctx:self.create(simulate_crash_after_partial_write=True)
        lease_id=str(ctx.exception); l=self.store.load(lease_id); self.assertEqual(l.status,'ALLOCATED'); self.assertNotEqual((self.creds/l.name).read_bytes(),SECRET)
        ev=self.store.cleanup(lease_id,expected_cleanup_generation=self.store.cleanup_generation()); self.assertEqual(ev['outcome'],'UNLINKED')
    def test_crash_before_handoff_reclaimed(self):
        l=self.create(); p=self.creds/l.name; ev=self.store.cleanup(l.lease_id,expected_cleanup_generation=self.store.cleanup_generation()); self.assertFalse(p.exists()); self.assertEqual(ev['outcome'],'UNLINKED')
    def test_live_child_protected_until_exit(self):
        l=self.create(); proc,rec,pidfd=launch('task-1',Generations(1,l.credential_generation,1),seconds=30); os.close(pidfd)
        try:self.store.handoff(l.lease_id,rec); self.assertRaises(LiveOwner,self.store.cleanup,l.lease_id,expected_cleanup_generation=self.store.cleanup_generation()); self.assertTrue((self.creds/l.name).exists())
        finally:proc.kill();proc.wait()
        self.assertEqual(self.store.cleanup(l.lease_id,expected_cleanup_generation=self.store.cleanup_generation())['status'],'CLEANED')
    def test_rotation_does_not_delete_live_old_child(self):
        l=self.create(); proc,rec,pidfd=launch('task-1',Generations(1,l.credential_generation,1),seconds=30); os.close(pidfd)
        try:self.store.handoff(l.lease_id,rec); self.store.rotate_credential_generation(); self.assertRaises(LiveOwner,self.store.cleanup,l.lease_id,expected_cleanup_generation=self.store.cleanup_generation())
        finally:proc.kill();proc.wait()
        self.store.cleanup(l.lease_id,expected_cleanup_generation=self.store.cleanup_generation())
    def test_stale_cleanup_generation(self):
        l=self.create(); old=self.store.cleanup_generation(); self.store.advance_cleanup_generation(); self.assertRaises(StaleCleanupGeneration,self.store.cleanup,l.lease_id,expected_cleanup_generation=old); self.assertTrue((self.creds/l.name).exists())
    def test_byte_identical_replacement_rejected_by_opaque_handle(self):
        l=self.create(); p=self.creds/l.name; data=p.read_bytes(); p.unlink(); p.write_bytes(data); os.chmod(p,0o600); self.assertRaises(ObjectIdentityMismatch,self.store.cleanup,l.lease_id,expected_cleanup_generation=self.store.cleanup_generation())
    def test_symlink_substitution_rejected(self):
        l=self.create(); p=self.creds/l.name; p.unlink(); t=self.root/'target'; t.write_bytes(SECRET); p.symlink_to(t); self.assertRaises(ObjectIdentityMismatch,self.store.cleanup,l.lease_id,expected_cleanup_generation=self.store.cleanup_generation()); self.assertTrue(t.exists())
    def test_directory_replacement_rejected(self):
        l=self.create(); old=self.root/'old'; self.creds.rename(old); self.creds.mkdir(); (self.creds/l.name).write_bytes(SECRET); self.assertRaises(NamespaceIdentityMismatch,self.store.cleanup,l.lease_id,expected_cleanup_generation=self.store.cleanup_generation())
    def test_unknown_after_unlink_reconciles(self):
        l=self.create(); g=self.store.cleanup_generation(); self.assertRaises(UnknownCleanupOutcome,self.store.cleanup,l.lease_id,expected_cleanup_generation=g,simulate_unknown_after_unlink=True); self.assertFalse((self.creds/l.name).exists()); ev=self.store.reconcile_cleanup(l.lease_id,expected_cleanup_generation=g); self.assertEqual(ev['outcome'],'MISSING_RECONCILED'); self.assertEqual(self.store.reconcile_cleanup(l.lease_id,expected_cleanup_generation=g),ev)
    def test_secret_absent_from_db_and_evidence(self):
        l=self.create(); self.store.cleanup(l.lease_id,expected_cleanup_generation=self.store.cleanup_generation()); self.assertNotIn(SECRET,(self.root/'leases.db').read_bytes()); self.assertNotIn(SECRET.decode(),json.dumps(self.store.evidence(l.lease_id)))
    def test_unsafe_glob_can_delete_live_file(self):
        l=self.create(); proc,rec,pidfd=launch('task-1',Generations(1,l.credential_generation,1),seconds=30); os.close(pidfd)
        try:self.store.handoff(l.lease_id,rec); UnsafeGlobCleanup().cleanup(self.creds); self.assertFalse((self.creds/l.name).exists())
        finally:proc.kill();proc.wait()
if __name__=='__main__':unittest.main()
