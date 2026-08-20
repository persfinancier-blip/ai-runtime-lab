import unittest
from experiments.ctv2_bundle_authority_lifecycle.protocol import UnsafeAuthoritySwap,kid
class Unsafe(unittest.TestCase):
    def test_self_authorized_swap_should_not_work_but_does(self):
        a=UnsafeAuthoritySwap('good',b'good'); evil=b'evil'; a.rotate_authority(kid(evil),evil)
        self.assertNotEqual(a.signer_id,kid(evil),'unsafe caller replaced authority without root proof')
if __name__=='__main__': unittest.main()
