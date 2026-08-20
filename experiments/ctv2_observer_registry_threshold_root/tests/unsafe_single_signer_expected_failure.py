import unittest
from experiments.ctv2_observer_registry_threshold_root.protocol import *
class Unsafe(unittest.TestCase):
    def test_one_asserted_key_should_not_rewrite_registry_but_does(self):
        attacker=b"attacker"; root=RootState("registry-A",99,99,1,{key_id(attacker):attacker.hex()})
        u={"registry_id":"registry-A","version":1,"generation":1,"threshold":1,
           "observers":{"evil":{"observer_id":"evil","generation":1,"status":"ACTIVE","key_hex":attacker.hex()}},
           "previous_digest":None,"root_version":root.version,"authority_epoch":root.authority_epoch,"root_id":root.root_id}
        s=RegistrySnapshot(**u,signatures=(Signature(key_id(attacker),sign(attacker,u)),))
        self.assertFalse(UnsafeSingleSignerRootSwap().accept_snapshot(s,attacker),"single self-asserted key rewrote observer registry")
if __name__=="__main__": unittest.main()
