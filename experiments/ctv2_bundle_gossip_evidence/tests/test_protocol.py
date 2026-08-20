import tempfile,unittest
from pathlib import Path
from experiments.ctv2_bundle_gossip_evidence.protocol import AuthenticationError,ClockRollback,GossipStore,GossipTracker,SignedView
class Tests(unittest.TestCase):
 def setUp(self):
  self.pk=b'peer'; self.pks={'peer-A':self.pk}; self.oks={'obs-A':b'a','obs-B':b'b'}; self.td=tempfile.TemporaryDirectory(); self.store=GossipStore(Path(self.td.name)/'s.json')
 def tearDown(self): self.td.cleanup()
 def t(self): return GossipTracker(peer_keys=self.pks,observer_keys=self.oks,store=self.store,max_silence=10)
 def v(self,*e): return SignedView.issue(peer_id='peer-A',event_ids=tuple(e),key=self.pk)
 def test_current(self):
  t=self.t(); self.assertEqual(t.observe(observer_id='obs-A',view=self.v('e1','e2'),now=10),'CURRENT')
 def test_missing_unknown(self): self.assertEqual(self.t().missing_exchange(peer_id='peer-A',observer_id='obs-A',now=10),'UNKNOWN_PARTITIONED')
 def test_silence_expires_unknown(self):
  t=self.t(); t.observe(observer_id='obs-A',view=self.v('e1'),now=10); self.assertEqual(t.classify(peer_id='peer-A',observer_id='obs-A',now=21),'UNKNOWN_PARTITIONED')
 def test_freeze_requires_newer_prior_independent(self):
  t=self.t(); t.observe(observer_id='obs-B',view=self.v('e1','e2','e3'),now=20); self.assertEqual(t.observe(observer_id='obs-A',view=self.v('e1','e2'),now=25),'FREEZE_SUSPECTED')
 def test_old_before_new_not_freeze(self):
  t=self.t(); t.observe(observer_id='obs-A',view=self.v('e1'),now=10); t.observe(observer_id='obs-B',view=self.v('e1','e2'),now=20); self.assertNotIn('FREEZE_SUSPECTED',t.historical_incidents('peer-A'))
 def test_split(self):
  t=self.t(); t.observe(observer_id='obs-A',view=self.v('e1','l'),now=10); self.assertEqual(t.observe(observer_id='obs-B',view=self.v('e1','r'),now=11),'SPLIT_VIEW')
 def test_duplicate_no_refresh(self):
  t=self.t(); v=self.v('e1'); t.observe(observer_id='obs-A',view=v,now=10); self.assertEqual(t.observe(observer_id='obs-A',view=v,now=19),'DUPLICATE_IGNORED'); self.assertEqual(t.classify(peer_id='peer-A',observer_id='obs-A',now=21),'UNKNOWN_PARTITIONED')
 def test_restart(self):
  t=self.t(); t.observe(observer_id='obs-B',view=self.v('e1','e2'),now=10); t.observe(observer_id='obs-A',view=self.v('e1'),now=11); r=self.t(); r.verify_persisted_observations(); self.assertEqual(r.classify(peer_id='peer-A',observer_id='obs-A',now=12),'FREEZE_SUSPECTED')
 def test_clock_rollback(self):
  t=self.t(); t.missing_exchange(peer_id='peer-A',observer_id='obs-A',now=20); self.assertRaises(ClockRollback,t.classify,peer_id='peer-A',observer_id='obs-A',now=19)
 def test_selective_freeze(self):
  t=self.t(); t.observe(observer_id='obs-B',view=self.v('e1','e2','e3'),now=30); t.observe(observer_id='obs-A',view=self.v('e1'),now=31); self.assertEqual(t.classify(peer_id='peer-A',observer_id='obs-A',now=31),'FREEZE_SUSPECTED')
 def test_expiry_keeps_incident(self):
  t=self.t(); t.observe(observer_id='obs-B',view=self.v('e1','e2'),now=10); t.observe(observer_id='obs-A',view=self.v('e1'),now=11); self.assertEqual(t.classify(peer_id='peer-A',observer_id='obs-A',now=100),'FREEZE_SUSPECTED')
 def test_forged_persisted_incident_is_not_trusted(self):
  t=self.t(); t.observe(observer_id='obs-A',view=self.v('e1'),now=10)
  raw=self.store.load(); raw['incidents']=[{'incident_id':'fake','kind':'SPLIT_VIEW','peer_id':'peer-A'}]; self.store.save(raw)
  restarted=self.t(); self.assertEqual(restarted.classify(peer_id='peer-A',observer_id='obs-A',now=11),'CURRENT')
 def test_tamper(self):
  t=self.t(); t.observe(observer_id='obs-A',view=self.v('e1'),now=10); raw=self.store.load(); raw['observations'][0]['event_ids']=['x']; self.store.save(raw); self.assertRaises(AuthenticationError,self.t().verify_persisted_observations)
if __name__=='__main__': unittest.main()
