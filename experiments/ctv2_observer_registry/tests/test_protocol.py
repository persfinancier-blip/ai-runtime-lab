import tempfile,unittest
from pathlib import Path
from experiments.ctv2_observer_registry.protocol import *
def obs(i,k,status="ACTIVE",generation=1): return {"observer_id":i,"key_hex":k.hex(),"status":status,"generation":generation}
class T(unittest.TestCase):
 def setUp(self):
  self.rk=b"root"; self.k1=b"k1"; self.k2=b"k2"; self.o1=obs("o1",self.k1); self.o2=obs("o2",self.k2)
  self.s1=RegistrySnapshot.issue(registry_id="R",version=1,generation=1,threshold=2,observers={"o1":self.o1,"o2":self.o2},previous_digest=None,root_key=self.rk)
 def reg(self,store=None):
  r=ObserverRegistry(self.rk,store)
  if r.current_id is None:r.accept(self.s1)
  return r
 def ev(self,i,k,s,g=1): return ObserverEvidence.issue(observer_id=i,observer_generation=g,registry_snapshot_id=s.snapshot_id,payload_digest="P",key=k)
 def test_bootstrap_quorum(self): self.assertTrue(self.reg().quorum([self.ev("o1",self.k1,self.s1),self.ev("o2",self.k2,self.s1)],"P"))
 def test_sybil(self): self.assertFalse(self.reg().quorum([self.ev("o1",self.k1,self.s1),self.ev("x",b"x",self.s1)],"P"))
 def test_duplicate(self):
  e=self.ev("o1",self.k1,self.s1); self.assertFalse(self.reg().quorum([e,e,e],"P"))
 def test_rotation(self):
  nk=b"n"; s2=RegistrySnapshot.issue(registry_id="R",version=2,generation=2,threshold=2,observers={"o1":obs("o1",nk,generation=2),"o2":self.o2},previous_digest=self.s1.snapshot_id,root_key=self.rk); r=self.reg(); r.accept(s2)
  self.assertFalse(r.quorum([self.ev("o1",self.k1,self.s1),self.ev("o2",self.k2,self.s1)],"P")); self.assertTrue(r.quorum([self.ev("o1",nk,s2,2),self.ev("o2",self.k2,s2)],"P"))
 def test_revocation(self):
  s2=RegistrySnapshot.issue(registry_id="R",version=2,generation=2,threshold=1,observers={"o1":obs("o1",self.k1,"REVOKED"),"o2":self.o2},previous_digest=self.s1.snapshot_id,root_key=self.rk); r=self.reg(); r.accept(s2); self.assertFalse(r.quorum([self.ev("o1",self.k1,s2)],"P"))
 def test_rollback(self):
  with self.assertRaises(RollbackError): self.reg().accept(self.s1)
 def test_wrong_predecessor(self):
  s2=RegistrySnapshot.issue(registry_id="R",version=2,generation=2,threshold=2,observers={"o1":self.o1,"o2":self.o2},previous_digest="bad",root_key=self.rk)
  with self.assertRaises(TamperError): self.reg().accept(s2)
 def test_historical_replay(self):
  r=self.reg(); old=[self.ev("o1",self.k1,self.s1),self.ev("o2",self.k2,self.s1)]; s2=RegistrySnapshot.issue(registry_id="R",version=2,generation=2,threshold=1,observers={"o1":obs("o1",self.k1,"REVOKED"),"o2":self.o2},previous_digest=self.s1.snapshot_id,root_key=self.rk); r.accept(s2); self.assertTrue(r.quorum(old,"P",snapshot_id=self.s1.snapshot_id,historical=True))
 def test_restart(self):
  with tempfile.TemporaryDirectory() as td:
   st=RegistryStore(Path(td)/"s"); self.reg(st); self.assertEqual(ObserverRegistry(self.rk,st).current().snapshot_id,self.s1.snapshot_id)
 def test_tamper(self):
  with tempfile.TemporaryDirectory() as td:
   st=RegistryStore(Path(td)/"s"); self.reg(st); x=st.load(); x["history"][self.s1.snapshot_id]["threshold"]=1; st.save(x)
   with self.assertRaises((AuthError,TamperError)): ObserverRegistry(self.rk,st)
 def test_before_after_transition(self):
  r=self.reg(); old=self.ev("o1",self.k1,self.s1); nk=b"n"; s2=RegistrySnapshot.issue(registry_id="R",version=2,generation=2,threshold=2,observers={"o1":obs("o1",nk,generation=2),"o2":self.o2},previous_digest=self.s1.snapshot_id,root_key=self.rk); r.accept(s2); self.assertFalse(r.quorum([old,self.ev("o2",self.k2,s2)],"P"))
if __name__=="__main__":unittest.main()
