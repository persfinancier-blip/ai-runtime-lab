import hashlib
import tempfile
import unittest
from pathlib import Path

from experiments.provider_threshold_rotation.enablement import (
    ThresholdEnablement,
    verify_enablement,
)
from experiments.provider_threshold_rotation.protocol import (
    DurableRotationAuthority,
    ProviderRotationIntent,
    RotationAuthority,
    Signature,
    ThresholdProof,
    key_id,
    mac,
    verify_threshold,
)


def authority(name="root", version=1, generation=1, threshold=2, prefix="k", revoked=()):
    raw = [hashlib.sha256(f"{prefix}-{i}".encode()).digest() for i in range(3)]
    keys = {key_id(key): key.hex() for key in raw}
    return RotationAuthority(name, version, generation, threshold, keys, tuple(revoked)), raw


def valid(key, payload):
    return Signature(key_id(key), mac(key, payload))


def invalid(key):
    return Signature(key_id(key), "0" * 64)


class SignerNoiseTests(unittest.TestCase):
    def test_provider_threshold_invalid_known_signer_does_not_consume_later_valid_signature(self):
        root, raw = authority()
        intent = ProviderRotationIntent(
            "anchor-A", "a" * 64, "b" * 64, root.authority_id, root.version, root.generation
        )
        proof = ThresholdProof(
            intent.intent_digest,
            root.authority_id,
            root.version,
            root.generation,
            (invalid(raw[0]), valid(raw[0], intent.payload), valid(raw[1], intent.payload)),
        )
        self.assertEqual(
            verify_threshold(root, intent, proof),
            tuple(sorted((key_id(raw[0]), key_id(raw[1])))),
        )

    def test_enablement_invalid_known_signer_does_not_consume_later_valid_signature(self):
        root, raw = authority()
        unsigned = ThresholdEnablement("a" * 64, 1, root.authority_id, 1, 1, ())
        enablement = ThresholdEnablement(
            unsigned.start_provider_generation_id,
            unsigned.start_provider_generation,
            unsigned.authority_id,
            unsigned.authority_version,
            unsigned.authority_generation,
            (invalid(raw[0]), valid(raw[0], unsigned.payload), valid(raw[1], unsigned.payload)),
        )
        self.assertEqual(
            verify_enablement(root, enablement),
            tuple(sorted((key_id(raw[0]), key_id(raw[1])))),
        )

    def test_authority_rotation_invalid_known_signer_does_not_consume_later_valid_signature(self):
        old, old_raw = authority(prefix="old")
        new, new_raw = authority(version=2, generation=2, prefix="new")
        payload = DurableRotationAuthority.authority_rotation_payload(old, new)
        with tempfile.TemporaryDirectory() as td:
            durable = DurableRotationAuthority(Path(td) / "db", old)
            result = durable.rotate_authority(
                new,
                (invalid(old_raw[0]), valid(old_raw[0], payload), valid(old_raw[1], payload)),
                (valid(new_raw[0], payload), valid(new_raw[1], payload)),
            )
        self.assertEqual(
            result["old_signers"],
            tuple(sorted((key_id(old_raw[0]), key_id(old_raw[1])))),
        )

    def test_restart_verifier_invalid_known_signer_noise_does_not_break_valid_history(self):
        old, old_raw = authority(prefix="old")
        new, new_raw = authority(version=2, generation=2, prefix="new")
        payload = DurableRotationAuthority.authority_rotation_payload(old, new)
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            durable = DurableRotationAuthority(path, old)
            durable.rotate_authority(
                new,
                (valid(old_raw[0], payload), valid(old_raw[1], payload)),
                (valid(new_raw[0], payload), valid(new_raw[1], payload)),
            )
            q = durable._con()
            try:
                q.execute("BEGIN IMMEDIATE")
                noisy = (
                    invalid(old_raw[0]),
                    valid(old_raw[0], payload),
                    valid(old_raw[1], payload),
                )
                q.execute(
                    "UPDATE provider_rotation_authority_transitions SET old_signatures_json=? WHERE new_authority_id=?",
                    (durable._encode_signatures(noisy), new.authority_id),
                )
                q.commit()
            finally:
                q.close()
            q = durable._con()
            try:
                self.assertEqual(
                    durable.verify_durable_locked(q, ()).authority_id,
                    new.authority_id,
                )
            finally:
                q.close()

    def test_duplicate_valid_signature_counts_once(self):
        root, raw = authority()
        intent = ProviderRotationIntent(
            "anchor-A", "a" * 64, "b" * 64, root.authority_id, root.version, root.generation
        )
        sig0 = valid(raw[0], intent.payload)
        proof = ThresholdProof(
            intent.intent_digest,
            root.authority_id,
            root.version,
            root.generation,
            (sig0, sig0, valid(raw[1], intent.payload)),
        )
        self.assertEqual(len(verify_threshold(root, intent, proof)), 2)

    def test_revoked_and_unknown_noise_do_not_inflate_or_poison_quorum(self):
        base, raw = authority()
        revoked_id = key_id(raw[2])
        root = RotationAuthority(
            base.authority_name, base.version, base.generation, 2, base.keys, (revoked_id,)
        )
        intent = ProviderRotationIntent(
            "anchor-A", "a" * 64, "b" * 64, root.authority_id, root.version, root.generation
        )
        unknown_key = hashlib.sha256(b"unknown").digest()
        proof = ThresholdProof(
            intent.intent_digest,
            root.authority_id,
            root.version,
            root.generation,
            (
                Signature(key_id(unknown_key), mac(unknown_key, intent.payload)),
                valid(raw[2], intent.payload),
                invalid(raw[0]),
                valid(raw[0], intent.payload),
                valid(raw[1], intent.payload),
            ),
        )
        self.assertEqual(
            verify_threshold(root, intent, proof),
            tuple(sorted((key_id(raw[0]), key_id(raw[1])))),
        )


if __name__ == "__main__":
    unittest.main()
