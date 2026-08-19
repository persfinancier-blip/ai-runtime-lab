import struct
import unittest

from experiments.ctv2_consistency_wire.protocol import *

H = 32
LOG = bytes.fromhex("2b65705000")  # DER OID value bytes, arbitrary valid-length fixture
N1 = bytes(range(32))
N2 = bytes(range(32, 64))


class WireTests(unittest.TestCase):
    def item(self):
        return ConsistencyProofV2(LOG, 3, 7, (N1, N2))

    def wire(self):
        return encode_consistency_proof(self.item())

    def test_round_trip(self):
        self.assertEqual(decode_consistency_proof(self.wire(), hash_size=H), self.item())

    def test_independent_literal_fixture(self):
        # Independent TLS 1.3 presentation-language construction:
        # uint16 type; opaque LogID<2..127>; uint64 x2; vector<0..65535>;
        # each NodeHash is opaque<32..255>.
        path = bytes([32]) + N1 + bytes([32]) + N2
        fixture = (
            bytes([1, 5]) + bytes([len(LOG)]) + LOG
            + struct.pack("!Q", 3) + struct.pack("!Q", 7)
            + struct.pack("!H", len(path)) + path
        )
        self.assertEqual(self.wire(), fixture)

    def test_wrong_type(self):
        with self.assertRaises(WrongType):
            decode_consistency_proof(b"\x01\x06" + self.wire()[2:], hash_size=H)

    def test_truncation(self):
        for cut in (1, 2, 5, len(self.wire()) - 1):
            with self.assertRaises(WireError):
                decode_consistency_proof(self.wire()[:cut], hash_size=H)

    def test_trailing_bytes(self):
        with self.assertRaises(TrailingData):
            decode_consistency_proof(self.wire() + b"junk", hash_size=H)

    def test_node_hash_length_must_match_profile(self):
        wire = bytearray(self.wire())
        node_len_pos = 2 + 1 + len(LOG) + 8 + 8 + 2
        wire[node_len_pos] = 31
        with self.assertRaises(WireError):
            decode_consistency_proof(bytes(wire), hash_size=H)

    def test_vector_boundary_enforced(self):
        wire = bytearray(self.wire())
        vec_len_pos = 2 + 1 + len(LOG) + 8 + 8
        wire[vec_len_pos:vec_len_pos+2] = struct.pack("!H", 1)
        with self.assertRaises(WireError):
            decode_consistency_proof(bytes(wire), hash_size=H)

    def test_noncanonical_or_unterminated_oid_rejected(self):
        for bad in (bytes([0x2b, 0x80, 0x01]), bytes([0x2b, 0x81])):
            with self.assertRaises(MalformedVector):
                encode_consistency_proof(ConsistencyProofV2(bad, 3, 7, (N1,)))

    def test_log_id_bounds(self):
        with self.assertRaises(MalformedVector):
            encode_consistency_proof(ConsistencyProofV2(b"x", 3, 7, (N1,)))
        with self.assertRaises(MalformedVector):
            encode_consistency_proof(ConsistencyProofV2(b"x"*128, 3, 7, (N1,)))

    def test_vector_max_bound(self):
        with self.assertRaises(MalformedVector):
            encode_consistency_proof(ConsistencyProofV2(LOG, 3, 7, (N1,)*1986))

    def test_checkpoint_binding_before_merkle(self):
        calls = []
        def verifier(*args):
            calls.append(args); return True
        old = WitnessCheckpoint(LOG, 3, b"a"*32)
        new = WitnessCheckpoint(LOG, 7, b"b"*32)
        self.assertTrue(verify_bound_growth(self.wire(), old, new, hash_size=H, merkle_verifier=verifier))
        self.assertEqual(len(calls), 1)
        with self.assertRaises(BindingError):
            verify_bound_growth(self.wire(), WitnessCheckpoint(b"other",3,b"a"*32), new, hash_size=H, merkle_verifier=verifier)
        self.assertEqual(len(calls), 1)

    def test_swapped_sizes_rejected_before_merkle(self):
        calls=[]
        def verifier(*args): calls.append(args); return True
        old = WitnessCheckpoint(LOG, 7, b"a"*32)
        new = WitnessCheckpoint(LOG, 3, b"b"*32)
        with self.assertRaises(BindingError):
            verify_bound_growth(self.wire(), old, new, hash_size=H, merkle_verifier=verifier)
        self.assertFalse(calls)

    def test_uint64_and_bool_rejected_by_encoder(self):
        with self.assertRaises(WireError):
            encode_consistency_proof(ConsistencyProofV2(LOG, True, 7, (N1,)))
        with self.assertRaises(WireError):
            encode_consistency_proof(ConsistencyProofV2(LOG, 3, 1<<64, (N1,)))


if __name__ == "__main__":
    unittest.main()
