import sqlite3
import tempfile
import unittest
from pathlib import Path

from experiments.asymmetric_break_glass_history.final_supported import (
    SupportedFencedAsymmetricBreakGlassLedger,
)
from experiments.asymmetric_break_glass_history.suffix import (
    AsymmetricBreakGlassError,
    PublicRecoveryRotationError,
    SupportedAsymmetricBreakGlassLedger,
)
from experiments.asymmetric_provider_history.protocol import GenerationSigner
from experiments.provider_threshold_rotation.enablement import ThresholdEnablement
from experiments.provider_threshold_rotation.protocol import Signature, ThresholdNotMet, mac
from experiments.provider_recovery_authority_lifecycle.asymmetric_custody import (
    CustodyThresholdNotMet,
)
from experiments.provider_recovery_authority_lifecycle.custody_break_glass import (
    custody_enablement_payload,
)
from experiments.provider_recovery_authority_lifecycle.tests.test_public_custody_supported import (
    attested,
    authority,
    public_recovery,
    public_signatures,
    recovery,
    signatures,
)


def migration_root_signatures(ledger, payload):
    root = ledger.rotation_authority.current()
    return tuple(
        Signature(signer_id, mac(bytes.fromhex(key_hex), payload))
        for signer_id, key_hex in list(root.keys.items())[: root.threshold]
    )


