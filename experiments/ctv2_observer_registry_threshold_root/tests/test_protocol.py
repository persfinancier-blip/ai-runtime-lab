import tempfile,unittest
from pathlib import Path
from experiments.ctv2_observer_registry_threshold_root.protocol import *

def keys(prefix,n):
    raw=[f"{prefix}-{i}".encode() for i in range(n)]
    return raw,{key_id(k):k.hex() for k in raw}
def sigs(raw,payload,idxs):
    return tuple(Signature(key_id(raw[i]),sign(raw[i],payload)) for i in idxs)

class Tests(unittest.TestCase):
    def setUp(self):
        self.old_raw,old_keys=keys("old",3); self.new_raw,new_keys=keys("new",4); self.rec_raw,rec_keys=keys("recovery",4)
        self.obs1=b"observer-1"; self.obs2=b"observer-2"
        self.root1=RootState("registry-A",1,5,2,old_keys)
        self.root2=RootState("registry-A",2,5,3,new_keys)
        self.recovery=RecoveryAuthority(9,3,rec_keys)
        self.members={
            "o1":{"observer_id":"o1","generation":1,"status":"ACTIVE","key_hex":self.obs1.hex()},
            "o2":{"observer_id":"o2","generation":1,"status":"ACTIVE","key_hex":self.obs2.hex()},
        }
    def auth(self,store=None): return RegistryAuthority(self.root1,self.recovery,store)
    def snapshot(self,a,version=1,generation=1,previous=None,root=None,members=None,threshold=2,raw=None,idxs=None):
        root=root or a.current_root(); members=members or self.members
        u={"registry_id":"registry-A","version":version,"generation":generation,"threshold":threshold,
           "observers":members,"previous_digest":previous,"root_version":root.version,"authority_epoch":root.authority_epoch,"root_id":root.root_id}
        raw=raw or (self.old_raw if root.version==1 else self.new_raw)
        idxs=idxs if idxs is not None else list(range(root.threshold))
        return RegistrySnapshot(**u,signatures=sigs(raw,u,idxs))
    def rotate(self,a):
        p=rotation_payload(self.root1,self.root2)
        return a.rotate_root(self.root2,sigs(self.old_raw,p,[0,1]),sigs(self.new_raw,p,[0,1,2]))
    def test_threshold_bootstrap_snapshot(self):
        a=self.auth(); s=self.snapshot(a); a.accept_snapshot(s); self.assertEqual(a.current_snapshot().root_id,self.root1.root_id)
    def test_single_compromised_signer_cannot_rewrite_membership(self):
        a=self.auth(); s=self.snapshot(a,idxs=[0])
        with self.assertRaises(ThresholdError): a.accept_snapshot(s)
    def test_normal_rotation_requires_old_and_new_threshold(self):
        a=self.auth(); self.rotate(a); self.assertEqual(a.current_root().root_id,self.root2.root_id)
        p=rotation_payload(self.root1,self.root2)
        with self.assertRaises(ThresholdError): self.auth().rotate_root(self.root2,sigs(self.old_raw,p,[0]),sigs(self.new_raw,p,[0,1,2]))
    def test_duplicate_and_revoked_signers_do_not_inflate_threshold(self):
        r=RootState("registry-A",1,5,2,self.root1.keys,(key_id(self.old_raw[0]),))
        a=RegistryAuthority(r,self.recovery)
        s=self.snapshot(a,root=r,raw=self.old_raw,idxs=[0,0,1])
        with self.assertRaises(ThresholdError): a.accept_snapshot(s)
    def test_stale_root_cannot_sign_new_registry_snapshot_after_rotation(self):
        a=self.auth(); s1=self.snapshot(a); a.accept_snapshot(s1); self.rotate(a)
        stale=self.snapshot(a,version=2,generation=2,previous=s1.snapshot_id,root=self.root1,raw=self.old_raw,idxs=[0,1])
        with self.assertRaises(ThresholdError): a.accept_snapshot(stale)
    def test_new_root_snapshot_is_bound_to_exact_version_epoch(self):
        a=self.auth(); s1=self.snapshot(a); a.accept_snapshot(s1); self.rotate(a)
        s2=self.snapshot(a,version=2,generation=2,previous=s1.snapshot_id,root=self.root2); a.accept_snapshot(s2)
        bad=RegistrySnapshot(s2.registry_id,3,3,s2.threshold,s2.observers,s2.snapshot_id,2,999,s2.root_id,s2.signatures)
        with self.assertRaises(SubstitutionError): a.accept_snapshot(bad)
    def test_root_rollback_rejected(self):
        a=self.auth(); self.rotate(a)
        with self.assertRaises(RollbackError): a.rotate_root(self.root2,(),())
    def test_break_glass_uses_separate_recovery_quorum_and_epoch(self):
        a=self.auth(); recovered=RootState("registry-A",2,6,2,self.root2.keys); p=recovery_payload(self.root1,recovered,self.recovery)
        a.recover_root(recovered,sigs(self.rec_raw,p,[0,1,2])); self.assertEqual(a.current_root().authority_epoch,6)
        with self.assertRaises(ThresholdError): self.auth().recover_root(recovered,sigs(self.old_raw,p,[0,1,2]))
    def test_recovery_below_quorum_rejected(self):
        a=self.auth(); recovered=RootState("registry-A",2,6,2,self.root2.keys); p=recovery_payload(self.root1,recovered,self.recovery)
        with self.assertRaises(ThresholdError): a.recover_root(recovered,sigs(self.rec_raw,p,[0,1]))
    def test_historical_evidence_keeps_exact_root_and_registry_identity(self):
        a=self.auth(); s1=self.snapshot(a); a.accept_snapshot(s1)
        e=ObserverEvidence.issue(key=self.obs1,observer_id="o1",observer_generation=1,registry_snapshot_id=s1.snapshot_id,root_id=s1.root_id,payload_digest="p")
        self.rotate(a); members2={**self.members,"o1":{**self.members["o1"],"status":"REVOKED"}}
        s2=self.snapshot(a,version=2,generation=2,previous=s1.snapshot_id,root=self.root2,members=members2,threshold=1); a.accept_snapshot(s2)
        self.assertTrue(a.verify_evidence(e,historical=True))
        with self.assertRaises(EvidenceError): a.verify_evidence(e,historical=False)
    def test_restart_persists_root_and_registry_and_rejects_tamper(self):
        with tempfile.TemporaryDirectory() as td:
            st=JsonStore(Path(td)/"state.json"); a=self.auth(st); s1=self.snapshot(a); a.accept_snapshot(s1); self.rotate(a)
            s2=self.snapshot(a,version=2,generation=2,previous=s1.snapshot_id,root=self.root2); a.accept_snapshot(s2)
            b=RegistryAuthority(self.root1,self.recovery,st)
            self.assertEqual(b.current_root().root_id,self.root2.root_id); self.assertEqual(b.current_snapshot().snapshot_id,s2.snapshot_id)
            raw=st.load(); raw["roots"][self.root2.root_id]["threshold"]=1; st.save(raw)
            with self.assertRaises(IntegrityError): RegistryAuthority(self.root1,self.recovery,st)
    def test_recovery_authority_substitution_on_restart_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            st=JsonStore(Path(td)/"state.json"); self.auth(st)
            _,evil_keys=keys("evil-recovery",2); evil=RecoveryAuthority(9,1,evil_keys)
            with self.assertRaises(IntegrityError): RegistryAuthority(self.root1,evil,st)
    def test_quorum_counts_distinct_active_observers_under_exact_snapshot(self):
        a=self.auth(); s=self.snapshot(a); a.accept_snapshot(s)
        e1=ObserverEvidence.issue(key=self.obs1,observer_id="o1",observer_generation=1,registry_snapshot_id=s.snapshot_id,root_id=s.root_id,payload_digest="p")
        e2=ObserverEvidence.issue(key=self.obs2,observer_id="o2",observer_generation=1,registry_snapshot_id=s.snapshot_id,root_id=s.root_id,payload_digest="p")
        self.assertFalse(a.quorum([e1,e1],"p")); self.assertTrue(a.quorum([e1,e2],"p"))
    def test_strict_bool_not_accepted_as_versions(self):
        with self.assertRaises(IntegrityError): RootState("registry-A",True,5,2,self.root1.keys).validate()
    def test_restart_rejects_fabricated_root_transition_history(self):
        with tempfile.TemporaryDirectory() as td:
            st=JsonStore(Path(td)/"state.json"); a=self.auth(st); self.rotate(a)
            raw=st.load(); raw["root_transitions"]=[]; st.save(raw)
            with self.assertRaises(IntegrityError): RegistryAuthority(self.root1,self.recovery,st)
    def test_restart_rejects_bootstrap_root_substitution(self):
        with tempfile.TemporaryDirectory() as td:
            st=JsonStore(Path(td)/"state.json"); self.auth(st)
            _,other_keys=keys("other-bootstrap",2); other=RootState("registry-A",1,5,2,other_keys)
            with self.assertRaises(IntegrityError): RegistryAuthority(other,self.recovery,st)

if __name__=="__main__": unittest.main()
