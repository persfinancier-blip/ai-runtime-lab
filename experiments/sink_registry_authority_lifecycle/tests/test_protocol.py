import json,sqlite3,tempfile,threading,unittest
from pathlib import Path
from experiments.anchor_threshold_root.protocol import RootState,RecoveryAuthority,Signature,key_id,rotation_payload,recovery_payload,sign
from experiments.sink_registry_binding.protocol import RegistryEntry
from experiments.sink_registry_authority_lifecycle.protocol import *

def keys(prefix,n=3):
    raw=[f'{prefix}-{i}'.encode() for i in range(n)]; return raw,{key_id(k):k.hex() for k in raw}
def root(version,epoch,prefix,threshold=2):
    raw,k=keys(prefix); return RootState('sink-registry',version,epoch,threshold,k),raw
def recovery():
    raw,k=keys('recovery',4); return RecoveryAuthority(1,3,k),raw
def sigs(raw,p,count=2): return tuple(Signature(key_id(k),sign(k,p)) for k in raw[:count])
def entry(r,signer,generation=1,pred=None):
    return RegistryEntry('sink-A',generation,'a'*64,'https://sink.example','charge:v1',pred,key_id(signer),r.version)

class Tests(unittest.TestCase):
    def setUp(self): self.r1,self.k1=root(1,1,'r1'); self.rec,self.kr=recovery()
    def store(self,path): return DurableRegistryAuthority(path,self.r1,self.rec)
    def rotate(self,s,new=None):
        r2,k2=(new or root(2,1,'r2')); p=rotation_payload(self.r1,r2); s.rotate(r2,sigs(self.k1,p),sigs(k2,p)); return r2,k2
    def test_bootstrap_restart_and_current_identity(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'db'; s=self.store(p); self.assertEqual(root_id(s.current()),root_id(self.r1)); self.assertTrue(DurableRegistryAuthority(p,self.r1,self.rec).verify_durable(self.r1,self.rec))
    def test_normal_rotation_requires_old_and_new_threshold(self):
        with tempfile.TemporaryDirectory() as td:
            s=self.store(Path(td)/'db'); r2,k2=root(2,1,'r2'); p=rotation_payload(self.r1,r2)
            with self.assertRaises(Exception): s.rotate(r2,sigs(self.k1,p,1),sigs(k2,p))
            s.rotate(r2,sigs(self.k1,p),sigs(k2,p)); self.assertEqual(s.current().version,2)
    def test_same_generation_substitution_rejected_by_restart_identity(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'db'; s=self.store(p); fake,_=root(1,1,'different')
            with self.assertRaises(AuthorityRollback): s.assert_current(fake)
    def test_old_signer_cannot_publish_after_rotation_but_history_verifies(self):
        with tempfile.TemporaryDirectory() as td:
            s=self.store(Path(td)/'db'); signed=s.issue(entry(self.r1,self.k1[0]),self.k1[0]); d=s.accept_entry(signed); self.rotate(s)
            with self.assertRaises(EntryAuthError): s.issue(entry(self.r1,self.k1[0],generation=2,pred=d),self.k1[0])
            self.assertEqual(s.verify_historical_entry(d).entry_digest,d)
    def test_missing_historical_authority_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'db'; s=self.store(p); signed=s.issue(entry(self.r1,self.k1[0]),self.k1[0]); d=s.accept_entry(signed); aid=root_id(self.r1); q=sqlite3.connect(p); q.execute('DELETE FROM registry_authorities WHERE authority_id=?',(aid,)); q.commit(); q.close()
            with self.assertRaises(HistoricalAuthorityMissing): s.verify_historical_entry(d)
    def test_corrupt_historical_authority_fails_restart(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'db'; self.store(p); q=sqlite3.connect(p); q.execute("UPDATE registry_authorities SET body='{}'"); q.commit(); q.close()
            with self.assertRaises(Exception): DurableRegistryAuthority(p,self.r1,self.rec)
    def test_break_glass_recovery_is_separate(self):
        with tempfile.TemporaryDirectory() as td:
            s=self.store(Path(td)/'db'); r2,k2=root(2,2,'recovered'); p=recovery_payload(self.r1,r2,self.rec.generation)
            with self.assertRaises(Exception): s.recover(r2,sigs(self.kr,p,2))
            s.recover(r2,sigs(self.kr,p,3)); self.assertEqual(s.current().authority_epoch,2)
    def test_recovery_authority_substitution_rejected_on_restart(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'db'; self.store(p); other,okr=keys('other-recovery',4); bad=RecoveryAuthority(1,3,okr)
            with self.assertRaises(UnsafeRecovery): DurableRegistryAuthority(p,self.r1,bad)
    def test_rotation_vs_publication_serializes(self):
        with tempfile.TemporaryDirectory() as td:
            s=self.store(Path(td)/'db'); old=s.issue(entry(self.r1,self.k1[0]),self.k1[0]); r2,k2=root(2,1,'r2'); p=rotation_payload(self.r1,r2); out=[]; gate=threading.Barrier(3)
            def pub():
                gate.wait()
                try: s.accept_entry(old); out.append('published')
                except EntryAuthError: out.append('stale')
            def rot():
                gate.wait(); s.rotate(r2,sigs(self.k1,p),sigs(k2,p)); out.append('rotated')
            a=threading.Thread(target=pub); b=threading.Thread(target=rot); a.start(); b.start(); gate.wait(); a.join(); b.join(); self.assertIn('rotated',out); self.assertTrue(any(x in out for x in ('published','stale'))); self.assertTrue(s.verify_durable(self.r1,self.rec))
    def test_revocation_blocks_new_use_without_rewriting_prior_snapshot(self):
        with tempfile.TemporaryDirectory() as td:
            s=self.store(Path(td)/'db'); signed=s.issue(entry(self.r1,self.k1[0]),self.k1[0]); d=s.accept_entry(signed)
            r2,k2=root(2,1,'r2'); merged=dict(r2.keys); merged[key_id(self.k1[0])]=self.k1[0].hex(); r2=RootState('sink-registry',2,1,2,merged,(key_id(self.k1[0]),)); p=rotation_payload(self.r1,r2); s.rotate(r2,sigs(self.k1,p),sigs(k2,p))
            self.assertEqual(s.verify_historical_entry(d).entry_digest,d)
            with self.assertRaises(EntryAuthError): s.issue(RegistryEntry('sink-A',2,'a'*64,'https://sink.example','charge:v1',d,key_id(self.k1[0]),2),self.k1[0])
    def test_unsafe_ambient_key_self_swap(self):
        u=UnsafeAmbientAuthority(b'old'); self.assertTrue(u.replace(b'attacker'))

if __name__=='__main__': unittest.main()
