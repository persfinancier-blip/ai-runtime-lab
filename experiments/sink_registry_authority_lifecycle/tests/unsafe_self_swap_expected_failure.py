import unittest
from experiments.sink_registry_authority_lifecycle.protocol import UnsafeAmbientAuthority

class Unsafe(unittest.TestCase):
    def test_caller_should_not_replace_root_but_can(self):
        self.assertFalse(UnsafeAmbientAuthority(b'old').replace(b'attacker'))

if __name__=='__main__': unittest.main()
