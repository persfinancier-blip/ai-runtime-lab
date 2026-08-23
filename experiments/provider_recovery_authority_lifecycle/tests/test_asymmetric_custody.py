import sqlite3
import tempfile
import unittest
from pathlib import Path

from experiments.provider_recovery_authority_lifecycle.asymmetric_custody import (
    AsymmetricRecoveryCustody,
    CustodyThresholdNotMet,
    CustodySubstitution,
    PublicRecoveryAuthority,
    RecoverySigner,
    PublicSignature,
    custody_rotation_payload,
)


def authority(version=1, generation=1, prefix="recovery"):
    signers = [RecoverySigner.from_seed(bytes([version, generation, i]) + bytes(f"{prefix}-{i}", "utf-8")[:1] + b"x" * 28) for i in range(4)]
    public = PublicRecoveryAuthority(
        "provider-rotation-recovery",
        version,
        generation,
        3,
        {s.signer_id: s.public_key_hex for s in signers},
    )
    return public, signers


def signatures(signers, payload, count=3):
    return tuple(s.sign(payload) for s in signers[:count])


class AsymmetricCustodyTests(unittest.TestCase):
    def test_public_only_history_rotates_and_restarts(self):
        with tempfile.TemporaryDirectory() as td:
            old, olds = authority(); new, news = authority(2, 2, "new")
            path = Path(td) / "db"
            store = AsymmetricRecoveryCustody(path, old)
            payload = custody_rotation_payload(old, new, "root-1")
            store.rotate(new, "root-1", signatures(olds, payload), signatures(news, payload))
            restarted = AsymmetricRecoveryCustody(path, old)
            self.assertTrue(restarted.verify_durable())
            q = restarted._con()
            try:
                self.assertEqual(restarted.current_locked(q).authority_id, new.authority_id)
            finally:
                q.close()

    def test_old_public_material_remains_verification_only(self):
        old, olds = authority()
        self.assertFalse(hasattr(old, "sign"))
        self.assertFalse(any(hasattr(v, "sign") for v in old.public_keys.values()))
        payload = {"message": "historical"}
        sig = olds[0].sign(payload)
        self.assertEqual(sig.signer_id, olds[0].signer_id)

    def test_private_seed_material_is_not_in_durable_database(self):
        with tempfile.TemporaryDirectory() as td:
            old, olds = authority(); path = Path(td) / "db"
            AsymmetricRecoveryCustody(path, old)
            raw = path.read_bytes()
            for signer in olds:
                self.assertIn(signer.public_key_hex.encode(), raw)
            self.assertNotIn(b"recovery-", raw)

    def test_old_and_new_thresholds_are_both_required(self):
        with tempfile.TemporaryDirectory() as td:
            old, olds = authority(); new, news = authority(2, 2, "new")
            store = AsymmetricRecoveryCustody(Path(td) / "db", old)
            payload = custody_rotation_payload(old, new, "root-1")
            with self.assertRaises(CustodyThresholdNotMet):
                store.rotate(new, "root-1", signatures(olds, payload, 2), signatures(news, payload, 3))
            with self.assertRaises(CustodyThresholdNotMet):
                store.rotate(new, "root-1", signatures(olds, payload, 3), signatures(news, payload, 2))

    def test_malformed_extra_signature_cannot_denial_of_service_valid_quorum(self):
        with tempfile.TemporaryDirectory() as td:
            old, olds = authority(); new, news = authority(2, 2, "new")
            store = AsymmetricRecoveryCustody(Path(td) / "db", old)
            payload = custody_rotation_payload(old, new, "root-1")
            noisy_old = signatures(olds, payload) + (PublicSignature("junk", "not-hex"),)
            noisy_new = (PublicSignature("junk", "not-hex"),) + signatures(news, payload)
            store.rotate(new, "root-1", noisy_old, noisy_new)
            self.assertTrue(store.verify_durable())

    def test_tampered_public_transition_fails_restart(self):
        with tempfile.TemporaryDirectory() as td:
            old, olds = authority(); new, news = authority(2, 2, "new"); path = Path(td) / "db"
            store = AsymmetricRecoveryCustody(path, old); payload = custody_rotation_payload(old, new, "root-1")
            store.rotate(new, "root-1", signatures(olds, payload), signatures(news, payload))
            q = sqlite3.connect(path)
            q.execute("UPDATE provider_recovery_public_transitions SET old_signatures_json='[]'")
            q.commit(); q.close()
            with self.assertRaises(CustodyThresholdNotMet):
                AsymmetricRecoveryCustody(path, old)

    def test_public_authority_substitution_fails_restart(self):
        with tempfile.TemporaryDirectory() as td:
            old, _ = authority(); path = Path(td) / "db"; AsymmetricRecoveryCustody(path, old)
            q = sqlite3.connect(path)
            q.execute("UPDATE provider_recovery_public_authorities SET threshold=1")
            q.commit(); q.close()
            with self.assertRaises(CustodySubstitution):
                AsymmetricRecoveryCustody(path, old)


if __name__ == "__main__":
    unittest.main()
