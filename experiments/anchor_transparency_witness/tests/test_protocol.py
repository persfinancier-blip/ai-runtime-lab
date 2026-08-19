import tempfile, unittest
from pathlib import Path
from experiments.anchor_transparency_witness.protocol import Checkpoint, ReferenceLog, CheckpointObserver, ConsistencyError, InvalidCheckpoint, ReplayDetected, SplitViewDetected, StaleCheckpoint, Witness, WitnessPolicy, WitnessStore, WitnessThresholdError
class WitnessTests(unittest.TestCase):
    def setUp(self): self.log_key=b'log-key'; self.w1=b'w1'; self.w2=b'w2'; self.w3=b'w3'; self.tmp=tempfile.TemporaryDirectory(); self.base=Path(self.tmp.name)
    def tearDown(self): self.tmp.cleanup()
    def witness(self,name,key): return Witness(name,key,'log-A',self.log_key,WitnessStore(self.base/f'{name}.json'))
    def test_linear_history_accepts_valid_extension(self):
        log=ReferenceLog('log-A',self.log_key,[b'a']); w=self.witness('w1',self.w1); c1=log.checkpoint(); w.observe(c1); log.append(b'b'); c2=log.checkpoint(); sig=w.observe(c2,log.consistency_from(c1)); self.assertEqual(w.store.load(),c2); self.assertEqual(sig.checkpoint_id,c2.identity())
    def test_structural_bool_version_is_rejected(self):
        log=ReferenceLog('log-A',self.log_key,[b'a']); good=log.checkpoint(); bad=Checkpoint(True,good.log_id,good.size,good.root_hash,good.sequence,good.signature); w=self.witness('w1',self.w1)
        with self.assertRaises(InvalidCheckpoint): w.observe(bad)
    def test_same_size_different_root_detected(self):
        l1=ReferenceLog('log-A',self.log_key,[b'a']); l2=ReferenceLog('log-A',self.log_key,[b'x']); w=self.witness('w1',self.w1); w.observe(l1.checkpoint());
        with self.assertRaises(SplitViewDetected): w.observe(l2.checkpoint())
    def test_larger_without_consistency_rejected(self):
        log=ReferenceLog('log-A',self.log_key,[b'a']); w=self.witness('w1',self.w1); w.observe(log.checkpoint()); log.append(b'b');
        with self.assertRaises(ConsistencyError): w.observe(log.checkpoint())
    def test_fork_after_common_predecessor_detected_when_observed(self):
        common=[b'a']; base=ReferenceLog('log-A',self.log_key,common); w=self.witness('w1',self.w1); c1=base.checkpoint(); w.observe(c1); f1=ReferenceLog('log-A',self.log_key,common+[b'good']); f2=ReferenceLog('log-A',self.log_key,common+[b'evil']); w.observe(f1.checkpoint(),f1.consistency_from(c1))
        with self.assertRaises(SplitViewDetected): w.observe(f2.checkpoint())
    def test_replay_old_checkpoint_rejected(self):
        log=ReferenceLog('log-A',self.log_key,[b'a']); w=self.witness('w1',self.w1); c1=log.checkpoint(); w.observe(c1); log.append(b'b'); c2=log.checkpoint(); w.observe(c2,log.consistency_from(c1))
        with self.assertRaises(ReplayDetected): w.observe(c1)
    def test_stale_checkpoint_surfaces_stale(self):
        log=ReferenceLog('log-A',self.log_key,[b'a']); w=self.witness('w1',self.w1); c=log.checkpoint(); w.observe(c)
        with self.assertRaises(StaleCheckpoint): w.observe(c)
    def test_restart_preserves_watermark(self):
        log=ReferenceLog('log-A',self.log_key,[b'a']); w=self.witness('w1',self.w1); c=log.checkpoint(); w.observe(c); w2=self.witness('w1',self.w1); self.assertEqual(w2.store.load(),c)
        with self.assertRaises(StaleCheckpoint): w2.observe(c)
    def test_freeze_surfaces_stale_by_trusted_local_freshness_policy(self):
        log=ReferenceLog('log-A',self.log_key,[b'a']); w=self.witness('w1',self.w1); c=log.checkpoint(); w.observe(c,accepted_at=100); self.assertEqual(w.freshness(105,10),'CURRENT'); self.assertEqual(w.freshness(111,10),'STALE')
    def test_restart_can_verify_next_extension_from_self_contained_proof(self):
        log=ReferenceLog('log-A',self.log_key,[b'a']); w=self.witness('w1',self.w1); c1=log.checkpoint(); w.observe(c1); log.append(b'b'); c2=log.checkpoint(); restarted=self.witness('w1',self.w1); restarted.observe(c2,log.consistency_from(c1)); self.assertEqual(restarted.store.load(),c2)
    def test_threshold_policy_counts_unique_witnesses(self):
        log=ReferenceLog('log-A',self.log_key,[b'a']); cp=log.checkpoint(); a=self.witness('w1',self.w1).observe(cp); b=self.witness('w2',self.w2).observe(cp); policy=WitnessPolicy({'w1':self.w1,'w2':self.w2,'w3':self.w3},2); self.assertEqual(policy.verify(cp,[a,b,a]),('w1','w2'))
        with self.assertRaises(WitnessThresholdError): policy.verify(cp,[a,a])
    def test_threshold_rejects_one_witness(self):
        log=ReferenceLog('log-A',self.log_key,[b'a']); cp=log.checkpoint(); a=self.witness('w1',self.w1).observe(cp)
        with self.assertRaises(WitnessThresholdError): WitnessPolicy({'w1':self.w1,'w2':self.w2},2).verify(cp,[a])

    def test_observer_detects_conflict_across_independent_witness_paths(self):
        a=ReferenceLog('log-A',self.log_key,[b'common',b'good']).checkpoint()
        b=ReferenceLog('log-A',self.log_key,[b'common',b'evil']).checkpoint()
        # Separate witnesses can TOFU different forks; detection occurs when their views are compared.
        self.witness('w1',self.w1).observe(a)
        self.witness('w2',self.w2).observe(b)
        observer=CheckpointObserver(); observer.observe(a)
        with self.assertRaises(SplitViewDetected): observer.observe(b)

    def test_bad_explicit_extension_detected(self):
        log=ReferenceLog('log-A',self.log_key,[b'a']); w=self.witness('w1',self.w1); c1=log.checkpoint(); w.observe(c1); log.append(b'b'); c2=log.checkpoint(); bad=log.consistency_from(c1); bad=type(bad)(bad.old_size,bad.old_root,bad.new_size,bad.prior_leaves_hex,(b'evil'.hex(),))
        with self.assertRaises(SplitViewDetected): w.observe(c2,bad)
if __name__=='__main__': unittest.main()
