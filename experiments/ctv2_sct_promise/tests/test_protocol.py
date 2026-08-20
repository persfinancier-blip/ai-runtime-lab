import hashlib
import unittest

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from experiments.ctv2_sct_promise.protocol import (
    BindingError, Extension, Malformed, PromiseStatus, SignatureError, SnapshotError,
    TrailingData, Truncated, WrongType, SignedCertificateTimestampV2,
    PRECERT_SCT_V2, X509_ENTRY_V2,
    audit_sct_promise, authenticate_sct_to_exact_leaf, decode_sct, encode_leaf,
    encode_sct, sign_sct_for_leaf,
)
from experiments.ctv2_sth_chain.protocol import ED25519, LogProfile, TreeHeadDataV2, sign_sth
from experiments.ctv2_inclusion_chain.protocol import InclusionProofV2, encode_inclusion_proof
from experiments.rfc9162_consistency.protocol import merkle_tree_hash


def largest_pow2_lt(n): return 1 << ((n - 1).bit_length() - 1)
def path(index, entries):
    if len(entries) == 1: return ()
    k = largest_pow2_lt(len(entries))
    if index < k:
        return path(index, entries[:k]) + (merkle_tree_hash(entries[k:]),)
    return path(index-k, entries[k:]) + (merkle_tree_hash(entries[:k]),)


class SCTPromiseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.log_id = b"\x2b\x06\x01\x04\x01\x83\xb2\x03\x01"
        cls.other_log_id = b"\x2b\x06\x01\x04\x01\x83\xb2\x03\x02"
        cls.sk = Ed25519PrivateKey.from_private_bytes(bytes(range(1,33)))
        pk = cls.sk.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        cls.profile = LogProfile(cls.log_id, 32, ED25519, pk)
        cls.ts = 1_000_000
        cls.mmd = 10_000
        cls.ext = (Extension(7,b"policy"),)
        cls.leaf = encode_leaf(
            versioned_type=X509_ENTRY_V2, timestamp=cls.ts,
            issuer_key_hash=hashlib.sha256(b"issuer").digest(),
            tbs_certificate=b"synthetic-tbs-certificate-A", sct_extensions=cls.ext,
        )
        cls.sct = sign_sct_for_leaf(cls.leaf, log_id=cls.log_id, private_key=cls.sk)
        cls.other_leaf = encode_leaf(
            versioned_type=X509_ENTRY_V2, timestamp=cls.ts,
            issuer_key_hash=hashlib.sha256(b"issuer").digest(),
            tbs_certificate=b"synthetic-tbs-certificate-B", sct_extensions=cls.ext,
        )
        cls.entries = [
            encode_leaf(versioned_type=X509_ENTRY_V2,timestamp=cls.ts-3+i,
                        issuer_key_hash=hashlib.sha256(f"iss{i}".encode()).digest(),
                        tbs_certificate=f"other-{i}".encode())
            for i in range(2)
        ] + [cls.leaf] + [
            encode_leaf(versioned_type=X509_ENTRY_V2,timestamp=cls.ts+i,
                        issuer_key_hash=hashlib.sha256(f"issx{i}".encode()).digest(),
                        tbs_certificate=f"tail-{i}".encode())
            for i in range(2)
        ]
        cls.index=2
        root=merkle_tree_hash(cls.entries)
        cls.sth_before_deadline=sign_sth(TreeHeadDataV2(cls.ts+5_000,len(cls.entries),root),log_id=cls.log_id,private_key=cls.sk,hash_size=32)
        cls.sth_after_deadline=sign_sth(TreeHeadDataV2(cls.ts+20_000,len(cls.entries),root),log_id=cls.log_id,private_key=cls.sk,hash_size=32)
        cls.proof=encode_inclusion_proof(InclusionProofV2(cls.log_id,len(cls.entries),cls.index,path(cls.index,cls.entries)))

    def test_exact_sct_leaf_binding(self):
        auth=authenticate_sct_to_exact_leaf(self.sct,self.leaf,self.profile)
        self.assertEqual(auth.sct.timestamp,self.ts)
        self.assertEqual(auth.leaf.sct_extensions,self.ext)

    def test_inclusion_before_deadline_is_fulfilled(self):
        out=audit_sct_promise(sct_wire=self.sct,leaf_wire=self.leaf,sth_wire=self.sth_before_deadline,
                              profile=self.profile,mmd_ms=self.mmd,inclusion_wire=self.proof)
        self.assertEqual(out.status,PromiseStatus.FULFILLED)

    def test_inclusion_under_post_deadline_sth_is_still_fulfilled_not_proof_of_late_insert(self):
        out=audit_sct_promise(sct_wire=self.sct,leaf_wire=self.leaf,sth_wire=self.sth_after_deadline,
                              profile=self.profile,mmd_ms=self.mmd,inclusion_wire=self.proof)
        self.assertEqual(out.status,PromiseStatus.FULFILLED)

    def test_predeadline_without_inclusion_is_not_yet_auditable(self):
        out=audit_sct_promise(sct_wire=self.sct,leaf_wire=self.leaf,sth_wire=self.sth_before_deadline,
                              profile=self.profile,mmd_ms=self.mmd)
        self.assertEqual(out.status,PromiseStatus.NOT_YET_AUDITABLE)

    def test_postdeadline_without_membership_or_nonmembership_evidence_is_inconclusive(self):
        out=audit_sct_promise(sct_wire=self.sct,leaf_wire=self.leaf,sth_wire=self.sth_after_deadline,
                              profile=self.profile,mmd_ms=self.mmd)
        self.assertEqual(out.status,PromiseStatus.INCONCLUSIVE_AFTER_DEADLINE)

    def test_complete_authenticated_postdeadline_snapshot_absence_proves_violation(self):
        absent=tuple(x for x in self.entries if x != self.leaf)
        root=merkle_tree_hash(absent)
        sth=sign_sth(TreeHeadDataV2(self.ts+20_000,len(absent),root),log_id=self.log_id,private_key=self.sk,hash_size=32)
        out=audit_sct_promise(sct_wire=self.sct,leaf_wire=self.leaf,sth_wire=sth,
                              profile=self.profile,mmd_ms=self.mmd,complete_snapshot_leaves=absent)
        self.assertEqual(out.status,PromiseStatus.MMD_VIOLATION)

    def test_complete_snapshot_containing_leaf_is_fulfilled(self):
        out=audit_sct_promise(sct_wire=self.sct,leaf_wire=self.leaf,sth_wire=self.sth_after_deadline,
                              profile=self.profile,mmd_ms=self.mmd,complete_snapshot_leaves=tuple(self.entries))
        self.assertEqual(out.status,PromiseStatus.FULFILLED)

    def test_substituted_leaf_rejected_by_sct_signature(self):
        with self.assertRaises(SignatureError):
            authenticate_sct_to_exact_leaf(self.sct,self.other_leaf,self.profile)

    def test_sct_logid_mismatch_rejected(self):
        parsed=decode_sct(self.sct)
        forged=encode_sct(SignedCertificateTimestampV2(parsed.versioned_type,self.other_log_id,parsed.timestamp,parsed.sct_extensions,parsed.signature))
        with self.assertRaises(BindingError):
            authenticate_sct_to_exact_leaf(forged,self.leaf,self.profile)

    def test_sct_timestamp_mismatch_rejected_before_signature(self):
        parsed=decode_sct(self.sct)
        bad=encode_sct(SignedCertificateTimestampV2(parsed.versioned_type,parsed.log_id,parsed.timestamp+1,parsed.sct_extensions,parsed.signature))
        with self.assertRaises(BindingError):
            authenticate_sct_to_exact_leaf(bad,self.leaf,self.profile)

    def test_sct_extension_mismatch_rejected(self):
        parsed=decode_sct(self.sct)
        bad=encode_sct(SignedCertificateTimestampV2(parsed.versioned_type,parsed.log_id,parsed.timestamp,(Extension(7,b"other"),),parsed.signature))
        with self.assertRaises(BindingError):
            authenticate_sct_to_exact_leaf(bad,self.leaf,self.profile)

    def test_sct_leaf_type_mismatch_rejected(self):
        parsed=decode_sct(self.sct)
        bad=encode_sct(SignedCertificateTimestampV2(PRECERT_SCT_V2,parsed.log_id,parsed.timestamp,parsed.sct_extensions,parsed.signature))
        with self.assertRaises(BindingError):
            authenticate_sct_to_exact_leaf(bad,self.leaf,self.profile)

    def test_corrupted_sct_signature_rejected(self):
        parsed=decode_sct(self.sct)
        sig=bytearray(parsed.signature);sig[-1]^=1
        bad=encode_sct(SignedCertificateTimestampV2(parsed.versioned_type,parsed.log_id,parsed.timestamp,parsed.sct_extensions,bytes(sig)))
        with self.assertRaises(SignatureError):
            authenticate_sct_to_exact_leaf(bad,self.leaf,self.profile)

    def test_strict_decoder_wrong_type_truncation_trailing(self):
        bad=bytearray(self.sct);bad[1]=0x04
        with self.assertRaises(WrongType): decode_sct(bytes(bad))
        with self.assertRaises(Truncated): decode_sct(self.sct[:-1])
        with self.assertRaises(TrailingData): decode_sct(self.sct+b"x")

    def test_empty_signature_rejected(self):
        parsed=decode_sct(self.sct)
        with self.assertRaises(Malformed):
            encode_sct(SignedCertificateTimestampV2(parsed.versioned_type,parsed.log_id,parsed.timestamp,parsed.sct_extensions,b""))

    def test_authenticated_inclusion_wrong_root_rejected(self):
        wrong=bytearray(merkle_tree_hash(self.entries)); wrong[0]^=1
        sth=sign_sth(TreeHeadDataV2(self.ts+20_000,len(self.entries),bytes(wrong)),log_id=self.log_id,private_key=self.sk,hash_size=32)
        with self.assertRaises(Exception):
            audit_sct_promise(sct_wire=self.sct,leaf_wire=self.leaf,sth_wire=sth,
                              profile=self.profile,mmd_ms=self.mmd,inclusion_wire=self.proof)

    def test_complete_snapshot_rejects_malformed_ct_leaf_even_if_bytes_are_supplied(self):
        malformed=list(self.entries)
        malformed[0]=b"not-a-ct-leaf"
        root=merkle_tree_hash(tuple(malformed))
        sth=sign_sth(TreeHeadDataV2(self.ts+20_000,len(malformed),root),log_id=self.log_id,private_key=self.sk,hash_size=32)
        with self.assertRaises((WrongType, Truncated, Malformed)):
            audit_sct_promise(sct_wire=self.sct,leaf_wire=self.leaf,sth_wire=sth,
                              profile=self.profile,mmd_ms=self.mmd,complete_snapshot_leaves=tuple(malformed))

    def test_snapshot_wrong_root_rejected(self):
        with self.assertRaises(SnapshotError):
            audit_sct_promise(sct_wire=self.sct,leaf_wire=self.leaf,sth_wire=self.sth_after_deadline,
                              profile=self.profile,mmd_ms=self.mmd,complete_snapshot_leaves=tuple(self.entries[:-1]))

    def test_mmd_boolean_and_overflow_rejected(self):
        with self.assertRaises(Malformed):
            audit_sct_promise(sct_wire=self.sct,leaf_wire=self.leaf,sth_wire=self.sth_after_deadline,
                              profile=self.profile,mmd_ms=True)
        leaf=encode_leaf(versioned_type=X509_ENTRY_V2,timestamp=(1<<64)-2,
                         issuer_key_hash=hashlib.sha256(b"z").digest(),tbs_certificate=b"x")
        sct=sign_sct_for_leaf(leaf,log_id=self.log_id,private_key=self.sk)
        root=merkle_tree_hash((leaf,))
        sth=sign_sth(TreeHeadDataV2((1<<64)-1,1,root),log_id=self.log_id,private_key=self.sk,hash_size=32)
        with self.assertRaises(Malformed):
            audit_sct_promise(sct_wire=sct,leaf_wire=leaf,sth_wire=sth,profile=self.profile,mmd_ms=2)


if __name__=='__main__': unittest.main()
