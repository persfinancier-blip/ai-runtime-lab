import tempfile,unittest
from pathlib import Path
from experiments.anchor_threshold_root.protocol import *
def make_keys(prefix,n):
    vals=[f'{prefix}-{i}'.encode() for i in range(n)]; return vals,{key_id(k):k.hex() for k in vals}
def sigs(keys,payload,indexes): return [Signature(key_id(keys[i]),sign(keys[i],payload)) for i in indexes]
class T(unittest.TestCase):
    def setUp(self):
        self.old_raw,old_keys=make_keys('old',3); self.new_raw,new_keys=make_keys('new',4); self.rec_raw,rec_keys=make_keys('recovery',5)
        self.old=RootState('anchor-A',1,7,2,old_keys); self.new=RootState('anchor-A',2,7,3,new_keys); self.rec=RecoveryAuthority(4,3,rec_keys)
    def trust(self,store=None): return ThresholdTrustStore(self.old,self.rec,store)
    def rsigs(self):
        p=rotation_payload(self.old,self.new); return sigs(self.old_raw,p,[0,1]),sigs(self.new_raw,p,[0,1,2])
    def test_normal_rotation_requires_old_and_new_threshold(self):
        a,b=self.rsigs(); ev=self.trust(); out=ev.rotate(self.new,a,b); self.assertEqual(ev.root,self.new); self.assertEqual(len(out['old_signers']),2); self.assertEqual(len(out['new_signers']),3)
    def test_one_compromised_old_signer_cannot_rotate(self):
        _,b=self.rsigs(); p=rotation_payload(self.old,self.new)
        with self.assertRaises(ThresholdError): self.trust().rotate(self.new,sigs(self.old_raw,p,[0]),b)
    def test_new_root_must_meet_own_threshold(self):
        a,_=self.rsigs(); p=rotation_payload(self.old,self.new)
        with self.assertRaises(ThresholdError): self.trust().rotate(self.new,a,sigs(self.new_raw,p,[0,1]))
    def test_duplicate_signer_does_not_count_twice(self):
        _,b=self.rsigs(); p=rotation_payload(self.old,self.new); one=Signature(key_id(self.old_raw[0]),sign(self.old_raw[0],p))
        with self.assertRaises(ThresholdError): self.trust().rotate(self.new,[one,one],b)
    def test_revoked_old_signer_cannot_contribute(self):
        old=RootState('anchor-A',1,7,2,self.old.keys,(key_id(self.old_raw[0]),)); p=rotation_payload(old,self.new)
        with self.assertRaises(ThresholdError): ThresholdTrustStore(old,self.rec).rotate(self.new,sigs(self.old_raw,p,[0,1]),sigs(self.new_raw,p,[0,1,2]))
    def test_cross_provider_substitution_rejected(self):
        bad=RootState('anchor-B',2,7,3,self.new.keys); p=rotation_payload(self.old,bad)
        with self.assertRaises(WrongProvider): self.trust().rotate(bad,sigs(self.old_raw,p,[0,1]),sigs(self.new_raw,p,[0,1,2]))
    def test_stale_version_and_epoch_rejected(self):
        a,b=self.rsigs()
        with self.assertRaises(StaleVersion): self.trust().rotate(RootState('anchor-A',3,7,3,self.new.keys),a,b)
        with self.assertRaises(EpochMismatch): self.trust().rotate(RootState('anchor-A',2,8,3,self.new.keys),a,b)
    def test_break_glass_uses_separate_recovery_quorum(self):
        new=RootState('anchor-A',2,8,2,self.new.keys); p=recovery_payload(self.old,new,self.rec.generation); t=self.trust(); out=t.recover(new,sigs(self.rec_raw,p,[0,1,2])); self.assertEqual(out['recovery_generation'],4); self.assertFalse(t.receipt_is_current(7,1))
    def test_provider_keys_cannot_self_authorize_recovery(self):
        new=RootState('anchor-A',2,8,2,self.new.keys); p=recovery_payload(self.old,new,self.rec.generation)
        with self.assertRaises(ThresholdError): self.trust().recover(new,sigs(self.old_raw,p,[0,1,2]))
    def test_recovery_below_quorum_rejected(self):
        new=RootState('anchor-A',2,8,2,self.new.keys); p=recovery_payload(self.old,new,self.rec.generation)
        with self.assertRaises(ThresholdError): self.trust().recover(new,sigs(self.rec_raw,p,[0,1]))
    def test_revoked_recovery_signer_rejected(self):
        rec=RecoveryAuthority(4,3,self.rec.keys,(key_id(self.rec_raw[0]),)); new=RootState('anchor-A',2,8,2,self.new.keys); p=recovery_payload(self.old,new,rec.generation)
        with self.assertRaises(ThresholdError): ThresholdTrustStore(self.old,rec).recover(new,sigs(self.rec_raw,p,[0,1,2]))
    def test_restart_has_exactly_one_activated_root(self):
        with tempfile.TemporaryDirectory() as td:
            store=AtomicRootStore(Path(td)/'root.json'); t=self.trust(store); a,b=self.rsigs(); t.rotate(self.new,a,b); loaded=store.load(); self.assertEqual(loaded,self.new); self.assertTrue(set(loaded.keys).isdisjoint(set(self.old.keys)))
    def test_evidence_contains_identifiers_not_private_material(self):
        a,b=self.rsigs(); out=self.trust().rotate(self.new,a,b); text=repr(out)
        for k in self.old_raw+self.new_raw+self.rec_raw: self.assertNotIn(k.hex(),text)
    def test_junk_signatures_do_not_break_sufficient_quorum(self):
        a,b=self.rsigs(); p=rotation_payload(self.old,self.new)
        junk=Signature('unknown-key','00'); duplicate=a[0]
        t=self.trust(); t.rotate(self.new,[junk,duplicate,*a],[junk,*b]); self.assertEqual(t.root,self.new)

    def test_recovery_replay_is_rejected_after_epoch_advance(self):
        new=RootState('anchor-A',2,8,2,self.new.keys); p=recovery_payload(self.old,new,self.rec.generation); rs=sigs(self.rec_raw,p,[0,1,2]); t=self.trust(); t.recover(new,rs)
        with self.assertRaises(EpochMismatch): t.recover(new,rs)

    def test_failed_persistence_does_not_activate_candidate(self):
        class FailingStore:
            path=Path('/virtual/already-exists')
            def save(self,state): raise OSError('simulated durable-store failure')
        t=ThresholdTrustStore(self.old,self.rec)
        t.store=FailingStore(); a,b=self.rsigs()
        with self.assertRaises(OSError): t.rotate(self.new,a,b)
        self.assertEqual(t.root,self.old)

if __name__=='__main__': unittest.main()
