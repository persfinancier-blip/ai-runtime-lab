import json,unittest
from dataclasses import replace
from experiments.launch_record_integrity.protocol import *
KEY=b'K'*32
def base(): return LaunchRecord('task-A',123,456,123,7,8,9,4,10,'nonce-10')
def verify(raw,guard=None,ring=None,task='task-A',gens=(7,8,9)):
    return verify_record(raw,expected_task=task,expected_generations=gens,keyring=ring or Keyring('k2',{'k2':KEY},4),replay_guard=guard or ReplayGuard({}))
class Tests(unittest.TestCase):
    def test_valid(self): self.assertEqual(verify(sign_record(base(),key_id='k2',key=KEY)).pid,123)
    def test_tamper(self):
        signed=sign_record(base(),key_id='k2',key=KEY)
        for f,v in {'pid':124,'starttime':457,'task_id':'task-X','sandbox_generation':70,'process_group':999}.items():
            env=json.loads(signed); env['payload']['record'][f]=v
            with self.subTest(f=f),self.assertRaises(AuthError): verify(json.dumps(env))
    def test_cross_task(self):
        with self.assertRaises(DomainError): verify(sign_record(base(),key_id='k2',key=KEY),task='task-B')
    def test_rollback(self):
        g=ReplayGuard({'task-A':10}); verify(sign_record(base(),key_id='k2',key=KEY),guard=g)
        with self.assertRaises(ReplayError): verify(sign_record(replace(base(),record_seq=9,launch_nonce='old'),key_id='k2',key=KEY),guard=g)
    def test_key_rotation(self):
        with self.assertRaises(KeyErrorRecord): verify(sign_record(base(),key_id='k1',key=b'1'*32),ring=Keyring('k2',{'k1':b'1'*32,'k2':KEY},4))
    def test_authority_rotation(self):
        with self.assertRaises(DomainError): verify(sign_record(replace(base(),authority_epoch=3),key_id='k2',key=KEY))
    def test_reformat(self):
        e=json.loads(sign_record(base(),key_id='k2',key=KEY)); self.assertEqual(verify(json.dumps({'mac':e['mac'],'payload':e['payload']},indent=4)).record_seq,10)
    def test_duplicate_key(self):
        with self.assertRaises(ParseError): verify('{"payload":{},"payload":{},"mac":"x"}')
    def test_corrupt(self):
        with self.assertRaises(ParseError): verify('{"payload":')
    def test_generation_drift(self):
        with self.assertRaises(DomainError): verify(sign_record(base(),key_id='k2',key=KEY),gens=(7,99,9))
    def test_metadata_type_confusion_rejected(self):
        raw=sign_record(base(),key_id='k2',key=KEY)
        for field,value in [('schema_version',True),('alg',7),('key_id',['k2']),('record','not-an-object')]:
            bad=json.loads(raw); bad['payload'][field]=value
            with self.subTest(field=field),self.assertRaises((ParseError,AuthError)): verify(json.dumps(bad))
    def test_no_key_evidence(self):
        ev=evidence_summary(sign_record(base(),key_id='k2',key=KEY)); s=json.dumps(ev); self.assertNotIn(KEY.hex(),s); self.assertNotIn('KKKK',s)
    def test_unsigned_is_unsafe(self): self.assertTrue(unsafe_accept_unsigned(json.dumps({'task_id':'task-A','pid':999999}),'task-A'))
