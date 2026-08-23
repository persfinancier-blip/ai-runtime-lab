import hashlib
import sqlite3
import tempfile
import threading
import unittest
from pathlib import Path

from experiments.anchor_attestation.protocol import AttestationVerifier, AttestedCatchup, ProviderIdentity, SignedAnchorProvider
from experiments.asymmetric_provider_history.protocol import GenerationSigner
from experiments.provider_threshold_rotation.enablement import ThresholdEnablement
from experiments.provider_threshold_rotation.protocol import RotationAuthority, Signature, ThresholdNotMet, key_id, mac
from experiments.provider_rotation_recovery.protocol import RecoveryAuthority
from experiments.provider_recovery_authority_lifecycle.asymmetric_custody import (
    CustodySubstitution,
    PublicRecoveryAuthority,
    RecoverySigner,
)
from experiments.provider_recovery_authority_lifecycle.protocol import VersionedRecoveryAuthority
from experiments.provider_recovery_authority_lifecycle.public_custody_supported import (
    CustodyBindingError,
    SupportedPublicRecoveryAuthorityLifecycleLedger,
)


def authority(version=1, generation=1, prefix="rot"):
    raw = [f"{prefix}-{version}-{generation}-{i}".encode() for i in range(3)]
    return RotationAuthority(
        "provider-rotation", version, generation, 2, {key_id(k): k.hex() for k in raw}
    ), raw


def recovery(version=1, generation=1, prefix="recovery"):
    raw = [f"{prefix}-{version}-{generation}-{i}".encode() for i in range(4)]
    return VersionedRecoveryAuthority(
        version,
        RecoveryAuthority(
            "provider-rotation-recovery",
            generation,
            3,
            {key_id(k): k.hex() for k in raw},
        ),
    ), raw


def public_recovery(version=1, generation=1, prefix="public-recovery"):
    signers = [
        RecoverySigner.from_seed(hashlib.sha256(f"{prefix}-{version}-{generation}-{i}".encode()).digest())
        for i in range(4)
    ]
    authority = PublicRecoveryAuthority(
        "provider-rotation-recovery",
        version,
        generation,
        3,
        {s.signer_id: s.public_key_hex for s in signers},
    )
    return authority, signers


def signatures(raw, payload, count):
    return tuple(Signature(key_id(k), mac(k, payload)) for k in raw[:count])


def public_signatures(signers, payload, count):
    return tuple(s.sign(payload) for s in signers[:count])


def attested(generation, key, position=0):
    provider = SignedAnchorProvider("anchor-A", generation, key, value=position)
    verifier = AttestationVerifier(
        {("anchor-A", generation): key}, ProviderIdentity("anchor-A", generation)
    )
    return provider, AttestedCatchup(provider, verifier)


