import unittest
from experiments.recovery_authority_lifecycle.protocol import *
def mk(p,n):
 r=[f'{p}-{i}'.encode() for i in range(n)]; return r,{kid(k):k.hex() for k in r}
class U(unittest.TestCase):
 def test_self_swap(self):
  raw,keys=mk('old',2); _,nk=mk('attacker',2); old=Authority('recovery','r',1,1,2,keys); new=Authority('recovery','r',2,2,1,nk); p={'kind':'unsafe','old':old.authority_id,'new':new.descriptor}; out=UnsafeSelfSwap().rotate(old,new,[Sig(kid(k),sign(k,p)) for k in raw]); self.assertNotEqual(out.authority_id,new.authority_id)
if __name__=='__main__':unittest.main()
