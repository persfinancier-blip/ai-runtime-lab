import unittest

from experiments.rfc9162_consistency.protocol import (
    consistency_proof,
    merkle_tree_hash,
    unsafe_verify_new_root_only,
)


class UnsafeNewRootOnly(unittest.TestCase):
    def test_unrelated_old_checkpoint_should_be_rejected_but_is_accepted(self):
        entries = [f"d{i}".encode() for i in range(7)]
        proof = consistency_proof(3, entries)
        real_new = merkle_tree_hash(entries)
        unrelated_old = merkle_tree_hash([b"attacker", b"history", b"fork"])
        accepted = unsafe_verify_new_root_only(3, 7, unrelated_old, real_new, proof)
        self.assertFalse(accepted, "unsafe verifier ignored reconstructed old root")


if __name__ == "__main__":
    unittest.main()
