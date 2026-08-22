import sqlite3
import tempfile
import unittest
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from experiments.asymmetric_provider_history.protocol import (
    AsymmetricProviderHistory,
    CurrentGenerationRequired,
    GenerationSigner,
    HistoricalVerificationError,
    HistoryRollback,
    InvalidTransition,
    PublicGeneration,
    SignedReceipt,
    TransitionProof,
    UnsafeSymmetricHistory,
)


class Tests(unittest.TestCase):
    def setUp(self):
        self.s1 = GenerationSigner.from_seed("anchor-A", 1, b"\x01" * 32)
        self.s2 = GenerationSigner.from_seed("anchor-A", 2, b"\x02" * 32)

    def history(self, td):
        return AsymmetricProviderHistory(Path(td) / "history.db", self.s1.public)

    def test_historical_receipt_survives_rotation_using_public_material_only(self):
        with tempfile.TemporaryDirectory() as td:
            h = self.history(td)
            r1 = h.sign_current_receipt(self.s1, position=1, request_id="req-1")
            h.store_receipt(r1)
            h.rotate(self.s2.public, h.make_transition(self.s1, self.s2))
            self.assertEqual(h.load_receipt("req-1").generation, 1)
            self.assertEqual(h.current().generation, 2)

    def test_durable_database_contains_public_keys_not_private_seeds(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "history.db"
            h = AsymmetricProviderHistory(path, self.s1.public)
            h.rotate(self.s2.public, h.make_transition(self.s1, self.s2))
            raw = path.read_bytes()
            self.assertNotIn(b"\x01" * 32, raw)
            self.assertNotIn(b"\x02" * 32, raw)
            self.assertEqual([r[2] for r in h.durable_public_rows()], [
                self.s1.public.public_key_hex,
                self.s2.public.public_key_hex,
            ])

    def test_public_key_has_no_signing_operation(self):
        public = self.s1.public.public_key
        self.assertIsInstance(public, Ed25519PublicKey)
        self.assertFalse(hasattr(public, "sign"))

    def test_old_signer_cannot_create_new_receipt_after_rotation(self):
        with tempfile.TemporaryDirectory() as td:
            h = self.history(td)
            h.rotate(self.s2.public, h.make_transition(self.s1, self.s2))
            with self.assertRaises(CurrentGenerationRequired):
                h.sign_current_receipt(self.s1, position=2, request_id="old-new")
            r2 = h.sign_current_receipt(self.s2, position=2, request_id="req-2")
            h.store_receipt(r2)
            self.assertEqual(h.load_receipt("req-2").generation, 2)

    def test_forged_receipt_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            h = self.history(td)
            good = h.sign_current_receipt(self.s1, position=1, request_id="req")
            bad = SignedReceipt(
                good.provider_id, good.generation, good.position, good.request_id,
                good.kind, good.challenge, "00" * 64,
            )
            with self.assertRaises(HistoricalVerificationError):
                h.store_receipt(bad)

    def test_request_position_or_provider_rebinding_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            h = self.history(td)
            good = h.sign_current_receipt(self.s1, position=1, request_id="req")
            for bad in (
                SignedReceipt(good.provider_id, good.generation, 2, good.request_id, good.kind, good.challenge, good.signature),
                SignedReceipt(good.provider_id, good.generation, good.position, "other", good.kind, good.challenge, good.signature),
                SignedReceipt("anchor-B", good.generation, good.position, good.request_id, good.kind, good.challenge, good.signature),
            ):
                with self.assertRaises(HistoricalVerificationError):
                    h.store_receipt(bad)

    def test_transition_requires_old_and_new_signatures(self):
        with tempfile.TemporaryDirectory() as td:
            h = self.history(td)
            proof = h.make_transition(self.s1, self.s2)
            broken_old = TransitionProof(
                proof.provider_id, proof.old_generation_id, proof.new_generation_id,
                "00" * 64, proof.new_signature,
            )
            with self.assertRaises(HistoricalVerificationError):
                h.rotate(self.s2.public, broken_old)
        with tempfile.TemporaryDirectory() as td:
            h = self.history(td)
            proof = h.make_transition(self.s1, self.s2)
            broken_new = TransitionProof(
                proof.provider_id, proof.old_generation_id, proof.new_generation_id,
                proof.old_signature, "00" * 64,
            )
            with self.assertRaises(HistoricalVerificationError):
                h.rotate(self.s2.public, broken_new)

    def test_cross_provider_and_generation_gap_rejected(self):
        other = GenerationSigner.from_seed("anchor-B", 2, b"\x03" * 32)
        with self.assertRaises(InvalidTransition):
            AsymmetricProviderHistory.make_transition(self.s1, other)
        gap = GenerationSigner.from_seed("anchor-A", 3, b"\x04" * 32)
        with self.assertRaises(InvalidTransition):
            AsymmetricProviderHistory.make_transition(self.s1, gap)

    def test_public_key_substitution_fails_restart(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "history.db"
            h = AsymmetricProviderHistory(path, self.s1.public)
            q = sqlite3.connect(path)
            q.execute(
                "UPDATE asymmetric_provider_generations SET public_key_hex=? WHERE generation=1",
                (self.s2.public.public_key_hex,),
            )
            q.commit(); q.close()
            with self.assertRaises(HistoricalVerificationError):
                AsymmetricProviderHistory(path, self.s1.public)

    def test_transition_proof_corruption_fails_restart(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "history.db"
            h = AsymmetricProviderHistory(path, self.s1.public)
            h.rotate(self.s2.public, h.make_transition(self.s1, self.s2))
            q = sqlite3.connect(path)
            q.execute("UPDATE asymmetric_provider_transitions SET old_signature=?", ("00" * 64,))
            q.commit(); q.close()
            with self.assertRaises(HistoricalVerificationError):
                AsymmetricProviderHistory(path, self.s1.public)

    def test_head_rollback_fails_restart(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "history.db"
            h = AsymmetricProviderHistory(path, self.s1.public)
            h.rotate(self.s2.public, h.make_transition(self.s1, self.s2))
            q = sqlite3.connect(path)
            q.execute(
                "UPDATE asymmetric_provider_head SET generation_id=?,generation=1",
                (self.s1.public.generation_id,),
            )
            q.commit(); q.close()
            with self.assertRaises(HistoryRollback):
                AsymmetricProviderHistory(path, self.s1.public)

    def test_restart_verifies_mixed_generation_receipts(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "history.db"
            h = AsymmetricProviderHistory(path, self.s1.public)
            r1 = h.sign_current_receipt(self.s1, position=1, request_id="r1")
            h.store_receipt(r1)
            h.rotate(self.s2.public, h.make_transition(self.s1, self.s2))
            r2 = h.sign_current_receipt(self.s2, position=2, request_id="r2")
            h.store_receipt(r2)
            restarted = AsymmetricProviderHistory(path, self.s1.public)
            self.assertEqual(restarted.load_receipt("r1").generation, 1)
            self.assertEqual(restarted.load_receipt("r2").generation, 2)

    def test_corrupt_receipt_binding_and_signature_fail_restart(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "history.db"
            h = AsymmetricProviderHistory(path, self.s1.public)
            h.store_receipt(h.sign_current_receipt(self.s1, position=1, request_id="r1"))
            q = sqlite3.connect(path)
            q.execute("UPDATE asymmetric_provider_receipts SET stable_binding=?", ("0" * 64,))
            q.commit(); q.close()
            with self.assertRaises(HistoricalVerificationError):
                AsymmetricProviderHistory(path, self.s1.public)
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "history.db"
            h = AsymmetricProviderHistory(path, self.s1.public)
            h.store_receipt(h.sign_current_receipt(self.s1, position=1, request_id="r1"))
            q = sqlite3.connect(path)
            q.execute("UPDATE asymmetric_provider_receipts SET signature=?", ("00" * 64,))
            q.commit(); q.close()
            with self.assertRaises(HistoricalVerificationError):
                AsymmetricProviderHistory(path, self.s1.public)

    def test_bool_generation_and_noncanonical_signature_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            h = self.history(td)
            good = h.sign_current_receipt(self.s1, position=1, request_id="req")
            bad_generation = SignedReceipt(
                good.provider_id, True, good.position, good.request_id,
                good.kind, good.challenge, good.signature,
            )
            with self.assertRaises(HistoricalVerificationError):
                h.store_receipt(bad_generation)
            bad_signature = SignedReceipt(
                good.provider_id, good.generation, good.position, good.request_id,
                good.kind, good.challenge, good.signature.upper(),
            )
            with self.assertRaises(HistoricalVerificationError):
                h.store_receipt(bad_signature)

    def test_noncanonical_public_key_encoding_rejected(self):
        uppercase = PublicGeneration(
            self.s1.public.provider_id,
            self.s1.public.generation,
            self.s1.public.public_key_hex.upper(),
        )
        with self.assertRaises(HistoricalVerificationError):
            uppercase.validate()

    def test_unsafe_symmetric_history_can_sign_with_durable_historical_key(self):
        unsafe = UnsafeSymmetricHistory(b"durable-historical-hmac")
        new_effect = {"provider_id": "anchor-A", "generation": 1, "request_id": "evil-new"}
        forged = unsafe.sign(new_effect)
        self.assertTrue(unsafe.verify(new_effect, forged))


if __name__ == "__main__":
    unittest.main()
