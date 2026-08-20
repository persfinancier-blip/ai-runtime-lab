import struct
import unittest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from experiments.ctv2_inclusion_chain.protocol import InclusionProofV2, encode_inclusion_proof, leaf_hash_exact, unsafe_verify_supplied_leaf_hash
from experiments.ctv2_sth_chain.protocol import ED25519, LogProfile, TreeHeadDataV2, sign_sth
from experiments.rfc9162_consistency.protocol import merkle_tree_hash
from experiments.ctv2_inclusion_chain.tests.test_protocol import path

class UnsafeLeafBindingBaseline(unittest.TestCase):
    def test_artifact_substitution_should_fail_but_hash_only_verifier_accepts(self):
        log_id=b"\x2b\x06\x01\x04\x01\x83\xb2\x03\x01"
        sk=Ed25519PrivateKey.from_private_bytes(bytes(range(1,33)))
        pk=sk.public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)
        profile=LogProfile(log_id,32,ED25519,pk)
        real_leaf=struct.pack("!H",0x0100)+b"real-artifact"
        substituted_leaf=struct.pack("!H",0x0100)+b"attacker-artifact"
        entries=[b"\x01\x00a",real_leaf,b"\x01\x00c"]
        root=merkle_tree_hash(entries)
        sth=sign_sth(TreeHeadDataV2(1,3,root),log_id=log_id,private_key=sk,hash_size=32)
        proof=encode_inclusion_proof(InclusionProofV2(log_id,3,1,path(1,entries)))
        accepted=unsafe_verify_supplied_leaf_hash(leaf_hash_exact(real_leaf),sth,proof,profile)
        self.assertFalse(accepted, f"unsafe verifier accepted proof while caller presented different leaf bytes: {substituted_leaf!r}")

if __name__=="__main__":
    unittest.main()
