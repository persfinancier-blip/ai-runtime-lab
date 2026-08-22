import json, tempfile, unittest
from pathlib import Path
from experiments.sink_registry_migration_checkpoint.protocol import *

def keys(n=3):
    raw=[f'k{i}'.encode() for i in range(n)]; return raw,{key_id(k):k.hex() for k in raw}

class Tests(unittest.TestCase):
    def setUp(self): self.raw,self.keys=keys()
    def store(self,td):
        s=MigrationStore(Path(td)/'db'); q=s._con()
        rid=sha({'version':1,'epoch':1,'threshold':2,'keys':dict(sorted(self.keys.items())),'revoked':[]}); self.rid=rid; q.execute("INSERT INTO registry_authority_head VALUES(1,?,?,?,?,?,?)",(rid,1,1,2,json.dumps(self.keys),json.dumps([])))
        q.execute("INSERT INTO broker_meta VALUES(1,1)")
        entry=('d'*64,'sink-A',1,'a'*64,'https://sink.example','charge',None,key_id(self.raw[0]),1,'s'*64)
        q.execute("INSERT INTO sink_registry_entries VALUES(?,?,?,?,?,?,?,?,?,?)",entry)
        ejson=json.dumps({'legacy':'exact-row'},sort_keys=True,separators=(',',':'))
        q.execute("INSERT INTO registry_authorized_entries VALUES(?,?,?,?)",(entry[0],ejson,self.rid,1))
        q.execute("INSERT INTO sink_registry_heads VALUES(?,?,?)",('sink-A',entry[0],1))
        q.execute("INSERT INTO sink_capability_heads VALUES(?,?,?,?,?)",('sink-A',1,'c'*64,1,'probe'))
        q.execute("INSERT INTO broker_requests VALUES(?,?,?,?)",('done','r'*64,'CONFIRMED','receipt'))
        q.commit();q.close();return s
    def proof(self,cp,count=2): return MigrationProof(cp.checkpoint_id,self.rid,1,tuple(sign_checkpoint(cp,k) for k in self.raw[:count]))
    def test_threshold_checkpoint_migrates_without_promoting_legacy_rows(self):
        with tempfile.TemporaryDirectory() as td:
            s=self.store(td);cp=s.preview(cutoff_sequence=7);s.migrate(cp,self.proof(cp));self.assertTrue(s.verify());q=s._con();self.assertEqual(q.execute('SELECT COUNT(*) FROM registry_threshold_publications').fetchone()[0],0);q.close()
    def test_one_signer_cannot_migrate(self):
        with tempfile.TemporaryDirectory() as td:
            s=self.store(td);cp=s.preview(cutoff_sequence=7);self.assertRaises(MigrationThresholdError,s.migrate,cp,self.proof(cp,1))
    def test_pending_intent_blocks_migration(self):
        with tempfile.TemporaryDirectory() as td:
            s=self.store(td);q=s._con();q.execute("INSERT INTO broker_requests VALUES(?,?,?,?)",('pending','p'*64,'INTENT',None));q.commit();q.close();self.assertRaises(MigrationPendingEffects,s.preview,cutoff_sequence=7)
    def test_pending_unknown_blocks_migration(self):
        with tempfile.TemporaryDirectory() as td:
            s=self.store(td);q=s._con();q.execute("INSERT INTO broker_requests VALUES(?,?,?,?)",('u','u'*64,'UNKNOWN',None));q.commit();q.close();self.assertRaises(MigrationPendingEffects,s.preview,cutoff_sequence=7)
    def test_confirmed_is_allowed_and_count_bound(self):
        with tempfile.TemporaryDirectory() as td:
            s=self.store(td);cp=s.preview(cutoff_sequence=7);self.assertEqual(len(cp.confirmed_requests_digest),64)
    def test_legacy_omission_after_checkpoint_detected(self):
        with tempfile.TemporaryDirectory() as td:
            s=self.store(td);cp=s.preview(cutoff_sequence=7);s.migrate(cp,self.proof(cp));q=s._con();q.execute('DELETE FROM registry_authorized_entries');q.commit();q.close();self.assertRaises(MigrationSubstitution,s.verify)
    def test_registry_head_substitution_before_commit_detected(self):
        with tempfile.TemporaryDirectory() as td:
            s=self.store(td);cp=s.preview(cutoff_sequence=7);q=s._con();q.execute("UPDATE sink_registry_heads SET generation=2");q.commit();q.close();self.assertRaises(MigrationSubstitution,s.migrate,cp,self.proof(cp))
    def test_authority_rotation_before_commit_detected(self):
        with tempfile.TemporaryDirectory() as td:
            s=self.store(td);cp=s.preview(cutoff_sequence=7);q=s._con();q.execute("UPDATE registry_authority_head SET version=2");q.commit();q.close();self.assertRaises(MigrationSubstitution,s.migrate,cp,self.proof(cp))
    def test_same_slot_substitution_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            s=self.store(td);cp=s.preview(cutoff_sequence=7);s.migrate(cp,self.proof(cp));changed=MigrationCheckpoint(**{**cp.canonical,'cutoff_sequence':8});self.assertRaises(MigrationSubstitution,s.migrate,changed,self.proof(changed))
    def test_unsafe_auto_promotion_creates_fake_threshold_rows(self):
        with tempfile.TemporaryDirectory() as td:
            s=self.store(td);q=s._con();self.assertEqual(UnsafeAutoPromotion.promote(q),1);q.commit();self.assertEqual(q.execute('SELECT COUNT(*) FROM registry_threshold_publications').fetchone()[0],1);q.close()
if __name__=='__main__': unittest.main()
