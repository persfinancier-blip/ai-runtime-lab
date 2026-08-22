import sqlite3
import tempfile
import unittest
from pathlib import Path

from experiments.anchor_attestation.protocol import (
    AttestationVerifier,
    AttestedCatchup,
    ProviderIdentity,
    SignedAnchorProvider,
)
from experiments.asymmetric_provider_history.protocol import GenerationSigner
from experiments.asymmetric_provider_history.integration import PendingRotationBlocked
from experiments.shared_anchor_intent_ledger.protocol import Intent
from experiments.provider_threshold_rotation.enablement import ThresholdEnablement
from experiments.provider_threshold_rotation.protocol import (
    InvalidAuthority,
    ProviderRotationIntent,
    RotationAuthority,
    Signature,
    ThresholdNotMet,
    key_id,
    mac,
)
from experiments.provider_threshold_rotation.supported import (
    SupportedThresholdAuthorizedAsymmetricProviderLedger,
)


def authority(version=1, generation=1, threshold=2, prefix="rot"):
    raw = [f"{prefix}-{version}-{generation}-{i}".encode() for i in range(3)]
    keys = {key_id(k): k.hex() for k in raw}
    return RotationAuthority("provider-rotation", version, generation, threshold, keys), raw


def signatures(raw, payload, count=2):
    return tuple(Signature(key_id(k), mac(k, payload)) for k in raw[:count])


def attested(generation, key, position=0):
    provider = SignedAnchorProvider("anchor-A", generation, key, value=position)
    verifier = AttestationVerifier(
        {("anchor-A", generation): key}, ProviderIdentity("anchor-A", generation)
    )
    return provider, AttestedCatchup(provider, verifier)


