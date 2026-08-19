import unittest
from experiments.anchor_attestation.protocol import UnsafeUnauthenticatedRead
class Unsafe(unittest.TestCase):
    def test_spoofed_read_is_accepted(self):
        self.assertFalse(UnsafeUnauthenticatedRead().allow(7,7), "unsafe unauthenticated claimed position was accepted")
if __name__=="__main__": unittest.main()
