import hashlib
import unittest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from experiments.ctv2_sct_promise.protocol import X509_ENTRY_V2, encode_leaf, sign_sct_for_leaf, unsafe_accept_inclusion_without_sct_binding
from experiments.ctv2_sth_chain.protocol import ED25519,LogProfile,TreeHeadDataV2,sign_sth
from experiments.ctv2_inclusion_chain.protocol import InclusionProofV2,encode_inclusion_proof
from experiments.rfc9162_consistency.protocol import merkle_tree_hash

class UnsafeBaseline(unittest.TestCase):
    def test_inclusion_only_should_not_accept_different_sct_promise_but_does(self):
        log_id=b"\x2b\x06\x01\x04\x01\x83\xb2\x03\x01"
        sk=Ed25519PrivateKey.from_private_bytes(bytes(range(1,33)))
        pk=sk.public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)
        profile=LogProfile(log_id,32,ED25519,pk)
        promised=encode_leaf(versioned_type=X509_ENTRY_V2,timestamp=1000,issuer_key_hash=hashlib.sha256(b'i').digest(),tbs_certificate=b'promised')
        included=encode_leaf(versioned_type=X509_ENTRY_V2,timestamp=1000,issuer_key_hash=hashlib.sha256(b'i').digest(),tbs_certificate=b'different-artifact')
        presented_sct=sign_sct_for_leaf(promised,log_id=log_id,private_key=sk)
        self.assertTrue(presented_sct)
        root=merkle_tree_hash((included,))
        sth=sign_sth(TreeHeadDataV2(2000,1,root),log_id=log_id,private_key=sk,hash_size=32)
        proof=encode_inclusion_proof(InclusionProofV2(log_id,1,0,()))
        accepted=unsafe_accept_inclusion_without_sct_binding(leaf_wire=included,sth_wire=sth,inclusion_wire=proof,profile=profile)
        self.assertFalse(accepted,"unsafe inclusion-only check accepted a leaf that the presented SCT never promised")

if __name__=='__main__': unittest.main()
