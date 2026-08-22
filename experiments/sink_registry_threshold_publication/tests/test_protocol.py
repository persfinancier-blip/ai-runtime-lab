import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from experiments.anchor_threshold_root.protocol import RootState, Signature, key_id
from experiments.sink_registry_binding.protocol import RegistryEntry
from experiments.sink_registry_threshold_publication.protocol import *


def keys(prefix, n=3):
    raw = [f"{prefix}-{i}".encode() for i in range(n)]
    return raw, {key_id(k): k.hex() for k in raw}


class Tests(unittest.TestCase):
    def setUp(self):
        self.raw, mapping = keys("root", 3)
        self.root = RootState("sink-registry", 1, 1, 2, mapping)
        self.entry = publication_entry(
            self.root,
            sink_id="sink-A",
            generation=1,
            adapter_digest="a" * 64,
            endpoint_origin="https://sink.example",
            operation_profile="charge-v1",
        )

    def proof(self, *indexes):
        return tuple(sign_publication(self.entry, self.raw[i]) for i in indexes)

    def test_two_distinct_signers_meet_threshold(self):
        env = make_envelope(self.root, self.entry, self.proof(0, 1))
        self.assertEqual(verify_envelope(self.root, env), env)

    def test_one_compromised_signer_cannot_publish(self):
        with self.assertRaises(InvalidSignatureSet):
            make_envelope(self.root, self.entry, self.proof(0))

    def test_duplicate_signer_does_not_inflate_threshold(self):
        sig = sign_publication(self.entry, self.raw[0])
        with self.assertRaises(InvalidSignatureSet):
            make_envelope(self.root, self.entry, (sig, sig))

    def test_unknown_signer_rejected_even_with_other_valid_signatures(self):
        outsider = b"outsider"
        with self.assertRaises(InvalidSignatureSet):
            make_envelope(
                self.root,
                self.entry,
                (
                    self.proof(0)[0],
                    self.proof(1)[0],
                    sign_publication(self.entry, outsider),
                ),
            )

    def test_revoked_signer_rejected(self):
        revoked = RootState(
            self.root.provider_id,
            self.root.version,
            self.root.authority_epoch,
            2,
            self.root.keys,
            (key_id(self.raw[0]),),
        )
        entry = publication_entry(
            revoked,
            sink_id="sink-A",
            generation=1,
            adapter_digest="a" * 64,
            endpoint_origin="https://sink.example",
            operation_profile="charge-v1",
        )
        with self.assertRaises(InvalidSignatureSet):
            make_envelope(
                revoked,
                entry,
                (
                    sign_publication(entry, self.raw[0]),
                    sign_publication(entry, self.raw[1]),
                ),
            )

    def test_malformed_or_invalid_signature_rejected(self):
        good = self.proof(0)[0]
        bad = Signature(key_id(self.raw[1]), "0" * 64)
        with self.assertRaises(InvalidSignatureSet):
            make_envelope(self.root, self.entry, (good, bad))

    def test_signature_set_for_entry_a_cannot_attach_to_entry_b(self):
        env = make_envelope(self.root, self.entry, self.proof(0, 1))
        other = publication_entry(
            self.root,
            sink_id="sink-A",
            generation=1,
            adapter_digest="b" * 64,
            endpoint_origin="https://evil.example",
            operation_profile="charge-v1",
        )
        forged = ThresholdEnvelope(
            RegistryEntry(**other.unsigned, signature=env.proof.proof_digest),
            env.proof,
        )
        with self.assertRaises(InvalidSignatureSet):
            verify_envelope(self.root, forged)

    def test_stale_authority_generation_rejected_for_new_publication(self):
        env = make_envelope(self.root, self.entry, self.proof(0, 1))
        _, map2 = keys("root2", 3)
        current = RootState("sink-registry", 2, 1, 2, map2)
        with self.assertRaises(AuthorityMismatch):
            verify_envelope(current, env)

    def test_historical_threshold_semantics_survive_new_root_threshold(self):
        env = make_envelope(self.root, self.entry, self.proof(0, 1))
        with tempfile.TemporaryDirectory() as td:
            store = ThresholdProofStore(Path(td) / "proofs.db")
            digest = store.accept(self.root, env)
            _, map2 = keys("root2", 4)
            _current = RootState("sink-registry", 2, 1, 3, map2)
            historical = store.verify_historical(digest)
            self.assertEqual(historical, env)

    def test_stored_threshold_proof_corruption_detected(self):
        env = make_envelope(self.root, self.entry, self.proof(0, 1))
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "proofs.db"
            store = ThresholdProofStore(path)
            digest = store.accept(self.root, env)
            q = sqlite3.connect(path)
            proof = json.loads(
                q.execute("SELECT proof_json FROM threshold_publications").fetchone()[0]
            )
            proof["signatures"][0]["signature"] = "0" * 64
            q.execute(
                "UPDATE threshold_publications SET proof_json=?",
                (json.dumps(proof, sort_keys=True, separators=(",", ":")),),
            )
            q.commit()
            q.close()
            with self.assertRaises((InvalidSignatureSet, ProofSubstitution)):
                store.verify_historical(digest)

    def test_unsafe_single_signer_baseline_accepts(self):
        signature = sign_publication(self.entry, self.raw[0])
        self.assertTrue(
            UnsafeSingleSignerPublication.accepts(self.root, self.entry, signature)
        )


if __name__ == "__main__":
    unittest.main()
