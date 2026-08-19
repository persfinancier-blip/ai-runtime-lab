import hashlib
import unittest

from experiments.rfc9162_consistency.protocol import (
    Checkpoint,
    MalformedProof,
    RootMismatch,
    SizeError,
    consistency_proof,
    leaf_hash,
    merkle_tree_hash,
    node_hash,
    verify_checkpoint_growth,
    verify_consistency,
)


class RFC9162ConsistencyTests(unittest.TestCase):
    def setUp(self):
        self.entries = [f"d{i}".encode() for i in range(17)]

    def roots(self, first, second):
        return merkle_tree_hash(self.entries[:first]), merkle_tree_hash(self.entries[:second])

    def test_valid_non_power_of_two_sizes(self):
        for first, second in [(3, 7), (5, 9), (6, 7), (9, 17), (13, 17)]:
            with self.subTest(first=first, second=second):
                p = consistency_proof(first, self.entries[:second])
                r1, r2 = self.roots(first, second)
                self.assertTrue(verify_consistency(first, second, r1, r2, p))

    def test_equal_size_requires_empty_proof_and_same_root(self):
        root = merkle_tree_hash(self.entries[:7])
        self.assertTrue(verify_consistency(7, 7, root, root, []))
        with self.assertRaises(RootMismatch):
            verify_consistency(7, 7, root, b"\x01" * 32, [])
        with self.assertRaises(MalformedProof):
            verify_consistency(7, 7, root, root, [root])

    def test_old_larger_than_new_rejected(self):
        r7, r3 = self.roots(7, 3)
        with self.assertRaises(SizeError):
            verify_consistency(7, 3, r7, r3, [])

    def test_tampered_node_rejected(self):
        p = list(consistency_proof(3, self.entries[:7]))
        p[1] = bytes([p[1][0] ^ 1]) + p[1][1:]
        r1, r2 = self.roots(3, 7)
        with self.assertRaises((RootMismatch, MalformedProof)):
            verify_consistency(3, 7, r1, r2, p)

    def test_missing_and_extra_nodes_rejected(self):
        p = list(consistency_proof(6, self.entries[:17]))
        r1, r2 = self.roots(6, 17)
        with self.assertRaises((RootMismatch, MalformedProof)):
            verify_consistency(6, 17, r1, r2, p[:-1])
        with self.assertRaises(MalformedProof):
            verify_consistency(6, 17, r1, r2, p + [p[-1]])

    def test_power_of_two_boundaries(self):
        for first, second in [(1, 2), (2, 3), (4, 7), (8, 9), (8, 16), (16, 17)]:
            with self.subTest(first=first, second=second):
                p = consistency_proof(first, self.entries[:second])
                r1, r2 = self.roots(first, second)
                self.assertTrue(verify_consistency(first, second, r1, r2, p))

    def test_empty_tree_boundary_is_explicitly_rejected(self):
        with self.assertRaises(SizeError):
            verify_consistency(0, 7, hashlib.sha256(b"").digest(), merkle_tree_hash(self.entries[:7]), [])
        with self.assertRaises(SizeError):
            consistency_proof(0, self.entries[:7])

    def test_one_leaf_old_tree_is_supported(self):
        p = consistency_proof(1, self.entries[:7])
        r1, r2 = self.roots(1, 7)
        self.assertTrue(verify_consistency(1, 7, r1, r2, p))

    def test_rfc9162_section_2_1_5_examples_exact_nodes(self):
        a,b,c,d,e,f,j = [leaf_hash(x) for x in self.entries[:7]]
        g = node_hash(a,b); h = node_hash(c,d); i = node_hash(e,f)
        k = node_hash(g,h); l = node_hash(i,j)
        self.assertEqual(consistency_proof(3, self.entries[:7]), (c, d, g, l))
        self.assertEqual(consistency_proof(4, self.entries[:7]), (l,))
        self.assertEqual(consistency_proof(6, self.entries[:7]), (i, j, k))

    def test_checkpoint_integration_needs_no_prior_leaf_material(self):
        p = consistency_proof(5, self.entries[:13])
        old = Checkpoint(5, merkle_tree_hash(self.entries[:5]))
        new = Checkpoint(13, merkle_tree_hash(self.entries[:13]))
        self.assertTrue(verify_checkpoint_growth(old, new, p))

    def test_exhaustive_pairs_up_to_64(self):
        entries = [bytes([i]) for i in range(64)]
        checked = 0
        for second in range(2, 65):
            for first in range(1, second):
                p = consistency_proof(first, entries[:second])
                self.assertLessEqual(len(p), (second - 1).bit_length() + 1)
                self.assertTrue(verify_consistency(
                    first, second,
                    merkle_tree_hash(entries[:first]),
                    merkle_tree_hash(entries[:second]), p))
                checked += 1
        self.assertEqual(checked, 2016)

    def test_boolean_sizes_are_rejected(self):
        root = merkle_tree_hash(self.entries[:1])
        with self.assertRaises(SizeError):
            verify_consistency(True, 1, root, root, [])

    def test_malformed_hash_lengths_fail_closed(self):
        p = list(consistency_proof(3, self.entries[:7]))
        p[0] = b"short"
        r1, r2 = self.roots(3,7)
        with self.assertRaises(MalformedProof):
            verify_consistency(3,7,r1,r2,p)


if __name__ == "__main__":
    unittest.main()
