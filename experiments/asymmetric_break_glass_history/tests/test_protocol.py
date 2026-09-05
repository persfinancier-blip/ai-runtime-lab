import hashlib,json,sqlite3,tempfile,unittest
from pathlib import Path
from experiments.asymmetric_break_glass_history.protocol import *

def signer(tag): return RecoverySigner(hashlib.sha256(tag.encode()).digest())
def authority(v,g,n=3,t=2,prefix='a'):
    ss=[signer(f'{prefix}-{v}-{g}-{i}') for i in range(n)]
    return RecoveryAuthority.build(v,g,t,[x.public for x in ss]),ss
def sigs(ss,p,n=None): return tuple(x.sign(p) for x in (ss if n is None else ss[:n]))

class Tests(unittest.TestCase):
    def make(self,path):
        a,s=authority(1,1); return PublicOnlyBreakGlassHistory(path,a),a,s
    def boundary(self,h,a,s,cutoff=7):
        p=boundary_payload('a'*64,cutoff,'root-legacy',a)
        return h.establish_boundary('a'*64,cutoff,'root-legacy',sigs(s,p))
    def test_boundary_and_public_only_proof_restart(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'db'; h,a,s=self.make(path); self.boundary(h,a,s)
            p=break_glass_payload(8,'r1','r2',a); h.record_break_glass(8,'r1','r2',sigs(s,p))
            self.assertTrue(PublicOnlyBreakGlassHistory(path,a).verify_durable())
            raw=path.read_bytes(); self.assertNotIn(s[0]._private.private_bytes_raw(),raw)
    def test_legacy_cannot_be_auto_promoted(self):
        with tempfile.TemporaryDirectory() as td:
            h,a,s=self.make(Path(td)/'db'); self.boundary(h,a,s,10); p=break_glass_payload(10,'x','y',a)
            with self.assertRaises(UnsupportedLegacyProof): h.record_break_glass(10,'x','y',sigs(s,p))
    def test_one_old_signer_cannot_create_after_rotation(self):
        with tempfile.TemporaryDirectory() as td:
            h,a,s=self.make(Path(td)/'db'); self.boundary(h,a,s); b,bs=authority(2,2,prefix='b'); rp=rotation_payload(a,b); h.rotate_authority(b,sigs(s,rp),sigs(bs,rp)); p=break_glass_payload(8,'x','y',b)
            with self.assertRaises(ThresholdError): h.record_break_glass(8,'x','y',(s[0].sign(p),))
    def test_old_public_key_verifies_historical_proof_after_rotation(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'db'; h,a,s=self.make(path); self.boundary(h,a,s); p=break_glass_payload(8,'x','y',a); h.record_break_glass(8,'x','y',sigs(s,p)); b,bs=authority(2,2,prefix='b'); rp=rotation_payload(a,b); h.rotate_authority(b,sigs(s,rp),sigs(bs,rp)); self.assertTrue(PublicOnlyBreakGlassHistory(path,a).verify_durable())
    def test_rebind_to_other_successor_detected(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'db'; h,a,s=self.make(path); self.boundary(h,a,s); p=break_glass_payload(8,'x','y',a); h.record_break_glass(8,'x','y',sigs(s,p)); q=sqlite3.connect(path); q.execute("UPDATE break_glass_proofs SET successor_root_id='attacker' WHERE sequence=8"); q.commit(); q.close()
            with self.assertRaises(ProofRebind): PublicOnlyBreakGlassHistory(path,a)
    def test_missing_historical_public_key_detected(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'db'; h,a,s=self.make(path); self.boundary(h,a,s); p=break_glass_payload(8,'x','y',a); h.record_break_glass(8,'x','y',sigs(s,p)); q=sqlite3.connect(path); q.execute('DELETE FROM recovery_authorities WHERE authority_id=?',(a.authority_id,)); q.commit(); q.close()
            with self.assertRaises(IntegrityError): PublicOnlyBreakGlassHistory(path,a)
    def test_forged_public_key_substitution_detected(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'db'; h,a,s=self.make(path); q=sqlite3.connect(path); body=json.loads(q.execute('SELECT body FROM recovery_authorities').fetchone()[0]); body['signers'][0]['public_hex']='00'*32; q.execute('UPDATE recovery_authorities SET body=?',(json.dumps(body,sort_keys=True,separators=(',',':')),)); q.commit(); q.close()
            with self.assertRaises(IntegrityError): PublicOnlyBreakGlassHistory(path,a)
    def test_invalid_signature_noise_does_not_consume_valid_signer(self):
        a,s=authority(1,1); p={'x':1}; bad=Signature(s[0].public.signer_id,'00'*64); accepted=verify_threshold(a,p,(bad,s[0].sign(p),s[1].sign(p))); self.assertEqual(len(accepted),2)
    def test_duplicate_signer_does_not_inflate_quorum(self):
        a,s=authority(1,1); p={'x':1}; one=s[0].sign(p)
        with self.assertRaises(ThresholdError): verify_threshold(a,p,(one,one))
    def test_boundary_tamper_detected(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'db'; h,a,s=self.make(path); self.boundary(h,a,s); q=sqlite3.connect(path); q.execute("UPDATE migration_boundary SET root_id='evil'"); q.commit(); q.close()
            with self.assertRaises(LegacyBoundaryError): PublicOnlyBreakGlassHistory(path,a)
    def test_rotation_proof_corruption_detected(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'db'; h,a,s=self.make(path); b,bs=authority(2,2,prefix='b'); rp=rotation_payload(a,b); h.rotate_authority(b,sigs(s,rp),sigs(bs,rp)); q=sqlite3.connect(path); q.execute("UPDATE recovery_rotations SET old_sigs='[]'"); q.commit(); q.close()
            with self.assertRaises(ThresholdError): PublicOnlyBreakGlassHistory(path,a)
    def test_unsafe_legacy_auto_promotion(self): self.assertTrue(UnsafeLegacyAutoPromotion().promote(4,'legacy-hmac'))
if __name__=='__main__': unittest.main()
