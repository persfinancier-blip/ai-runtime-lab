import tempfile,threading,unittest
from pathlib import Path
from experiments.ctv2_bundle_authority_lifecycle.protocol import *

def keys(prefix,n):
    raw=[f'{prefix}-{i}'.encode() for i in range(n)]
    return raw,{kid(k):k.hex() for k in raw}
def sigs(raw,p,idxs): return tuple(Sig(kid(raw[i]),sign(raw[i],p)) for i in idxs)

class LifecycleTests(unittest.TestCase):
    def setUp(self):
        self.td=tempfile.TemporaryDirectory(); self.db=Path(self.td.name)/'x.db'
        self.r1raw,self.r1keys=keys('root1',3); self.b1raw,self.b1keys=keys('bundle1',2)
        self.r2raw,self.r2keys=keys('root2',3); self.b2raw,self.b2keys=keys('bundle2',2)
        self.recraw,self.reckeys=keys('recovery',3)
        self.r1=Root('bundle-provider',1,7,2,self.r1keys,self.b1keys)
        self.r2=Root('bundle-provider',2,7,2,self.r2keys,self.b2keys)
        self.rec=Recovery(1,2,self.reckeys); self.s=LifecycleStore(self.db,self.r1,self.rec)
    def tearDown(self): self.td.cleanup()
    def rotate(self):
        p=transition_payload(self.r1,self.r2,'rotation')
        return self.s.transition(self.r2,sigs(self.r1raw,p,[0,1]),sigs(self.r2raw,p,[0,1]))
    def bundle(self,root,raw,idx,v,g):
        sid=kid(raw[idx]); return Bundle.issue(bundle_id='release',version=v,generation=g,issued_at=100,root=root,signer_id=sid,key=raw[idx],payload_digest='a'*64)
    def test_current_root_accepts_current_signer(self):
        b=self.bundle(self.r1,self.b1raw,0,1,1); self.s.publish(b); self.assertEqual(self.s.replay(b.bundle_digest)['root_version'],1)
    def test_stale_signer_rejected_after_rotation(self):
        self.rotate()
        with self.assertRaises((StaleRoot,AuthenticationError)): self.s.publish(self.bundle(self.r1,self.b1raw,0,1,1))
    def test_new_signer_rejected_before_transition(self):
        with self.assertRaises((StaleRoot,AuthenticationError)): self.s.publish(self.bundle(self.r2,self.b2raw,0,1,1))
    def test_break_glass_invalidates_old_epoch(self):
        r3=Root('bundle-provider',2,8,2,self.r2keys,self.b2keys)
        p=transition_payload(self.r1,r3,'recovery')
        self.s.transition(r3,recovery_sigs=sigs(self.recraw,p,[0,1]),kind='recovery')
        with self.assertRaises((StaleRoot,AuthenticationError)): self.s.publish(self.bundle(self.r1,self.b1raw,0,1,1))
    def test_restart_reloads_root(self):
        self.rotate(); s2=LifecycleStore(self.db,self.r1,self.rec)
        self.assertEqual(s2.current_root().root_digest,self.r2.root_digest)
        with self.assertRaises(StaleRoot): s2.publish(self.bundle(self.r1,self.b1raw,0,1,1))
    def test_historical_replay_old_bundle_but_not_new_authority(self):
        b1=self.bundle(self.r1,self.b1raw,0,1,1); self.s.publish(b1); self.rotate()
        self.assertEqual(self.s.replay(b1.bundle_digest)['root_version'],1)
        with self.assertRaises((StaleRoot,AuthenticationError)): self.s.publish(self.bundle(self.r1,self.b1raw,1,2,2))
    def test_same_coordinates_substituted_key_material_rejected(self):
        evil=b'evil'; bad=Root('bundle-provider',1,7,2,self.r1keys,{kid(evil):evil.hex()})
        self.assertNotEqual(bad.root_digest,self.r1.root_digest)
        with self.assertRaises(StaleRoot):
            p=transition_payload(self.r1,bad,'rotation')
            self.s.transition(bad,sigs(self.r1raw,p,[0,1]),(),kind='rotation')
    def test_partial_transition_rolls_back(self):
        p=transition_payload(self.r1,self.r2,'rotation')
        with self.assertRaises(RuntimeError): self.s.transition(self.r2,sigs(self.r1raw,p,[0,1]),sigs(self.r2raw,p,[0,1]),failpoint='after_insert')
        self.assertEqual(self.s.current_root().root_digest,self.r1.root_digest)
        self.s.publish(self.bundle(self.r1,self.b1raw,0,1,1))
    def test_root_transition_vs_publication_serializes(self):
        b=self.bundle(self.r1,self.b1raw,0,1,1); p=transition_payload(self.r1,self.r2,'rotation')
        barrier=threading.Barrier(3); out=[]
        def pub():
            barrier.wait()
            try: out.append(('pub','ok',self.s.publish(b)))
            except Exception as e: out.append(('pub',type(e).__name__,None))
        def rot():
            barrier.wait()
            try: out.append(('rot','ok',self.s.transition(self.r2,sigs(self.r1raw,p,[0,1]),sigs(self.r2raw,p,[0,1]))))
            except Exception as e: out.append(('rot',type(e).__name__,None))
        a=threading.Thread(target=pub); c=threading.Thread(target=rot); a.start(); c.start(); barrier.wait(); a.join(); c.join()
        self.assertIn(('rot','ok',self.r2.root_digest),out)
        self.assertEqual(self.s.current_root().root_digest,self.r2.root_digest)
        if any(x[0]=='pub' and x[1]=='ok' for x in out): self.assertEqual(self.s.replay(b.bundle_digest)['historical_root_digest'],self.r1.root_digest)
    def test_rotation_needs_old_and_new_threshold(self):
        p=transition_payload(self.r1,self.r2,'rotation')
        with self.assertRaises(ThresholdError): self.s.transition(self.r2,sigs(self.r1raw,p,[0]),sigs(self.r2raw,p,[0,1]))
        with self.assertRaises(ThresholdError): self.s.transition(self.r2,sigs(self.r1raw,p,[0,1]),sigs(self.r2raw,p,[0]))
    def test_restart_cannot_substitute_recovery_authority(self):
        evilraw,evilkeys=keys('evil-recovery',1)
        s2=LifecycleStore(self.db,self.r1,Recovery(99,1,evilkeys))
        self.assertEqual(s2.recovery.recovery_digest,self.rec.recovery_digest)
        r3=Root('bundle-provider',2,8,2,self.r2keys,self.b2keys)
        p=transition_payload(self.r1,r3,'recovery')
        with self.assertRaises(ThresholdError): s2.transition(r3,recovery_sigs=sigs(evilraw,p,[0]),kind='recovery')
    def test_stored_root_tampering_is_rejected(self):
        c=self.s.connect(); row=c.execute('SELECT root_json FROM roots WHERE root_digest=?',(self.r1.root_digest,)).fetchone(); import json
        x=json.loads(row['root_json']); x['bundle_keys']={}
        c.execute('UPDATE roots SET root_json=? WHERE root_digest=?',(json.dumps(x,sort_keys=True),self.r1.root_digest)); c.commit(); c.close()
        with self.assertRaises(SubstitutionError): self.s.current_root()

if __name__=='__main__': unittest.main()