class PublicCustodySupportedTests(unittest.TestCase):
    def make_ledger(self, path):
        signer = GenerationSigner.from_seed("anchor-A", 1, b"A" * 32)
        provider, a1 = attested(1, b"hmac-1")
        root, root_raw = authority()
        rec, rec_raw = recovery()
        public, public_signers = public_recovery()
        base = ThresholdEnablement(signer.public.generation_id, 1, root.authority_id, 1, 1, ())
        enable = ThresholdEnablement(
            base.start_provider_generation_id,
            1,
            root.authority_id,
            1,
            1,
            signatures(root_raw, base.payload, 2),
        )
        ledger = SupportedPublicRecoveryAuthorityLifecycleLedger(
            path,
            a1,
            signer.public,
            signer,
            root,
            enable,
            rec.recovery,
            public,
        )
        return provider, ledger, signer, root, root_raw, rec, rec_raw, public, public_signers, enable

    def rotate(self, ledger, root_raw, rec1_raw, rec2, rec2_raw, public2, public1_signers, public2_signers):
        symmetric_payload, public_payload = ledger.recovery_custody_rotation_payloads(rec2, public2)
        return ledger.rotate_recovery_authority_with_custody(
            rec2,
            public2,
            signatures(rec1_raw, symmetric_payload, 3),
            signatures(rec2_raw, symmetric_payload, 3),
            signatures(root_raw, symmetric_payload, 2),
            public_signatures(public1_signers, public_payload, 3),
            public_signatures(public2_signers, public_payload, 3),
        )

    def test_bootstrap_and_restart_bind_all_three_recovery_heads(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            _, ledger, signer, root, _, rec, _, public, _, enable = self.make_ledger(path)
            self.assertTrue(ledger.verify_durable())
            restarted = SupportedPublicRecoveryAuthorityLifecycleLedger(
                path, ledger.attested, signer.public, signer, root, enable, rec.recovery, public
            )
            self.assertTrue(restarted.verify_durable())

    def test_rotation_advances_symmetric_lab084_and_public_heads_atomically(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            _, ledger, _, _, root_raw, _, rec1_raw, _, public1_signers, _ = self.make_ledger(path)
            rec2, rec2_raw = recovery(2, 2, "recovery-new")
            public2, public2_signers = public_recovery(2, 2, "public-new")
            out = self.rotate(
                ledger, root_raw, rec1_raw, rec2, rec2_raw, public2, public1_signers, public2_signers
            )
            self.assertEqual(out["symmetric_authority_id"], rec2.authority_id)
            self.assertEqual(out["public_authority_id"], public2.authority_id)
            self.assertTrue(ledger.verify_durable())

    def test_metadata_mismatch_fails_before_any_head_moves(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            _, ledger, _, _, root_raw, rec1, rec1_raw, public1, public1_signers, _ = self.make_ledger(path)
            rec2, rec2_raw = recovery(2, 2, "recovery-new")
            bad_public, bad_signers = public_recovery(2, 3, "bad-public")
            before = ledger.recovery_lifecycle.current().authority_id
            with self.assertRaises(CustodyBindingError):
                self.rotate(ledger, root_raw, rec1_raw, rec2, rec2_raw, bad_public, public1_signers, bad_signers)
            self.assertEqual(ledger.recovery_lifecycle.current().authority_id, before)
            self.assertEqual(before, rec1.authority_id)
            self.assertEqual(ledger.public_recovery_custody.historical(public1.authority_id).authority_id, public1.authority_id)

    def test_plain_symmetric_rotation_is_blocked_on_supported_custody_surface(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            _, ledger, _, _, _, _, _, _, _, _ = self.make_ledger(path)
            with self.assertRaises(CustodyBindingError):
                ledger.rotate_recovery_authority(None, (), (), ())

    def test_public_head_rollback_is_detected_on_restart(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            _, ledger, signer, root, root_raw, rec1, rec1_raw, public1, public1_signers, enable = self.make_ledger(path)
            rec2, rec2_raw = recovery(2, 2, "recovery-new")
            public2, public2_signers = public_recovery(2, 2, "public-new")
            self.rotate(ledger, root_raw, rec1_raw, rec2, rec2_raw, public2, public1_signers, public2_signers)
            q = sqlite3.connect(path)
            q.execute(
                "UPDATE provider_recovery_public_head SET authority_id=?,version=?,generation=? WHERE singleton=1",
                (public1.authority_id, public1.version, public1.generation),
            )
            q.commit(); q.close()
            with self.assertRaises((CustodySubstitution, CustodyBindingError)):
                SupportedPublicRecoveryAuthorityLifecycleLedger(
                    path, ledger.attested, signer.public, signer, root, enable, rec1.recovery, public1
                )

    def test_binding_row_substitution_is_detected(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            _, ledger, _, _, _, _, _, _, _, _ = self.make_ledger(path)
            q = sqlite3.connect(path)
            q.execute("UPDATE provider_recovery_custody_bindings SET generation=999")
            q.commit(); q.close()
            with self.assertRaises(CustodyBindingError):
                ledger.verify_durable()

    def test_root_recovery_races_custody_rotation_and_exactly_one_successor_wins(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            _, ledger, _, root1, root1_raw, rec1, rec1_raw, _, public1_signers, _ = self.make_ledger(path)
            root2, _ = authority(2, 2, "recovered")
            recovery_intent = ledger.recovery.make_intent(root1, root2, rec1.recovery)
            recovery_sigs = signatures(rec1_raw, recovery_intent.payload, 3)

            rec2, rec2_raw = recovery(2, 2, "recovery-new")
            public2, public2_signers = public_recovery(2, 2, "public-new")
            symmetric_payload, public_payload = ledger.recovery_custody_rotation_payloads(rec2, public2)
            rotate_args = (
                rec2,
                public2,
                signatures(rec1_raw, symmetric_payload, 3),
                signatures(rec2_raw, symmetric_payload, 3),
                signatures(root1_raw, symmetric_payload, 2),
                public_signatures(public1_signers, public_payload, 3),
                public_signatures(public2_signers, public_payload, 3),
            )

            gate = threading.Barrier(3)
            outcomes = []
            lock = threading.Lock()

            def run_rotation():
                gate.wait()
                try:
                    ledger.rotate_recovery_authority_with_custody(*rotate_args)
                    result = "rotation"
                except Exception as exc:
                    result = type(exc).__name__
                with lock:
                    outcomes.append(result)

            def run_recovery():
                gate.wait()
                try:
                    ledger.recover_rotation_authority(root2, recovery_sigs)
                    result = "recovery"
                except Exception as exc:
                    result = type(exc).__name__
                with lock:
                    outcomes.append(result)

            threads = [threading.Thread(target=run_rotation), threading.Thread(target=run_recovery)]
            for thread in threads:
                thread.start()
            gate.wait()
            for thread in threads:
                thread.join(10)
            self.assertTrue(all(not thread.is_alive() for thread in threads))
            self.assertEqual(sum(item in {"rotation", "recovery"} for item in outcomes), 1, outcomes)
            self.assertTrue(ledger.verify_durable())


if __name__ == "__main__":
    unittest.main()
