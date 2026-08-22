import tempfile
import unittest
from pathlib import Path

from experiments.provider_threshold_rotation.protocol import *


def authority(name="rot-A", version=1, generation=1, threshold=2, count=3, revoked=()):
    raw = [f"{name}-{version}-{generation}-{i}".encode() for i in range(count)]
    keys = {key_id(k): k.hex() for k in raw}
    return RotationAuthority(name, version, generation, threshold, keys, tuple(revoked)), raw


def sigs(raw, payload, indexes):
    return tuple(Signature(key_id(raw[i]), mac(raw[i], payload)) for i in indexes)


class Tests(unittest.TestCase):
    def test_unsafe_old_plus_attacker_new_is_sufficient_without_threshold(self):
        self.assertTrue(UnsafeOldAndNewOnly.allows(True, True))

    def test_compromised_provider_keys_without_threshold_rejected(self):
        a, raw = authority()
        intent = ProviderRotationIntent("p", "a"*64, "b"*64, a.authority_id, a.version, a.generation)
        proof = ThresholdProof(intent.intent_digest, a.authority_id, a.version, a.generation, ())
        with self.assertRaises(ThresholdNotMet):
            verify_threshold(a, intent, proof)

    def test_distinct_quorum_authorizes_exact_transition(self):
        a, raw = authority()
        intent = ProviderRotationIntent("p", "a"*64, "b"*64, a.authority_id, a.version, a.generation)
        proof = ThresholdProof(intent.intent_digest, a.authority_id, a.version, a.generation, sigs(raw, intent.payload, [0,1]))
        self.assertEqual(len(verify_threshold(a, intent, proof)), 2)

    def test_duplicate_unknown_and_revoked_do_not_inflate(self):
        a0, raw = authority()
        revoked = key_id(raw[0])
        a = RotationAuthority(a0.authority_name,a0.version,a0.generation,2,a0.keys,(revoked,))
        intent = ProviderRotationIntent("p","a"*64,"b"*64,a.authority_id,a.version,a.generation)
        good = Signature(key_id(raw[1]), mac(raw[1], intent.payload))
        unknown = Signature("unknown", "0"*64)
        rev = Signature(key_id(raw[0]), mac(raw[0], intent.payload))
        with self.assertRaises(ThresholdNotMet):
            verify_threshold(a,intent,ThresholdProof(intent.intent_digest,a.authority_id,a.version,a.generation,(good,good,unknown,rev)))

    def test_proof_substitution_rejected(self):
        a, raw = authority()
        i1=ProviderRotationIntent("p","a"*64,"b"*64,a.authority_id,a.version,a.generation)
        i2=ProviderRotationIntent("p","a"*64,"c"*64,a.authority_id,a.version,a.generation)
        proof=ThresholdProof(i1.intent_digest,a.authority_id,a.version,a.generation,sigs(raw,i1.payload,[0,1]))
        with self.assertRaises(ProofSubstitution): verify_threshold(a,i2,proof)

    def test_authority_rotation_requires_old_and_new_threshold(self):
        with tempfile.TemporaryDirectory() as td:
            old, ork=authority()
            store=DurableRotationAuthority(Path(td)/"db",old)
            new,nrk=authority(version=2,generation=2)
            p=store.authority_rotation_payload(old,new)
            out=store.rotate_authority(new,sigs(ork,p,[0,1]),sigs(nrk,p,[0,1]))
            self.assertEqual(store.current().authority_id,new.authority_id)
            self.assertEqual(len(out["old_signers"]),2)

    def test_stale_authority_proof_rejected_after_rotation(self):
        with tempfile.TemporaryDirectory() as td:
            old, ork=authority()
            store=DurableRotationAuthority(Path(td)/"db",old)
            old_intent=ProviderRotationIntent("p","a"*64,"b"*64,old.authority_id,old.version,old.generation)
            old_sigs=sigs(ork,old_intent.payload,[0,1])
            new,nrk=authority(version=2,generation=2)
            p=store.authority_rotation_payload(old,new)
            store.rotate_authority(new,sigs(ork,p,[0,1]),sigs(nrk,p,[0,1]))
            q=store._con()
            try:
                q.execute("BEGIN IMMEDIATE")
                with self.assertRaises(ThresholdNotMet):
                    store.authorize_provider_rotation_locked(q,provider_id="p",old_generation_id="a"*64,new_generation_id="b"*64,signatures=old_sigs)
            finally:
                if q.in_transaction: q.rollback()
                q.close()

    def test_persisted_provider_threshold_proof_reverified(self):
        with tempfile.TemporaryDirectory() as td:
            a, raw=authority()
            store=DurableRotationAuthority(Path(td)/"db",a)
            q=store._con()
            try:
                q.execute("BEGIN IMMEDIATE")
                intent=ProviderRotationIntent("p","a"*64,"b"*64,a.authority_id,a.version,a.generation)
                store.authorize_provider_rotation_locked(q,provider_id="p",old_generation_id="a"*64,new_generation_id="b"*64,signatures=sigs(raw,intent.payload,[0,1]))
                q.commit()
                q.execute("BEGIN")
                store.verify_durable_locked(q,[("p","a"*64,"b"*64)])
                q.commit()
            finally:q.close()

    def test_corrupted_threshold_proof_fails_restart_verification(self):
        with tempfile.TemporaryDirectory() as td:
            a, raw=authority()
            store=DurableRotationAuthority(Path(td)/"db",a)
            intent=ProviderRotationIntent("p","a"*64,"b"*64,a.authority_id,a.version,a.generation)
            q=store._con()
            q.execute("BEGIN IMMEDIATE")
            store.authorize_provider_rotation_locked(q,provider_id="p",old_generation_id="a"*64,new_generation_id="b"*64,signatures=sigs(raw,intent.payload,[0,1]))
            q.commit()
            q.execute("UPDATE provider_rotation_threshold_proofs SET intent_digest=? WHERE new_provider_generation_id=?",("0"*64,"b"*64))
            q.commit()
            q.execute("BEGIN")
            with self.assertRaises(ProofSubstitution): store.verify_durable_locked(q,[("p","a"*64,"b"*64)])
            q.rollback();q.close()

    def test_same_sql_transaction_rolls_back_threshold_proof_with_caller_failure(self):
        with tempfile.TemporaryDirectory() as td:
            a, raw=authority()
            store=DurableRotationAuthority(Path(td)/"db",a)
            intent=ProviderRotationIntent("p","a"*64,"b"*64,a.authority_id,a.version,a.generation)
            q=store._con()
            q.execute("BEGIN IMMEDIATE")
            store.authorize_provider_rotation_locked(q,provider_id="p",old_generation_id="a"*64,new_generation_id="b"*64,signatures=sigs(raw,intent.payload,[0,1]))
            q.rollback();q.close()
            q=store._con()
            self.assertEqual(q.execute("SELECT COUNT(*) FROM provider_rotation_threshold_proofs").fetchone()[0],0)
            q.close()

if __name__=="__main__":
    unittest.main()
