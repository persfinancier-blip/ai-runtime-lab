import tempfile,threading,unittest
from pathlib import Path
from experiments.authority_transition_races.protocol import *
def mk(kind,v,g,name):
 raw=[f"{kind}-{name}-{i}".encode() for i in range(3)];return A(kind,v,g,2,{kid(k):k.hex() for k in raw}),raw
def ss(raw,p):return tuple(Sig(kid(k),sign(k,p)) for k in raw[:2])
class T(unittest.TestCase):
 def setUp(self):self.r,self.rk=mk("root",1,1,"r");self.c,self.ck=mk("recovery",1,1,"c")
 def rot(self,pid,name="n",v=2):
  n,nk=mk("recovery",v,2,name);z=rotp(self.r,self.c,n);return P(pid,"rot",self.r.id,self.c.id,n,ss(self.ck,z),ss(nk,z),ss(self.rk,z))
 def rec(self,pid,name="n"):
  n,nk=mk("root",2,2,name);z=recp(self.r,n,self.c);return P(pid,"rec",self.r.id,self.c.id,n,ss(self.ck,z))
 def race(self,s,a,b):
  gate=threading.Barrier(3);out=[]
  def f(p):
   gate.wait()
   try:out.append(("ok",s.commit(p)))
   except Exception as e:out.append((type(e).__name__,str(e)))
  x=threading.Thread(target=f,args=(a,));y=threading.Thread(target=f,args=(b,));x.start();y.start();gate.wait();x.join();y.join();return out
 def test_rot_vs_rec(self):
  with tempfile.TemporaryDirectory() as d:self.assertEqual(sum(x[0]=="ok" for x in self.race(Store(Path(d)/"x",self.r,self.c),self.rot("a"),self.rec("b"))),1)
 def test_two_rot(self):
  with tempfile.TemporaryDirectory() as d:self.assertEqual(sum(x[0]=="ok" for x in self.race(Store(Path(d)/"x",self.r,self.c),self.rot("a","a"),self.rot("b","b"))),1)
 def test_two_rec(self):
  with tempfile.TemporaryDirectory() as d:self.assertEqual(sum(x[0]=="ok" for x in self.race(Store(Path(d)/"x",self.r,self.c),self.rec("a","a"),self.rec("b","b"))),1)
 def test_stale_root(self):
  with tempfile.TemporaryDirectory() as d:
   s=Store(Path(d)/"x",self.r,self.c);s.commit(self.rec("win"))
   with self.assertRaises(Stale):s.commit(self.rot("stale"))
 def test_stale_recovery(self):
  with tempfile.TemporaryDirectory() as d:
   s=Store(Path(d)/"x",self.r,self.c);s.commit(self.rot("win"))
   with self.assertRaises(Stale):s.commit(self.rec("stale"))
 def test_unknown_reconcile(self):
  with tempfile.TemporaryDirectory() as d:
   s=Store(Path(d)/"x",self.r,self.c);p=self.rot("u")
   with self.assertRaises(Unknown):s.commit(p,True)
   self.assertEqual(s.reconcile(p)["seq"],1);self.assertEqual(s.commit(p)["seq"],1)
 def test_restart(self):
  with tempfile.TemporaryDirectory() as d:
   path=Path(d)/"x";s=Store(path,self.r,self.c);self.race(s,self.rot("a"),self.rec("b"));self.assertEqual(Store(path,self.r,self.c).head()[2],1)
 def test_rollback_substitution(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(E):Store(Path(d)/"x",self.r,self.c).commit(self.rot("bad",v=1))
 def test_proposal_substitution(self):
  with tempfile.TemporaryDirectory() as d:
   s=Store(Path(d)/"x",self.r,self.c);s.commit(self.rot("same"))
   with self.assertRaises(Conflict):s.reconcile(self.rec("same"))
 def test_evidence_pair(self):
  with tempfile.TemporaryDirectory() as d:
   e=Store(Path(d)/"x",self.r,self.c).commit(self.rot("e"));self.assertEqual((e["r0"],e["c0"]),(self.r.id,self.c.id))
 def test_unsafe_accepts_two(self):
  u=Unsafe(self.r.id,self.c.id);a=self.rot("a");b=self.rec("b");self.assertTrue(u.check(a));self.assertTrue(u.check(b));u.write(a,self.r.id,a.new.id);u.write(b,b.new.id,self.c.id);self.assertEqual(len(u.accepted),2)
if __name__=="__main__":unittest.main()
