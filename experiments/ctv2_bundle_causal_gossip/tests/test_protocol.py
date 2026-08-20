import tempfile,unittest
from pathlib import Path
from experiments.ctv2_bundle_causal_gossip.protocol import *
class T(unittest.TestCase):
 def setUp(self):
  self.pk=b"p";self.ok={"a":b"a","b":b"b"};self.new=View.issue("p",("1","2","3"),self.pk);self.old=View.issue("p",("1","2"),self.pk)
 def t(self,s=None):return Tracker({"p":self.pk},self.ok,s)
 def add(self,t,w,v,tm=0):return t.accept(t.issue(w,v,tm))
 def test_new_old(self):t=self.t();self.add(t,"a",self.new,999);self.assertEqual(self.add(t,"a",self.old,-999),"LOCAL_FREEZE_SUSPECTED")
 def test_old_new(self):t=self.t();self.add(t,"a",self.old,999);self.assertEqual(self.add(t,"a",self.new,-999),"CURRENT")
 def test_cross_observer_clock_cannot_frame(self):t=self.t();self.add(t,"a",self.new,-999);self.assertEqual(self.add(t,"b",self.old,999),"CURRENT")
 def test_replay(self):t=self.t();o=t.issue("a",self.new);t.accept(o);self.assertEqual(t.accept(o),"DUPLICATE_IGNORED")
 def test_equiv(self):
  t=self.t();o=t.issue("a",self.new);t.accept(o);a=t.issue("a",self.old);t.accept(a);v=View.issue("p",("1","x"),self.pk);u={"observer":"a","seq":2,"pred":o.id,"peer":"p","view_id":v.id,"events":list(v.events),"peer_signature":v.signature,"claimed_time":0};b=Obs("a",2,o.id,"p",v.id,v.events,v.signature,0,sig(b"a",u))
  with self.assertRaises(Equiv):t.accept(b)
 def test_quorum(self):t=self.t();self.add(t,"a",self.new);self.add(t,"a",self.old);self.add(t,"b",self.new);self.assertEqual(self.add(t,"b",self.old),"CORROBORATED_FREEZE")
 def test_dup_no_quorum(self):t=self.t();self.add(t,"a",self.new);o=t.issue("a",self.old);t.accept(o);[t.accept(o) for _ in range(3)];self.assertEqual(t.classify("p"),"LOCAL_FREEZE_SUSPECTED")
 def test_partition(self):self.assertEqual(self.t().missing("p"),"UNKNOWN_PARTITIONED")
 def test_restart(self):
  with tempfile.TemporaryDirectory() as d:
   s=Store(Path(d)/"s");t=self.t(s);self.add(t,"a",self.new);self.add(t,"a",self.old);self.assertEqual(self.t(s).classify("p"),"LOCAL_FREEZE_SUSPECTED")
 def test_head_tamper(self):
  with tempfile.TemporaryDirectory() as d:
   s=Store(Path(d)/"s");t=self.t(s);self.add(t,"a",self.new);x=s.load();x["heads"]["a"]["seq"]=9;s.save(x)
   with self.assertRaises(Auth):self.t(s)
 def test_split(self):t=self.t();self.add(t,"a",self.new);v=View.issue("p",("1","x"),self.pk);self.assertEqual(self.add(t,"b",v),"SPLIT_VIEW")
 def test_fabricated_observer_content_without_peer_signature_rejected(self):
  t=self.t();first=t.issue("a",self.new);t.accept(first);fake_events=("1","2");fake_peer_sig="00"*32;fake_view=View("p",fake_events,fake_peer_sig);u={"observer":"a","seq":2,"pred":first.id,"peer":"p","view_id":fake_view.id,"events":list(fake_events),"peer_signature":fake_peer_sig,"claimed_time":0};o=Obs("a",2,first.id,"p",fake_view.id,fake_events,fake_peer_sig,0,sig(b"a",u))
  with self.assertRaises(Auth):t.accept(o)
 def test_view_id_substitution_rejected(self):
  t=self.t();o=t.issue("a",self.new);u=o.unsigned.copy();u["view_id"]=self.old.id;forged=Obs(o.observer,o.seq,o.pred,o.peer,self.old.id,o.events,o.peer_signature,o.claimed_time,sig(b"a",u))
  with self.assertRaises(Auth):t.accept(forged)
if __name__=="__main__":unittest.main()
