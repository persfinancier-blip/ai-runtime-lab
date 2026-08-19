import struct
import unittest
from dataclasses import replace

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from experiments.ctv2_sth_chain.protocol import (
    BindingError, ED25519, Extension, LogProfile, Malformed, ProfileError,
    SignatureError, SignedTreeHeadV2, TrailingData, TreeHeadDataV2, WrongType,
    authenticate_sth, decode_signed_sth, encode_signed_sth, encode_tree_head,
    sign_sth, unsafe_trust_parsed_fields, verify_authenticated_growth,
)
from experiments.ctv2_consistency_wire.protocol import ConsistencyProofV2, encode_consistency_proof
from experiments.rfc9162_consistency.protocol import consistency_proof, merkle_tree_hash

LOG_ID = bytes.fromhex('2b65645000')
OTHER_LOG = bytes.fromhex('2b65645001')
HASH_SIZE = 32


def key(seed=0):
    raw=bytes((i+seed)%256 for i in range(32))
    return Ed25519PrivateKey.from_private_bytes(raw)


def pub(k): return k.public_key().public_bytes_raw()


class STHChainTests(unittest.TestCase):
    def setUp(self):
        self.k=key(0)
        self.profile=LogProfile(LOG_ID,HASH_SIZE,ED25519,pub(self.k))
        self.entries=[f'd{i}'.encode() for i in range(7)]
        self.old_tree=TreeHeadDataV2(1000,3,merkle_tree_hash(self.entries[:3]),())
        self.new_tree=TreeHeadDataV2(2000,7,merkle_tree_hash(self.entries),())
        self.old=sign_sth(self.old_tree,log_id=LOG_ID,private_key=self.k,hash_size=HASH_SIZE)
        self.new=sign_sth(self.new_tree,log_id=LOG_ID,private_key=self.k,hash_size=HASH_SIZE)
        proof=consistency_proof(3,self.entries)
        self.consistency=encode_consistency_proof(ConsistencyProofV2(LOG_ID,3,7,proof))

    def test_round_trip_and_exact_signature_input(self):
        sth, tree_bytes=decode_signed_sth(self.old,hash_size=HASH_SIZE)
        self.assertEqual(sth.tree_head,self.old_tree)
        self.assertEqual(tree_bytes,encode_tree_head(self.old_tree,hash_size=HASH_SIZE))
        self.assertEqual(encode_signed_sth(sth,hash_size=HASH_SIZE),self.old)
        self.assertEqual(authenticate_sth(self.old,self.profile).tree_head_bytes,tree_bytes)

    def test_correct_signature_accepted(self):
        auth=authenticate_sth(self.old,self.profile)
        self.assertEqual(auth.sth.tree_head.tree_size,3)

    def test_wrong_log_id_profile_rejected_even_same_key(self):
        bad_profile=replace(self.profile,log_id=OTHER_LOG)
        with self.assertRaises(BindingError): authenticate_sth(self.old,bad_profile)

    def test_wrong_key_rejected(self):
        with self.assertRaises(SignatureError): authenticate_sth(self.old,replace(self.profile,public_key=pub(key(9))))

    def test_unknown_signature_profile_rejected(self):
        with self.assertRaises(ProfileError): authenticate_sth(self.old,replace(self.profile,signature_scheme=0x0403))

    def test_mutated_tree_fields_rejected(self):
        sth,_=decode_signed_sth(self.old,hash_size=HASH_SIZE)
        variants=[
            replace(sth.tree_head,timestamp=1001),
            replace(sth.tree_head,tree_size=4),
            replace(sth.tree_head,root_hash=b'x'*32),
            replace(sth.tree_head,sth_extensions=(Extension(1,b'x'),)),
        ]
        for tree in variants:
            forged=encode_signed_sth(SignedTreeHeadV2(LOG_ID,tree,sth.signature),hash_size=HASH_SIZE)
            with self.subTest(tree=tree):
                with self.assertRaises(SignatureError): authenticate_sth(forged,self.profile)

    def test_trailing_and_wrong_type_rejected(self):
        with self.assertRaises(TrailingData): decode_signed_sth(self.old+b'junk',hash_size=HASH_SIZE)
        bad=bytearray(self.old); bad[0:2]=struct.pack('!H',0x0105)
        with self.assertRaises(WrongType): decode_signed_sth(bytes(bad),hash_size=HASH_SIZE)

    def test_truncated_rejected(self):
        for cut in [1,3,10,len(self.old)-1]:
            with self.subTest(cut=cut):
                with self.assertRaises(Exception): decode_signed_sth(self.old[:cut],hash_size=HASH_SIZE)

    def test_hash_profile_mismatch_rejected(self):
        with self.assertRaises(Malformed): decode_signed_sth(self.old,hash_size=48)

    def test_extensions_must_be_sorted_unique(self):
        tree=replace(self.old_tree,sth_extensions=(Extension(2,b'a'),Extension(1,b'b')))
        with self.assertRaises(Malformed): encode_tree_head(tree,hash_size=HASH_SIZE)
        tree=replace(self.old_tree,sth_extensions=(Extension(1,b'a'),Extension(1,b'b')))
        with self.assertRaises(Malformed): encode_tree_head(tree,hash_size=HASH_SIZE)

    def test_full_signed_sth_to_consistency_chain(self):
        self.assertTrue(verify_authenticated_growth(self.old,self.new,self.consistency,self.profile))

    def test_proof_from_other_log_rejected(self):
        proof=consistency_proof(3,self.entries)
        bad=encode_consistency_proof(ConsistencyProofV2(OTHER_LOG,3,7,proof))
        with self.assertRaises(Exception): verify_authenticated_growth(self.old,self.new,bad,self.profile)

    def test_proof_wrong_size_pair_rejected(self):
        proof=consistency_proof(3,self.entries)
        bad=encode_consistency_proof(ConsistencyProofV2(LOG_ID,2,7,proof))
        with self.assertRaises(Exception): verify_authenticated_growth(self.old,self.new,bad,self.profile)

    def test_new_timestamp_must_advance(self):
        same=TreeHeadDataV2(1000,7,merkle_tree_hash(self.entries),())
        new=sign_sth(same,log_id=LOG_ID,private_key=self.k,hash_size=HASH_SIZE)
        with self.assertRaises(BindingError): verify_authenticated_growth(self.old,new,self.consistency,self.profile)

    def test_boolean_uint64_rejected(self):
        with self.assertRaises(Malformed): encode_tree_head(replace(self.old_tree,timestamp=True),hash_size=HASH_SIZE)

    def test_strict_oid_rejected_nonminimal(self):
        bad_profile=replace(self.profile,log_id=b'\x80\x01')
        with self.assertRaises(Malformed): authenticate_sth(self.old,bad_profile)


if __name__=='__main__': unittest.main()
