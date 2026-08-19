import unittest
from experiments.ctv2_consistency_wire.protocol import *
from experiments.ctv2_consistency_wire.tests.test_protocol import LOG, H, N1

class UnsafeSeed(unittest.TestCase):
    def test_trailing_bytes_should_be_rejected_but_prefix_parser_accepts(self):
        wire = encode_consistency_proof(ConsistencyProofV2(LOG, 3, 7, (N1,)))
        parsed = unsafe_decode_prefix_only(wire + b"attacker-controlled", hash_size=H)
        self.assertIsNone(parsed, "unsafe parser accepted trailing ambiguous bytes")

if __name__ == "__main__":
    unittest.main()
