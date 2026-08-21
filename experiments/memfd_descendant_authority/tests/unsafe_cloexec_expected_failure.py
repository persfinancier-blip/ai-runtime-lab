import unittest
from experiments.memfd_descendant_authority.protocol import unsafe_propagation

class Unsafe(unittest.TestCase):
    def test_cloexec_should_prevent_grandchild_but_does_not(self):
        self.assertFalse(unsafe_propagation(b'unsafe-secret'))

if __name__=='__main__':
    unittest.main()
