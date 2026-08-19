import json, unittest
from experiments.secret_observability.protocol import SecretBoundary, CredentialMeta, UnsafeRecorder, REDACTED

AUTH='bearer-lowentropy-secret'
COOKIE='sid=session-secret-42'
PROXY='Basic cHJveHk6c2VjcmV0'
REFRESH='refresh-secret-abc'

class Tests(unittest.TestCase):
 def setUp(self):
  self.b=SecretBoundary(b'audit-key-not-exported')
  self.ids={s:self.b.register_secret(s) for s in [AUTH,COOKIE,PROXY,REFRESH]}
  self.meta=CredentialMeta('origin-auth','api.example','cred-origin',7)
 def assert_no_secret(self,x):
  s=json.dumps(x,sort_keys=True)
  for sec in [AUTH,COOKIE,PROXY,REFRESH]: self.assertNotIn(sec,s)
 def test_authorization_redacted_all_channels(self):
  for ch in ['log','trace','evidence','replay']:
   r=self.b.emit(ch,'request',{'headers':{'Authorization':AUTH}},self.meta); self.assert_no_secret(r)
 def test_cookie_scope_auditable_value_hidden(self):
  r=self.b.emit('evidence','cookie',{'headers':{'Cookie':COOKIE},'host':'api.example','path':'/v1'},self.meta)
  self.assertEqual(r['payload']['headers']['Cookie'],REDACTED); self.assertEqual(r['payload']['host'],'api.example')
 def test_proxy_auth_separate(self):
  m=CredentialMeta('proxy-auth','proxy.example:8080','cred-proxy',2)
  r=self.b.emit('trace','proxy',{'headers':{'Proxy-Authorization':PROXY,'Authorization':AUTH}},m)
  self.assert_no_secret(r); self.assertEqual(r['credential']['kind'],'proxy-auth')
 def test_exception_sanitized(self):
  r=self.b.emit('log','error',RuntimeError('failed token '+AUTH+' cookie '+COOKIE)); self.assert_no_secret(r)
 def test_nested_and_case_variants(self):
  p={'Outer':[{'aUtHoRiZaTiOn':AUTH},{'nested':{'REFRESH_TOKEN':REFRESH}}]}; r=self.b.emit('replay','snap',p); self.assert_no_secret(r)
 def test_hmac_identity_not_raw_sha(self):
  ident=self.ids[AUTH]; self.assertNotEqual(ident,__import__('hashlib').sha256(AUTH.encode()).hexdigest()); self.assertEqual(len(ident),64)
 def test_rotation_preserves_public_id_changes_generation(self):
  a=CredentialMeta('origin-auth','api.example','cred-origin',7); b=CredentialMeta('origin-auth','api.example','cred-origin',8)
  self.assertEqual(a.credential_id,b.credential_id); self.assertNotEqual(a.generation,b.generation)
 def test_unknown_retry_evidence_no_secret(self):
  p={'effect_id':'eff-1','route_id':'route-9','outcome':'UNKNOWN','Authorization':AUTH}; r=self.b.emit('evidence','retry',p,self.meta); self.assert_no_secret(r); self.assertEqual(r['payload']['effect_id'],'eff-1')
 def test_serialization_second_boundary(self):
  raw={'message':'Bearer '+AUTH,'nested':{'cookie':COOKIE}}; s=self.b.serialize(raw); self.assert_no_secret(s)
 def test_key_names_case_and_punctuation(self):
  r=self.b.emit('log','x',{'API_KEY':'abc','access_token':'xyz','Password':'pw'}); self.assertEqual(r['payload']['API_KEY'],REDACTED)
 def test_unregistered_bearer_pattern_redacted(self):
  r=self.b.emit('log','x',{'message':'Authorization failed: Bearer abc.DEF-123'}); self.assertNotIn('abc.DEF-123',json.dumps(r))
 def test_nonsecret_preserved(self):
  r=self.b.emit('trace','x',{'method':'GET','status':401,'route':'proxy-A'}); self.assertEqual(r['payload']['method'],'GET')
 def test_unsafe_baseline_leaks(self):
  s=UnsafeRecorder().serialize({'headers':{'Authorization':AUTH},'error':'token='+AUTH}); self.assertIn(AUTH,s)

if __name__=='__main__': unittest.main()
