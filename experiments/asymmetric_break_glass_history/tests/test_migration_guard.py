import sqlite3
import tempfile
import unittest
from pathlib import Path

from experiments.asymmetric_break_glass_history.migration_guard import (
    AuthenticatedBreakGlassMigrationGuard,
    LegacyHistoryChanged,
    MigrationGuardError,
)
from experiments.asymmetric_break_glass_history.suffix import (
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
from experiments.provider_recovery_authority_lifecycle.final_supported import (
    SupportedRecoveryCustodyLedger,
)
from experiments.provider_recovery_authority_lifecycle.tests.test_public_custody_supported import (
    attested,
    authority,
    public_recovery,
    public_signatures,
    recovery,
    signatures,
)


def migration_root_signatures(ledger, payload, count=None):
    root = ledger.rotation_authority.current()
    count = root.threshold if count is None else count
    return tuple(
        Signature(signer_id, mac(bytes.fromhex(key_hex), payload))
        for signer_id, key_hex in list(root.keys.items())[:count]
    )


class MigrationGuardIntegrationTests(unittest.TestCase):
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
        ledger = SupportedRecoveryCustodyLedger(
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

    def compatibility_recovery(
        self, ledger, root1, rec1, rec1_raw, public_signers
    ):
        root2, _ = authority(2, 2, "legacy")
        legacy = ledger.recovery.make_intent(root1, root2, rec1.recovery)
        custody = ledger.break_glass_custody_payload(root2)
        ledger.recover_rotation_authority_with_custody(
            root2,
            public_signatures(public_signers, custody, 3),
            signatures(rec1_raw, legacy.payload, 3),
        )
        return root2

    def establish(self, guard, public_signers):
        payload = guard.payload()
        return guard.establish(
            public_signatures(public_signers, payload, 3),
            migration_root_signatures(guard.ledger, payload),
        )

    def test_threshold_signed_cutoff_restarts_without_recovery_hmac_material(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            (
                ledger,
                signer,
                root1,
                _,
                rec1,
                rec1_raw,
                public1,
                public_signers,
                enable,
            ) = self.make_ledger(path)
            self.compatibility_recovery(
                ledger, root1, rec1, rec1_raw, public_signers
            )
            guard = AuthenticatedBreakGlassMigrationGuard(ledger)
            boundary = self.establish(guard, public_signers)
            self.assertEqual(len(boundary), 64)
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
            result = restarted.migration_guard.verify()
            self.assertEqual(result["boundary_digest"], boundary)
            self.assertFalse(hasattr(restarted, "recovery"))
            self.assertFalse(hasattr(restarted, "recovery_lifecycle"))

    def test_establish_atomically_scrubs_recovery_hmac_keys_and_proofs(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            ledger, _, root1, _, rec1, rec1_raw, _, public_signers, _ = self.make_ledger(path)
            self.compatibility_recovery(
                ledger, root1, rec1, rec1_raw, public_signers
            )
            guard = AuthenticatedBreakGlassMigrationGuard(ledger)
            self.establish(guard, public_signers)
            q = sqlite3.connect(path)
            self.assertTrue(
                all(
                    value == "[]"
                    for (value,) in q.execute(
                        "SELECT signatures_json FROM provider_rotation_recovery_transitions"
                    ).fetchall()
                )
            )
            self.assertTrue(
                all(
                    value == "{}"
                    for (value,) in q.execute(
                        "SELECT keys_json FROM provider_rotation_recovery_authorities"
                    ).fetchall()
                )
            )
            self.assertTrue(
                all(
                    value == "{}"
                    for (value,) in q.execute(
                        "SELECT keys_json FROM provider_recovery_lifecycle_authorities"
                    ).fetchall()
                )
            )
            for column in (
                "old_signatures_json",
                "new_signatures_json",
                "root_signatures_json",
            ):
                self.assertTrue(
                    all(
                        value == "[]"
                        for (value,) in q.execute(
                            f"SELECT {column} FROM provider_recovery_lifecycle_transitions"
                        ).fetchall()
                    )
                )
            q.close()
            self.assertIsNotNone(guard.verify())

    def test_scrubbed_symmetric_material_cannot_reappear(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            ledger, _, root1, _, rec1, rec1_raw, _, public_signers, _ = self.make_ledger(path)
            self.compatibility_recovery(
                ledger, root1, rec1, rec1_raw, public_signers
            )
            guard = AuthenticatedBreakGlassMigrationGuard(ledger)
            self.establish(guard, public_signers)
            q = sqlite3.connect(path)
            # Ordinary DML is now denied by LAB-086. Drop exactly the relevant
            # trigger to model out-of-band durable corruption and prove the
            # verifier remains independently fail-closed.
            q.execute("DROP TRIGGER lab086_compat_recovery_authority_semantics_immutable")
            q.execute(
                "UPDATE provider_rotation_recovery_authorities SET keys_json=?",
                ('{"attacker":"00"}',),
            )
            q.commit()
            q.close()
            with self.assertRaises(MigrationGuardError):
                guard.verify()

    def test_cutoff_requires_current_public_threshold(self):
        with tempfile.TemporaryDirectory() as td:
            ledger, *rest = self.make_ledger(Path(td) / "db")
            public_signers = rest[-2]
            guard = AuthenticatedBreakGlassMigrationGuard(ledger)
            payload = guard.payload()
            with self.assertRaises(CustodyThresholdNotMet):
                guard.establish(
                    public_signatures(public_signers, payload, 1),
                    migration_root_signatures(ledger, payload),
                )

    def test_cutoff_requires_current_root_threshold(self):
        with tempfile.TemporaryDirectory() as td:
            ledger, *rest = self.make_ledger(Path(td) / "db")
            public_signers = rest[-2]
            guard = AuthenticatedBreakGlassMigrationGuard(ledger)
            payload = guard.payload()
            with self.assertRaises(ThresholdNotMet):
                guard.establish(
                    public_signatures(public_signers, payload, 3),
                    migration_root_signatures(ledger, payload, 1),
                )

    def test_stale_historical_public_quorum_cannot_authorize_cutoff(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            (
                ledger,
                _,
                _,
                root_raw,
                rec1,
                rec1_raw,
                _,
                old_public_signers,
                _,
            ) = self.make_ledger(path)
            rec2, rec2_raw = recovery(2, 2, "recovery-new")
            public2, public2_signers = public_recovery(2, 2, "public-new")
            symmetric_payload, public_payload = (
                ledger.recovery_custody_rotation_payloads(rec2, public2)
            )
            ledger.rotate_recovery_authority_with_custody(
                rec2,
                public2,
                signatures(rec1_raw, symmetric_payload, 3),
                signatures(rec2_raw, symmetric_payload, 3),
                signatures(root_raw, symmetric_payload, 2),
                public_signatures(old_public_signers, public_payload, 3),
                public_signatures(public2_signers, public_payload, 3),
            )
            guard = AuthenticatedBreakGlassMigrationGuard(ledger)
            payload = guard.payload()
            with self.assertRaises(CustodyThresholdNotMet):
                guard.establish(
                    public_signatures(old_public_signers, payload, 3),
                    migration_root_signatures(ledger, payload),
                )

    def test_root_coauthorization_is_reverified_after_restart(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            ledger, *rest = self.make_ledger(path)
            public_signers = rest[-2]
            guard = AuthenticatedBreakGlassMigrationGuard(ledger)
            self.establish(guard, public_signers)
            q = sqlite3.connect(path)
            q.execute("DROP TRIGGER lab086_migration_root_proof_is_immutable")
            q.execute(
                "UPDATE provider_asymmetric_break_glass_root_proof SET root_signatures_json='[]'"
            )
            q.commit()
            q.close()
            with self.assertRaises(ThresholdNotMet):
                guard.verify()

    def test_boundary_rebinding_cannot_reuse_old_root_proof(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            ledger, *rest = self.make_ledger(path)
            public_signers = rest[-2]
            guard = AuthenticatedBreakGlassMigrationGuard(ledger)
            self.establish(guard, public_signers)
            q = sqlite3.connect(path)
            q.execute("DROP TRIGGER lab086_migration_boundary_is_immutable")
            q.execute(
                "UPDATE provider_asymmetric_break_glass_boundary SET boundary_digest=?",
                ("0" * 64,),
            )
            q.commit()
            q.close()
            with self.assertRaises(MigrationGuardError):
                guard.verify()

    def test_legacy_semantic_history_tamper_after_cutoff_is_detected(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            ledger, _, root1, _, rec1, rec1_raw, _, public_signers, _ = self.make_ledger(path)
            self.compatibility_recovery(
                ledger, root1, rec1, rec1_raw, public_signers
            )
            guard = AuthenticatedBreakGlassMigrationGuard(ledger)
            self.establish(guard, public_signers)
            q = sqlite3.connect(path)
            q.execute("DROP TRIGGER lab086_legacy_recovery_transition_semantics_immutable")
            q.execute(
                "UPDATE provider_rotation_recovery_transitions SET intent_digest=?",
                ("0" * 64,),
            )
            q.commit()
            q.close()
            with self.assertRaises(LegacyHistoryChanged):
                guard.verify()

    def test_old_lab085_writer_cannot_extend_recovery_history_after_cutoff(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            ledger, _, root1, _, rec1, rec1_raw, _, public_signers, _ = self.make_ledger(path)
            guard = AuthenticatedBreakGlassMigrationGuard(ledger)
            self.establish(guard, public_signers)
            root2, _ = authority(2, 2, "blocked-legacy")
            with self.assertRaises(Exception):
                legacy = ledger.recovery.make_intent(root1, root2, rec1.recovery)
                custody = ledger.break_glass_custody_payload(root2)
                ledger.recover_rotation_authority_with_custody(
                    root2,
                    public_signatures(public_signers, custody, 3),
                    signatures(rec1_raw, legacy.payload, 3),
                )
            q = sqlite3.connect(path)
            self.assertEqual(
                q.execute(
                    "SELECT COUNT(*) FROM provider_rotation_recovery_transitions"
                ).fetchone()[0],
                0,
            )
            q.close()

    def test_sql_guard_is_inactive_before_authenticated_cutoff(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            ledger, _, root1, _, rec1, rec1_raw, _, public_signers, _ = self.make_ledger(path)
            AuthenticatedBreakGlassMigrationGuard(ledger)
            self.compatibility_recovery(
                ledger, root1, rec1, rec1_raw, public_signers
            )
            q = sqlite3.connect(path)
            self.assertEqual(
                q.execute(
                    "SELECT COUNT(*) FROM provider_rotation_recovery_transitions"
                ).fetchone()[0],
                1,
            )
            q.close()


if __name__ == "__main__":
    unittest.main()
