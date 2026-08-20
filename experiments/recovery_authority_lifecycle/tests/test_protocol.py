import tempfile,unittest
from pathlib import Path
from experiments.recovery_authority_lifecycle.protocol import *
def mk(prefix,n):
    raw=[f'{prefix}-{i}'.encode() for i in range(n)]; return raw,{kid(k):k.hex() for k in raw}
def sigs(raw,p,ids): return [Sig(kid(raw[i]),sign(raw[i],p)) for i in ids]
class T(unittest.TestCase):
    def setUp(self):
        self.rr,rk=mk('root',3); self.oraw,ok=mk('old',3); self.nraw,nk=mk('new',4)
        self.root=Authority('root','r',1,7,2,rk); self.old=Authority('recovery','r',1,10,2,ok); self.new=Authority('recovery','r',2,11,3,nk)
    def L(self,s=None): return Lifecycle(self.root,self.old,s)
    def triple(self):
        p=rotate_payload(self.root,self.old,self.new); return sigs(self.oraw,p,[0,1]),sigs(self.nraw,p,[0,1,2]),sigs(self.rr,p,[0,1])
    def test_rotation_requires_old_new_root(self):
        a,b,c=self.triple(); l=self.L(); l.rotate_recovery(self.new,a,b,c); self.assertEqual(l.current_recovery(),self.new)
    def test_recovery_alone_cannot_rotate(self):
        a,b,_=self.triple(); self.assertRaises(ThresholdError,self.L().rotate_recovery,self.new,a,b,[])
    def test_one_signer_cannot_rotate(self):
        p=rotate_payload(self.root,self.old,self.new); self.assertRaises(ThresholdError,self.L().rotate_recovery,self.new,sigs(self.oraw,p,[0]),sigs(self.nraw,p,[0]),sigs(self.rr,p,[0]))
    def test_duplicate_does_not_count(self):
        p=rotate_payload(self.root,self.old,self.new); one=sigs(self.oraw,p,[0])[0]; _,b,c=self.triple(); self.assertRaises(ThresholdError,self.L().rotate_recovery,self.new,[one,one],b,c)
    def test_revoked_signer_excluded(self):
        old=Authority('recovery','r',1,10,2,self.old.keys,(kid(self.oraw[0]),)); p=rotate_payload(self.root,old,self.new)
        self.assertRaises(ThresholdError,Lifecycle(self.root,old).rotate_recovery,self.new,sigs(self.oraw,p,[0,1]),sigs(self.nraw,p,[0,1,2]),sigs(self.rr,p,[0,1]))
    def test_rollback_same_version_rejected(self):
        a,b,c=self.triple(); l=self.L(); l.rotate_recovery(self.new,a,b,c); bad=Authority('recovery','r',2,12,3,self.new.keys)
        p=rotate_payload(self.root,self.new,bad); self.assertRaises(RollbackError,l.rotate_recovery,bad,sigs(self.nraw,p,[0,1,2]),sigs(self.nraw,p,[0,1,2]),sigs(self.rr,p,[0,1]))
    def test_restart_revalidates_transition(self):
        with tempfile.TemporaryDirectory() as td:
            st=Store(Path(td)/'s.json'); l=self.L(st); a,b,c=self.triple(); l.rotate_recovery(self.new,a,b,c); self.assertEqual(self.L(st).current_recovery(),self.new)
            raw=st.load(); raw['transitions'][0]['old_sigs'][0]['signature']='00'; st.save(raw); self.assertRaises(ThresholdError,self.L,st)
    def test_stale_recovery_cannot_recover_root(self):
        l=self.L(); a,b,c=self.triple(); l.rotate_recovery(self.new,a,b,c); nr=Authority('root','r',2,8,2,self.root.keys); p=recover_payload(self.root,nr,self.old)
        self.assertRaises(ThresholdError,l.recover_root,nr,sigs(self.oraw,p,[0,1]))
    def test_exact_current_recovery_binds_break_glass(self):
        l=self.L(); a,b,c=self.triple(); l.rotate_recovery(self.new,a,b,c); nr=Authority('root','r',2,8,2,self.root.keys); p=recover_payload(self.root,nr,self.new)
        l.recover_root(nr,sigs(self.nraw,p,[0,1,2])); self.assertEqual(l.historical_recovery(nr.authority_id).authority_id,self.new.authority_id)
    def test_restart_after_root_recovery_revalidates_old_rotation(self):
        with tempfile.TemporaryDirectory() as td:
            st=Store(Path(td)/'s.json'); l=self.L(st); a,b,c=self.triple(); l.rotate_recovery(self.new,a,b,c)
            nr=Authority('root','r',2,8,2,self.root.keys); p=recover_payload(self.root,nr,self.new); l.recover_root(nr,sigs(self.nraw,p,[0,1,2]))
            l2=self.L(st); self.assertEqual(l2.current_root().authority_id,nr.authority_id); self.assertEqual(l2.current_recovery(),self.new)
    def test_bootstrap_substitution_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            st=Store(Path(td)/'s.json'); self.L(st); _,keys=mk('other',3); other=Authority('recovery','r',1,10,2,keys); self.assertRaises(IntegrityError,Lifecycle,self.root,other,st)
    def test_final_boundary_fail_closed(self): self.assertRaises(RecoveryBoundaryError,self.L().final_boundary)
if __name__=='__main__':unittest.main()
