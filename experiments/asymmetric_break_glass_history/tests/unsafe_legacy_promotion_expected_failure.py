import unittest
from experiments.asymmetric_break_glass_history.protocol import UnsafeLegacyAutoPromotion
class Unsafe(unittest.TestCase):
    def test_legacy_hmac_should_not_become_asymmetric_authority_but_does(self):
        self.assertFalse(UnsafeLegacyAutoPromotion().promote(4,'legacy-hmac'))
if __name__=='__main__': unittest.main()