class AsymmetricSuffixIntegrationTests(unittest.TestCase):
    def make_ledger(self, path):
        signer = GenerationSigner.from_seed("anchor-A", 1, b"A" * 32)
        _, a1 = attested(1, b"hmac-1")
        root, root_raw = authority()
        rec, rec_raw = recovery()
        public, public_signers = public_recovery()
        base = ThresholdEnablement(
            signer.public.generation_id, 1, root.authority_id, 1, 1, ()
        )
        enable = ThresholdEnablement(
            base.start_provider_generation_id,
            1,
            root.authority_id,
            1,
            1,
            signatures(root_raw, base.payload, 2),
        )
        enable_payload = custody_enablement_payload(root, rec, public)
        ledger = SupportedAsymmetricBreakGlassLedger(
            path,
            a1,
            signer.public,
            signer,
            root,
            enable,
            rec.recovery,
            public,
            custody_enablement_signatures=public_signatures(
                public_signers, enable_payload, 3
            ),
        )
        return (
            ledger,
            signer,
            root,
            root_raw,
            rec,
            rec_raw,
            public,
            public_signers,
            enable,
        )

    def migrate(self, ledger, public_signers):
        payload = ledger.migration_guard.payload()
        return ledger.migration_guard.establish(
            public_signatures(public_signers, payload, 3),
            migration_root_signatures(ledger, payload),
        )

    def test_post_cutoff_recovery_uses_only_asymmetric_proof_and_restarts_without_hmac_recovery(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            (
                ledger,
                signer,
                root1,
                _,
                _,
                _,
                public1,
                public_signers,
                enable,
            ) = self.make_ledger(path)
            self.migrate(ledger, public_signers)
            root2, _ = authority(2, 2, "asymmetric")
            payload = ledger.asymmetric_recovery_payload(root2)
            out = ledger.recover_rotation_authority_asymmetric(
                root2, public_signatures(public_signers, payload, 3)
            )
            self.assertEqual(out["new_rotation_authority_id"], root2.authority_id)
            q = sqlite3.connect(path)
            self.assertEqual(
                q.execute(
                    "SELECT COUNT(*) FROM provider_rotation_recovery_transitions"
                ).fetchone()[0],
                0,
            )
            self.assertEqual(
                q.execute(
                    "SELECT COUNT(*) FROM provider_asymmetric_break_glass_proofs"
                ).fetchone()[0],
                1,
            )
            self.assertTrue(
                all(
                    row[0] == "{}"
                    for row in q.execute(
                        "SELECT keys_json FROM provider_rotation_recovery_authorities"
                    ).fetchall()
                )
            )
            self.assertTrue(
                all(
                    row[0] == "{}"
                    for row in q.execute(
                        "SELECT keys_json FROM provider_recovery_lifecycle_authorities"
                    ).fetchall()
                )
            )
            q.close()
            restarted = SupportedAsymmetricBreakGlassLedger(
                path,
                ledger.attested,
                signer.public,
                signer,
                root1,
                enable,
                None,
                public1,
            )
            self.assertTrue(restarted.verify_durable())
            self.assertFalse(hasattr(restarted, "recovery_lifecycle"))
            self.assertFalse(hasattr(restarted, "recovery"))
            self.assertEqual(
                restarted.rotation_authority.current().authority_id,
                root2.authority_id,
            )

    def test_hmac_compatibility_entry_points_are_blocked_after_migration(self):
        with tempfile.TemporaryDirectory() as td:
            ledger, _, _, _, _, _, _, public_signers, _ = self.make_ledger(
                Path(td) / "db"
            )
            self.migrate(ledger, public_signers)
            with self.assertRaises(AsymmetricBreakGlassError):
                ledger.recover_rotation_authority(None, ())
            with self.assertRaises(AsymmetricBreakGlassError):
                ledger.recover_rotation_authority_with_custody(None, (), ())
            with self.assertRaises(PublicRecoveryRotationError):
                ledger.rotate_recovery_authority_with_custody(None)

    def test_asymmetric_recovery_requires_current_public_threshold(self):
        with tempfile.TemporaryDirectory() as td:
            ledger, _, _, _, _, _, _, public_signers, _ = self.make_ledger(
                Path(td) / "db"
            )
            self.migrate(ledger, public_signers)
            root2, _ = authority(2, 2, "threshold")
            payload = ledger.asymmetric_recovery_payload(root2)
            with self.assertRaises(CustodyThresholdNotMet):
                ledger.recover_rotation_authority_asymmetric(
                    root2, public_signatures(public_signers, payload, 1)
                )

    def test_public_recovery_rotation_requires_root_coauthorization(self):
        with tempfile.TemporaryDirectory() as td:
            (
                ledger,
                _,
                _,
                root_raw,
                _,
                _,
                _,
                public1_signers,
                _,
            ) = self.make_ledger(Path(td) / "db")
            self.migrate(ledger, public1_signers)
            public2, public2_signers = public_recovery(2, 2, "public-new")
            payload = ledger.public_recovery_rotation_payload(public2)
            with self.assertRaises(ThresholdNotMet):
                ledger.rotate_public_recovery_authority(
                    public2,
                    public_signatures(public1_signers, payload, 3),
                    public_signatures(public2_signers, payload, 3),
                    signatures(root_raw, payload, 1),
                )

    def test_old_public_signers_cannot_authorize_after_public_only_rotation(self):
        with tempfile.TemporaryDirectory() as td:
            (
                ledger,
                _,
                _,
                root_raw,
                _,
                _,
                _,
                old_public_signers,
                _,
            ) = self.make_ledger(Path(td) / "db")
            self.migrate(ledger, old_public_signers)
            ledger = SupportedFencedAsymmetricBreakGlassLedger.from_existing(ledger)
            public2, public2_signers = public_recovery(2, 2, "public-new")
            rotate_payload = ledger.public_recovery_rotation_payload(public2)
            ledger.rotate_public_recovery_authority(
                public2,
                public_signatures(old_public_signers, rotate_payload, 3),
                public_signatures(public2_signers, rotate_payload, 3),
                signatures(root_raw, rotate_payload, 2),
            )
            root2, _ = authority(2, 2, "after-public-recovery-rotation")
            payload = ledger.asymmetric_recovery_payload(root2)
            with self.assertRaises(CustodyThresholdNotMet):
                ledger.recover_rotation_authority_asymmetric(
                    root2, public_signatures(old_public_signers, payload, 3)
                )
            ledger.recover_rotation_authority_asymmetric(
                root2, public_signatures(public2_signers, payload, 3)
            )
            self.assertTrue(ledger.verify_durable())

    def test_asymmetric_proof_tamper_fails_restart(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            ledger, signer, root1, _, _, _, public1, public_signers, enable = (
                self.make_ledger(path)
            )
            self.migrate(ledger, public_signers)
            root2, _ = authority(2, 2, "tamper")
            payload = ledger.asymmetric_recovery_payload(root2)
            ledger.recover_rotation_authority_asymmetric(
                root2, public_signatures(public_signers, payload, 3)
            )
            q = sqlite3.connect(path)
            q.execute(
                "UPDATE provider_asymmetric_break_glass_proofs SET public_signatures_json='[]'"
            )
            q.commit()
            q.close()
            with self.assertRaises(Exception):
                SupportedAsymmetricBreakGlassLedger(
                    path,
                    ledger.attested,
                    signer.public,
                    signer,
                    root1,
                    enable,
                    None,
                    public1,
                )

    def test_exactly_one_root_proof_type_is_required(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            ledger, _, _, _, _, _, _, public_signers, _ = self.make_ledger(path)
            self.migrate(ledger, public_signers)
            root2, _ = authority(2, 2, "count")
            payload = ledger.asymmetric_recovery_payload(root2)
            ledger.recover_rotation_authority_asymmetric(
                root2, public_signatures(public_signers, payload, 3)
            )
            q = sqlite3.connect(path)
            q.execute(
                "INSERT INTO provider_rotation_authority_transitions VALUES(?,?,?,?,?)",
                (
                    root2.authority_id,
                    ledger.rotation_authority.bootstrap.authority_id,
                    "0" * 64,
                    "[]",
                    "[]",
                ),
            )
            q.commit()
            q.close()
            with self.assertRaises(Exception):
                ledger.verify_durable()

    def test_verify_durable_holds_write_fence_across_lower_verifiers(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            ledger, *rest = self.make_ledger(path)
            public_signers = rest[-2]
            self.migrate(ledger, public_signers)
            observed = []
            original = ledger.public_recovery_custody.verify_durable

            def probed():
                result = original()
                q = sqlite3.connect(path, timeout=0)
                try:
                    q.execute("BEGIN IMMEDIATE")
                except sqlite3.OperationalError:
                    observed.append("blocked")
                else:
                    observed.append("writable")
                    q.rollback()
                finally:
                    q.close()
                return result

            ledger.public_recovery_custody.verify_durable = probed
            self.assertTrue(ledger.verify_durable())
            self.assertTrue(observed)
            self.assertTrue(all(value == "blocked" for value in observed))


if __name__ == "__main__":
    unittest.main()
