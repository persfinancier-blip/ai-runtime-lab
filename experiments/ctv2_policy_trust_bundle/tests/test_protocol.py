import tempfile,unittest
from pathlib import Path
from experiments.ctv2_policy_trust_bundle.protocol import *
KEY1=b'authority-one'; KEY2=b'authority-two'
def policy(version=1,generation=1,required_logs=2): return PolicyDocument('ct-policy',version,generation,100,200,required_logs,1,'CURRENT_POLICY')
def trust(version=1,generation=1,tag='A'): return TrustDocument(f'trust-{tag}-{version}',version,generation,90,190,(('log-a','profile-a','op-a','ACTIVE'),('log-b','profile-b','op-b','ACTIVE')))
def bundle(version=1,generation=1,release='release-main',authority_generation=1,p=None,t=None,key=KEY1,signer='root-1',issued_at=95,expires_at=180):
    p=p or policy(version,generation); t=t or trust(version,generation); m=BundleManifest(release,version,generation,issued_at,expires_at,authority_generation,p.content_digest,t.content_digest); return SignedBundle.issue(manifest=m,policy=p,trust=t,signer_id=signer,key=key)
class BundleTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.path=Path(self.tmp.name)/'bundle.db'; self.store=BundleStore(self.path,Authority(1,'root-1',KEY1))
    def tearDown(self): self.store.close(); self.tmp.cleanup()
    def test_valid_bundle_authenticates_exact_pair(self):
        b=bundle(); got=self.store.accept(b,now=100); self.assertEqual((got.policy_digest,got.trust_digest,got.bundle_digest),(b.policy.content_digest,b.trust.content_digest,b.manifest.content_digest))
    def test_mix_and_match_policy_from_other_bundle_rejected(self):
        o=bundle(); mixed=SignedBundle(o.manifest,policy(required_logs=1),o.trust,o.signer_id,o.signature)
        with self.assertRaises(MixAndMatchError): self.store.accept(mixed,now=100)
    def test_mix_and_match_trust_from_other_bundle_rejected(self):
        o=bundle(); mixed=SignedBundle(o.manifest,o.policy,trust(tag='M'),o.signer_id,o.signature)
        with self.assertRaises(MixAndMatchError): self.store.accept(mixed,now=100)
    def test_bad_signature_rejected(self):
        b=bundle(); bad=SignedBundle(b.manifest,b.policy,b.trust,b.signer_id,'00'*32)
        with self.assertRaises(AuthenticationError): self.store.accept(bad,now=100)
    def test_rollback_rejected(self):
        self.store.accept(bundle(),now=100); self.store.accept(bundle(2,2,p=policy(2,2),t=trust(2,2)),now=101)
        with self.assertRaises(RollbackError): self.store.accept(bundle(),now=102)
    def test_same_coordinates_different_content_rejected(self):
        self.store.accept(bundle(),now=100)
        with self.assertRaises(SubstitutionError): self.store.accept(bundle(p=policy(required_logs=1)),now=101)
    def test_partial_update_failpoints_never_expose_half_bundle(self):
        for point in ('after_manifest','after_policy','after_trust','before_commit'):
            with self.subTest(point=point):
                td=tempfile.TemporaryDirectory(); s=BundleStore(Path(td.name)/'db.sqlite',Authority(1,'root-1',KEY1))
                try:
                    with self.assertRaises(RuntimeError): s.accept(bundle(),now=100,failpoint=point)
                    with self.assertRaises(ReplayError): s.active_binding()
                    self.assertEqual([s.db.execute(f'SELECT count(*) FROM {t}').fetchone()[0] for t in ('bundles','policies','trusts','active')],[0,0,0,0])
                finally: s.close(); td.cleanup()
    def test_retry_is_idempotent(self):
        b=bundle(); self.assertEqual(self.store.accept(b,now=100),self.store.accept(b,now=101)); self.assertEqual(self.store.db.execute('SELECT count(*) FROM bundles').fetchone()[0],1)
    def test_historical_replay_uses_exact_bundle_identity(self):
        bind=self.store.accept(bundle(),now=100); self.store.accept(bundle(2,2,p=policy(2,2),t=trust(2,2)),now=101); self.assertEqual(self.store.replay(bind),bind)
    def test_tampered_historical_object_breaks_replay(self):
        bind=self.store.accept(bundle(),now=100); self.store.db.execute('UPDATE policies SET digest=? WHERE bundle_id=? AND version=? AND generation=?',('0'*64,bind.bundle_id,bind.bundle_version,bind.bundle_generation)); self.store.db.commit()
        with self.assertRaises(ReplayError): self.store.replay(bind)
    def test_tampered_document_bytes_break_replay_even_if_digest_column_unchanged(self):
        bind=self.store.accept(bundle(),now=100)
        self.store.db.execute('UPDATE policies SET document_json=? WHERE bundle_id=? AND version=? AND generation=?',('{"policy_id":"tampered"}',bind.bundle_id,bind.bundle_version,bind.bundle_generation)); self.store.db.commit()
        with self.assertRaises(ReplayError): self.store.replay(bind)
    def test_manifest_object_binding_is_rechecked_on_replay(self):
        bind=self.store.accept(bundle(),now=100)
        row=self.store.db.execute('SELECT manifest_json FROM bundles WHERE bundle_id=? AND version=? AND generation=?',(bind.bundle_id,bind.bundle_version,bind.bundle_generation)).fetchone()[0]
        import json,hashlib
        m=json.loads(row); m['policy_digest']='0'*64
        encoded=json.dumps(m,sort_keys=True,separators=(',',':'))
        d=hashlib.sha256(encoded.encode()).hexdigest()
        self.store.db.execute('UPDATE bundles SET manifest_json=?,digest=? WHERE bundle_id=? AND version=? AND generation=?',(encoded,d,bind.bundle_id,bind.bundle_version,bind.bundle_generation)); self.store.db.commit()
        with self.assertRaises(ReplayError): self.store.replay(bind)
    def test_authority_rotation_rejects_old_signer(self):
        self.store.accept(bundle(),now=100); self.store.rotate_authority(Authority(2,'root-2',KEY2))
        with self.assertRaises(AuthorityError): self.store.accept(bundle(2,2,p=policy(2,2),t=trust(2,2),authority_generation=1,key=KEY1,signer='root-1'),now=101)
        self.store.accept(bundle(2,2,p=policy(2,2),t=trust(2,2),authority_generation=2,key=KEY2,signer='root-2'),now=101)
    def test_gap_is_rejected(self):
        self.store.accept(bundle(),now=100)
        with self.assertRaises(RollbackError): self.store.accept(bundle(3,3,p=policy(3,3),t=trust(3,3)),now=101)
    def test_expired_or_future_bundle_rejected(self):
        with self.assertRaises(RollbackError): self.store.accept(bundle(),now=181)
        with self.assertRaises(RollbackError): self.store.accept(bundle(),now=94)
if __name__=='__main__': unittest.main()
