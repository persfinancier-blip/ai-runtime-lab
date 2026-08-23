import sqlite3
import tempfile
import threading
import unittest
from pathlib import Path

from experiments.provider_threshold_rotation.protocol import ThresholdNotMet
from experiments.provider_recovery_authority_lifecycle.custody_break_glass import CustodyBreakGlassError
from experiments.provider_recovery_authority_lifecycle.final_supported import SupportedRecoveryCustodyLedger
from experiments.provider_recovery_authority_lifecycle.tests.test_public_custody_supported import (
    attested,
    authority,
    public_recovery,
    public_signatures,
    recovery,
    signatures,
)
from experiments.asymmetric_provider_history.protocol import GenerationSigner
from experiments.provider_threshold_rotation.enablement import ThresholdEnablement


class CustodyBreakGlassTests(unittest.TestCase):
    def make_ledger(self, path):
        signer = GenerationSigner.from_seed("anchor-A", 1, b"A" * 32)
        _, a1 = attested(1, b"hmac-1")
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
        ledger = SupportedRecoveryCustodyLedger(
            path, a1, signer.public, signer, root, enable, rec.recovery, public
        )
        return ledger, signer, root, root_raw, rec, rec_raw, public, public_signers, enable

    def recovery_material(self, ledger, root1, rec1, rec1_raw, public_signers):
        root2, _ = authority(2, 2, "recovered")
        legacy = ledger.recovery.make_intent(root1, root2, rec1.recovery)
        custody = ledger.break_glass_custody_payload(root2)
        return (
            root2,
            public_signatures(public_signers, custody, 3),
            signatures(rec1_raw, legacy.payload, 3),
        )

    def test_hmac_only_new_root_recovery_is_blocked(self):
        with tempfile.TemporaryDirectory() as td:
            ledger, _, root1, _, rec1, rec1_raw, _, _, _ = self.make_ledger(Path(td) / "db")
            root2, _ = authority(2, 2, "recovered")
            legacy = ledger.recovery.make_intent(root1, root2, rec1.recovery)
            with self.assertRaises(CustodyBreakGlassError):
                ledger.recover_rotation_authority(root2, signatures(rec1_raw, legacy.payload, 3))

    def test_public_only_cannot_create_unverifiable_compatibility_row(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            ledger, _, root1, _, rec1, rec1_raw, _, public_signers, _ = self.make_ledger(path)
            root2, public_sigs, _ = self.recovery_material(ledger, root1, rec1, rec1_raw, public_signers)
            with self.assertRaises(ThresholdNotMet):
                ledger.recover_rotation_authority_with_custody(root2, public_sigs, ())
            q = sqlite3.connect(path)
            self.assertEqual(q.execute("SELECT COUNT(*) FROM provider_rotation_recovery_transitions").fetchone()[0], 0)
            self.assertEqual(q.execute("SELECT COUNT(*) FROM provider_rotation_recovery_custody_proofs").fetchone()[0], 0)
            q.close()

    def test_combined_recovery_commits_both_proofs_and_restarts(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            ledger, signer, root1, _, rec1, rec1_raw, public1, public_signers, enable = self.make_ledger(path)
            root2, public_sigs, compatibility_sigs = self.recovery_material(
                ledger, root1, rec1, rec1_raw, public_signers
            )
            out = ledger.recover_rotation_authority_with_custody(root2, public_sigs, compatibility_sigs)
            self.assertEqual(out["new_authority_id"], root2.authority_id)
            q = sqlite3.connect(path)
            self.assertEqual(q.execute("SELECT COUNT(*) FROM provider_rotation_recovery_transitions").fetchone()[0], 1)
            self.assertEqual(q.execute("SELECT COUNT(*) FROM provider_rotation_recovery_custody_proofs").fetchone()[0], 1)
            q.close()
            restarted = SupportedRecoveryCustodyLedger(
                path, ledger.attested, signer.public, signer, root1, enable, rec1.recovery, public1
            )
            self.assertTrue(restarted.verify_durable())

    def test_missing_public_proof_fails_restart_verification(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            ledger, _, root1, _, rec1, rec1_raw, _, public_signers, _ = self.make_ledger(path)
            root2, public_sigs, compatibility_sigs = self.recovery_material(
                ledger, root1, rec1, rec1_raw, public_signers
            )
            ledger.recover_rotation_authority_with_custody(root2, public_sigs, compatibility_sigs)
            q = sqlite3.connect(path)
            q.execute("DELETE FROM provider_rotation_recovery_custody_proofs")
            q.commit(); q.close()
            with self.assertRaises(CustodyBreakGlassError):
                ledger.verify_durable()

    def test_recovery_and_custody_rotation_serialize_to_one_successor(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            ledger, _, root1, root1_raw, rec1, rec1_raw, _, public1_signers, _ = self.make_ledger(path)
            root2, public_recovery_sigs, compatibility_sigs = self.recovery_material(
                ledger, root1, rec1, rec1_raw, public1_signers
            )
            rec2, rec2_raw = recovery(2, 2, "recovery-new")
            public2, public2_signers = public_recovery(2, 2, "public-new")
            symmetric_payload, public_payload = ledger.recovery_custody_rotation_payloads(rec2, public2)
            rotation_args = (
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

            def rotate():
                gate.wait()
                try:
                    ledger.rotate_recovery_authority_with_custody(*rotation_args)
                    value = "rotation"
                except Exception as exc:
                    value = type(exc).__name__
                with lock:
                    outcomes.append(value)

            def recover():
                gate.wait()
                try:
                    ledger.recover_rotation_authority_with_custody(
                        root2, public_recovery_sigs, compatibility_sigs
                    )
                    value = "recovery"
                except Exception as exc:
                    value = type(exc).__name__
                with lock:
                    outcomes.append(value)

            threads = [threading.Thread(target=rotate), threading.Thread(target=recover)]
            for thread in threads:
                thread.start()
            gate.wait()
            for thread in threads:
                thread.join(10)
            self.assertTrue(all(not t.is_alive() for t in threads))
            self.assertEqual(sum(x in {"rotation", "recovery"} for x in outcomes), 1, outcomes)
            self.assertTrue(ledger.verify_durable())


if __name__ == "__main__":
    unittest.main()