class SupportedIntegrationTests(unittest.TestCase):
    def make_ledger(self, path):
        signer1 = GenerationSigner.from_seed("anchor-A", 1, b"\x41" * 32)
        provider1, a1 = attested(1, b"hmac-1", 0)
        auth, auth_raw = authority()
        base = ThresholdEnablement(
            signer1.public.generation_id,
            1,
            auth.authority_id,
            auth.version,
            auth.generation,
            (),
        )
        enablement = ThresholdEnablement(
            base.start_provider_generation_id,
            base.start_provider_generation,
            base.authority_id,
            base.authority_version,
            base.authority_generation,
            signatures(auth_raw, base.payload),
        )
        ledger = SupportedThresholdAuthorizedAsymmetricProviderLedger(
            path, a1, signer1.public, signer1, auth, enablement
        )
        return provider1, ledger, signer1, auth, auth_raw, enablement

    def rotation_material(self, ledger, old_signer, auth_raw, generation=2, position=0):
        new_signer = GenerationSigner.from_seed(
            "anchor-A", generation, bytes([0x40 + generation]) * 32
        )
        proof = ledger.provider_history.make_transition(old_signer, new_signer)
        provider, new_attested = attested(generation, f"hmac-{generation}".encode(), position)
        current_auth = ledger.rotation_authority.current()
        intent = ProviderRotationIntent(
            "anchor-A",
            old_signer.public.generation_id,
            new_signer.public.generation_id,
            current_auth.authority_id,
            current_auth.version,
            current_auth.generation,
        )
        quorum = signatures(auth_raw, intent.payload)
        return provider, new_attested, new_signer, proof, quorum

    def test_quorum_authorized_rotation_and_restart(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "shared.db"
            _, ledger, s1, auth, raw, enablement = self.make_ledger(path)
            _, a2, s2, proof, quorum = self.rotation_material(ledger, s1, raw)
            ledger.rotate_provider(s2, proof, a2, quorum)
            self.assertEqual(ledger.provider_history.current().generation, 2)
            restarted = SupportedThresholdAuthorizedAsymmetricProviderLedger(
                path, a2, s1.public, s2, auth, enablement
            )
            self.assertTrue(restarted.verify_durable())

    def test_compromised_old_plus_attacker_new_without_quorum_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "shared.db"
            _, ledger, s1, _, raw, _ = self.make_ledger(path)
            _, a2, s2, proof, _ = self.rotation_material(ledger, s1, raw)
            with self.assertRaises(ThresholdNotMet):
                ledger.rotate_provider(s2, proof, a2, ())
            self.assertEqual(ledger.provider_history.current().generation, 1)
            q = sqlite3.connect(path)
            try:
                self.assertEqual(
                    q.execute("SELECT COUNT(*) FROM provider_rotation_threshold_proofs").fetchone()[0],
                    0,
                )
            finally:
                q.close()

    def test_prepared_intent_blocks_rotation_and_quorum_persistence(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "shared.db"
            _, ledger, s1, _, raw, _ = self.make_ledger(path)
            ledger.reserve(Intent("pending", "component-A", "migration", {"v": 1}))
            _, a2, s2, proof, quorum = self.rotation_material(ledger, s1, raw, position=0)
            with self.assertRaises(PendingRotationBlocked):
                ledger.rotate_provider(s2, proof, a2, quorum)
            q = sqlite3.connect(path)
            try:
                self.assertEqual(
                    q.execute("SELECT COUNT(*) FROM provider_rotation_threshold_proofs").fetchone()[0],
                    0,
                )
            finally:
                q.close()

    def test_authority_rotation_makes_old_provider_quorum_stale(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "shared.db"
            _, ledger, s1, old_auth, old_raw, _ = self.make_ledger(path)
            _, a2, s2, proof, old_quorum = self.rotation_material(ledger, s1, old_raw)
            new_auth, new_raw = authority(version=2, generation=2, prefix="rot-new")
            payload = ledger.rotation_authority.authority_rotation_payload(old_auth, new_auth)
            ledger.rotate_rotation_authority(
                new_auth, signatures(old_raw, payload), signatures(new_raw, payload)
            )
            with self.assertRaises(ThresholdNotMet):
                ledger.rotate_provider(s2, proof, a2, old_quorum)
            self.assertEqual(ledger.provider_history.current().generation, 1)

    def test_historical_receipt_survives_provider_rotation(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "shared.db"
            provider1, ledger, s1, auth, raw, enablement = self.make_ledger(path)
            intent = Intent("before-rotation", "component-A", "migration", {"v": 1})
            confirmed = ledger.execute(intent)
            self.assertEqual(confirmed.status, "CONFIRMED")
            old_receipt = ledger.provider_history.load_receipt(confirmed.request_id)
            _, a2, s2, proof, quorum = self.rotation_material(
                ledger, s1, raw, position=provider1.value
            )
            ledger.rotate_provider(s2, proof, a2, quorum)
            restarted = SupportedThresholdAuthorizedAsymmetricProviderLedger(
                path, a2, s1.public, s2, auth, enablement
            )
            loaded = restarted.provider_history.load_receipt(confirmed.request_id)
            self.assertEqual(loaded.stable_binding, old_receipt.stable_binding)
            self.assertTrue(restarted.verify_durable())

    def test_deleted_enablement_cannot_rebootstrap_after_threshold_transition(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "shared.db"
            _, ledger, s1, auth, raw, enablement = self.make_ledger(path)
            _, a2, s2, proof, quorum = self.rotation_material(ledger, s1, raw)
            ledger.rotate_provider(s2, proof, a2, quorum)
            q = sqlite3.connect(path)
            q.execute("DELETE FROM provider_rotation_threshold_enablement")
            q.commit()
            q.close()
            with self.assertRaises(Exception):
                SupportedThresholdAuthorizedAsymmetricProviderLedger(
                    path, a2, s1.public, s2, auth, enablement
                )

    def test_corrupted_threshold_proof_fails_restart(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "shared.db"
            _, ledger, s1, auth, raw, enablement = self.make_ledger(path)
            _, a2, s2, proof, quorum = self.rotation_material(ledger, s1, raw)
            ledger.rotate_provider(s2, proof, a2, quorum)
            q = sqlite3.connect(path)
            q.execute(
                "UPDATE provider_rotation_threshold_proofs SET signatures_json='[]'"
            )
            q.commit()
            q.close()
            with self.assertRaises(ThresholdNotMet):
                SupportedThresholdAuthorizedAsymmetricProviderLedger(
                    path, a2, s1.public, s2, auth, enablement
                )

    def test_noncanonical_authority_rejected_by_supported_surface(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "shared.db"
            signer = GenerationSigner.from_seed("anchor-A", 1, b"\x41" * 32)
            _, a1 = attested(1, b"hmac-1", 0)
            auth, raw = authority()
            sid, hx = next(iter(auth.keys.items()))
            bad_keys = dict(auth.keys)
            bad_keys[sid] = hx.upper()
            bad = RotationAuthority(
                auth.authority_name,
                auth.version,
                auth.generation,
                auth.threshold,
                bad_keys,
            )
            base = ThresholdEnablement(
                signer.public.generation_id,
                1,
                bad.authority_id,
                1,
                1,
                (),
            )
            with self.assertRaises(InvalidAuthority):
                SupportedThresholdAuthorizedAsymmetricProviderLedger(
                    path, a1, signer.public, signer, bad, base
                )


if __name__ == "__main__":
    unittest.main()
