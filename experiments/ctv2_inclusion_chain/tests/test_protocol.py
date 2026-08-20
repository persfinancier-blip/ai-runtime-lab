import hashlib
import struct
import unittest

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from experiments.ctv2_inclusion_chain.protocol import (
    BindingError, InclusionProofV2, Malformed, RootMismatch, TrailingData, Truncated,
    WrongType, decode_inclusion_proof, encode_inclusion_proof, leaf_hash_exact,
    verify_authenticated_inclusion, verify_inclusion_hash,
)
from experiments.ctv2_sth_chain.protocol import ED25519, LogProfile, TreeHeadDataV2, sign_sth
from experiments.rfc9162_consistency.protocol import merkle_tree_hash


def node_hash(a,b): return hashlib.sha256(b"\x01"+a+b).digest()
def largest_pow2_lt(n): return 1 << ((n-1).bit_length()-1)

def path(index, entries):
    n=len(entries)
    if n==1: return ()
    k=largest_pow2_lt(n)
    if index < k:
        return path(index,entries[:k]) + (merkle_tree_hash(entries[k:]),)
    return path(index-k,entries[k:]) + (merkle_tree_hash(entries[:k]),)

def leaf(i):
    return struct.pack("!H",0x0100) + b"leaf-" + bytes([i])

class InclusionChainTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.log_id=b"\x2b\x06\x01\x04\x01\x83\xb2\x03\x01"
        cls.sk=Ed25519PrivateKey.from_private_bytes(bytes(range(1,33)))
        pk=cls.sk.public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)
        cls.profile=LogProfile(cls.log_id,32,ED25519,pk)
        cls.entries=[leaf(i) for i in range(7)]
        cls.root=merkle_tree_hash(cls.entries)
        cls.sth=sign_sth(TreeHeadDataV2(123456789,7,cls.root),log_id=cls.log_id,private_key=cls.sk,hash_size=32)
        cls.index=3
        cls.item=InclusionProofV2(cls.log_id,7,cls.index,path(cls.index,cls.entries))
        cls.wire=encode_inclusion_proof(cls.item)

    def test_end_to_end_exact_leaf_signed_sth_and_wire_proof(self):
        self.assertTrue(verify_authenticated_inclusion(self.entries[self.index],self.sth,self.wire,self.profile))

    def test_wire_roundtrip(self):
        self.assertEqual(decode_inclusion_proof(self.wire,hash_size=32),self.item)

    def test_leaf_hash_is_exact_transitem_bytes(self):
        a=self.entries[self.index]
        b=a+b"\x00"
        self.assertNotEqual(leaf_hash_exact(a),leaf_hash_exact(b))

    def test_mutated_leaf_rejected(self):
        bad=bytearray(self.entries[self.index]); bad[-1]^=1
        with self.assertRaises(RootMismatch):
            verify_authenticated_inclusion(bytes(bad),self.sth,self.wire,self.profile)

    def test_wrong_log_id_rejected(self):
        other=InclusionProofV2(b"\x2b\x06\x01\x04\x01\x83\xb2\x03\x02",7,self.index,self.item.inclusion_path)
        with self.assertRaises(BindingError):
            verify_authenticated_inclusion(self.entries[self.index],self.sth,encode_inclusion_proof(other),self.profile)

    def test_wrong_tree_size_rejected(self):
        other=InclusionProofV2(self.log_id,6,self.index,self.item.inclusion_path)
        with self.assertRaises(BindingError):
            verify_authenticated_inclusion(self.entries[self.index],self.sth,encode_inclusion_proof(other),self.profile)

    def test_wrong_leaf_index_rejected(self):
        other=InclusionProofV2(self.log_id,7,self.index+1,self.item.inclusion_path)
        with self.assertRaises(RootMismatch):
            verify_authenticated_inclusion(self.entries[self.index],self.sth,encode_inclusion_proof(other),self.profile)

    def test_mutated_sth_root_fails_signature(self):
        bad=bytearray(self.sth)
        off=2+1+len(self.log_id)+8+8+1
        bad[off]^=1
        with self.assertRaises(Exception):
            verify_authenticated_inclusion(self.entries[self.index],bytes(bad),self.wire,self.profile)

    def test_different_but_validly_signed_root_rejected_by_merkle_proof(self):
        wrong_root=bytearray(self.root); wrong_root[0]^=1
        other_sth=sign_sth(
            TreeHeadDataV2(123456790,7,bytes(wrong_root)),
            log_id=self.log_id,private_key=self.sk,hash_size=32
        )
        with self.assertRaises(RootMismatch):
            verify_authenticated_inclusion(self.entries[self.index],other_sth,self.wire,self.profile)

    def test_trailing_bytes_rejected(self):
        with self.assertRaises(TrailingData):
            decode_inclusion_proof(self.wire+b"x",hash_size=32)

    def test_truncated_rejected(self):
        with self.assertRaises(Truncated):
            decode_inclusion_proof(self.wire[:-1],hash_size=32)

    def test_wrong_type_rejected(self):
        bad=bytearray(self.wire); bad[1]=0x05
        with self.assertRaises(WrongType):
            decode_inclusion_proof(bytes(bad),hash_size=32)

    def test_wrong_hash_length_rejected(self):
        bad=bytearray(self.wire)
        pos=2+1+len(self.log_id)+8+8+2
        bad[pos]=31
        with self.assertRaises((Malformed,Truncated)):
            decode_inclusion_proof(bytes(bad),hash_size=32)

    def test_leaf_index_equal_tree_size_rejected(self):
        bad=InclusionProofV2(self.log_id,7,7,())
        with self.assertRaises(Malformed):
            decode_inclusion_proof(encode_inclusion_proof(bad),hash_size=32)

    def test_boolean_sizes_not_accepted_by_verifier(self):
        with self.assertRaises(Malformed):
            verify_inclusion_hash(leaf_hash_exact(self.entries[0]),leaf_index=0,tree_size=True,root_hash=self.root,inclusion_path=())

    def test_all_indices_sizes_1_through_32(self):
        for size in range(1,33):
            entries=[leaf(i % 250) + struct.pack("!H",size) for i in range(size)]
            root=merkle_tree_hash(entries)
            for index,item in enumerate(entries):
                self.assertTrue(verify_inclusion_hash(
                    leaf_hash_exact(item),leaf_index=index,tree_size=size,
                    root_hash=root,inclusion_path=path(index,entries)
                ))

    def test_single_leaf_empty_proof(self):
        one=[leaf(9)]
        root=merkle_tree_hash(one)
        self.assertTrue(verify_inclusion_hash(leaf_hash_exact(one[0]),leaf_index=0,tree_size=1,root_hash=root,inclusion_path=()))

if __name__=="__main__":
    unittest.main()
