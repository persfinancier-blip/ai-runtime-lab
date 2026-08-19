import unittest
from experiments.anchor_rotation_concurrency.protocol import Proposal,Root,UnsafeCheckThenWrite
class U(unittest.TestCase):
 def test_check_then_write_split_brain(self):
  old=Root('anchor-A',1,7,2,('o1','o2','o3'));a=Proposal('A','rotation',old.digest,1,7,Root('anchor-A',2,7,2,('a1','a2','a3')),('s1','s2'));b=Proposal('B','rotation',old.digest,1,7,Root('anchor-A',2,7,2,('b1','b2','b3')),('s1','s2'));u=UnsafeCheckThenWrite(old);u.validate(a);u.validate(b);u.write(a);u.write(b);self.assertEqual(len(u.activations),1,'unsafe check-then-write accepted two successors')
if __name__=='__main__':unittest.main()
