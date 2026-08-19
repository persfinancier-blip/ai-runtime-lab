import unittest
from experiments.anchor_threshold_root.protocol import *
class U(unittest.TestCase):
    def test_self_asserted_single_key_should_not_recover_but_does(self):
        attacker=b'attacker-controlled'; state=RootState('anchor-A',2,8,1,{key_id(attacker):attacker.hex()}); p={'new_root':root_descriptor(state)}
        accepted=UnsafeSingleSignerRecovery().recover(state,attacker,sign(attacker,p)); self.assertFalse(accepted,'unsafe self-authorized one-signer recovery was accepted')
if __name__=='__main__': unittest.main()
