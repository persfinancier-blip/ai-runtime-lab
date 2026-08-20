import unittest
from experiments.authority_transition_races.tests.test_protocol import T
from experiments.authority_transition_races.protocol import Unsafe
class U(T):
 def test_expected_failure(self):
  u=Unsafe(self.r.id,self.c.id);a=self.rot("a");b=self.rec("b");self.assertTrue(u.check(a));self.assertTrue(u.check(b));u.write(a,self.r.id,a.new.id);u.write(b,b.new.id,self.c.id);self.assertLessEqual(len(u.accepted),1)
if __name__=="__main__":unittest.main()
