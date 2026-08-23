import sqlite3
import tempfile
import unittest
from pathlib import Path

from experiments.asymmetric_break_glass_history.migration_guard import (
    AuthenticatedBreakGlassMigrationGuard,
    LegacyHistoryChanged,
    MigrationGuardError,
    _digest,
    migration_payload,
)
from experiments.asymmetric_break_glass_history.suffix import (
    SupportedAsymmetricBreakGlassLedger,
)
from experiments.asymmetric_provider_history.protocol import GenerationSigner
from experiments.provider_threshold_rotation.enablement import ThresholdEnablement
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
        return ledger, signer, root, rec, rec_raw, public, public_signers, enable

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

    def test_threshold_signed_cutoff_binds_real_legacy_history_and_restarts(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            (
                ledger,
                signer,
                root1,
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
            payload = guard.payload()
            boundary = guard.establish(
                public_signatures(public_signers, payload, 3)
            )
            self.assertEqual(len(boundary), 64)
            # The old LAB-085 surface is no longer the supported restart boundary
            # because its HMAC break-glass verifier intentionally requires proof
            # bytes that migration has destroyed. Reopen through LAB-086 instead.
            restarted = SupportedAsymmetricBreakGlassLedger(
                path,
                ledger.attested,
                signer.public,
                signer,
                root1,
                enable,
                rec1.recovery,
                public1,
            )
            result = restarted.migration_guard.verify()
            self.assertEqual(result["boundary_digest"], boundary)

    def test_establish_atomically_scrubs_legacy_hmac_proof_bytes(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            ledger, _, root1, rec1, rec1_raw, _, public_signers, _ = self.make_ledger(path)
            self.compatibility_recovery(
                ledger, root1, rec1, rec1_raw, public_signers
            )
            guard = AuthenticatedBreakGlassMigrationGuard(ledger)
            guard.establish(public_signatures(public_signers, guard.payload(), 3))
            q = sqlite3.connect(path)
            rows = q.execute(
                "SELECT signatures_json FROM provider_rotation_recovery_transitions"
            ).fetchall()
            q.close()
            self.assertEqual(rows, [("[]",)])
            self.assertIsNotNone(guard.verify())

    def test_scrubbed_hmac_proof_bytes_cannot_reappear(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            ledger, _, root1, rec1, rec1_raw, _, public_signers, _ = self.make_ledger(path)
            self.compatibility_recovery(
                ledger, root1, rec1, rec1_raw, public_signers
            )
            guard = AuthenticatedBreakGlassMigrationGuard(ledger)
            guard.establish(public_signatures(public_signers, guard.payload(), 3))
            q = sqlite3.connect(path)
            q.execute(
                "UPDATE provider_rotation_recovery_transitions "
                "SET signatures_json='[{\"signer_id\":\"attacker\",\"signature\":\"00\"}]'"
            )
            q.commit()
            q.close()
            with self.assertRaises(MigrationGuardError):
                guard.verify()

    def test_cutoff_requires_current_public_threshold(self):
        with tempfile.TemporaryDirectory() as td:
            ledger, *_, public_signers, _ = self.make_ledger(Path(td) / "db")
            guard = AuthenticatedBreakGlassMigrationGuard(ledger)
            payload = guard.payload()
            with self.assertRaises(CustodyThresholdNotMet):
                guard.establish(public_signatures(public_signers, payload, 1))

    def test_stale_historical_recovery_quorum_cannot_authorize_cutoff(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            (
                ledger,
                _,
                root1,
                rec1,
                rec1_raw,
                public1,
                old_public_signers,
                _,
            ) = self.make_ledger(path)
            _, root_raw = authority()
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
            q = ledger._con()
            try:
                q.execute("BEGIN IMMEDIATE")
                legacy = guard._legacy_digest_locked(q, root1.version)
                payload = migration_payload(
                    legacy_digest=legacy,
                    cutoff_root=root1,
                    symmetric_authority_id=rec1.authority_id,
                    public_authority=public1,
                )
                boundary = _digest(payload)
                encoded = ledger.public_recovery_custody._encode_signatures(
                    public_signatures(old_public_signers, payload, 3)
                )
                q.execute(
                    "INSERT INTO provider_asymmetric_break_glass_boundary VALUES(1,?,?,?,?,?,?,?,?,?,?)",
                    (
                        legacy,
                        root1.authority_id,
                        root1.version,
                        root1.generation,
                        rec1.authority_id,
                        public1.authority_id,
                        public1.version,
                        public1.generation,
                        boundary,
                        encoded,
                    ),
                )
                q.commit()
            finally:
                q.close()
            with self.assertRaises(MigrationGuardError):
                guard.verify()

    def test_legacy_semantic_history_tamper_after_cutoff_is_detected(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            ledger, _, root1, rec1, rec1_raw, _, public_signers, _ = self.make_ledger(path)
            self.compatibility_recovery(
                ledger, root1, rec1, rec1_raw, public_signers
            )
            guard = AuthenticatedBreakGlassMigrationGuard(ledger)
            guard.establish(public_signatures(public_signers, guard.payload(), 3))
            q = sqlite3.connect(path)
            q.execute(
                "UPDATE provider_rotation_recovery_transitions SET intent_digest=?",
                ("0" * 64,),
            )
            q.commit()
            q.close()
            with self.assertRaises(LegacyHistoryChanged):
                guard.verify()

    def test_old_lab085_writer_cannot_append_hmac_recovery_after_cutoff(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            ledger, _, root1, rec1, rec1_raw, _, public_signers, _ = self.make_ledger(path)
            guard = AuthenticatedBreakGlassMigrationGuard(ledger)
            guard.establish(public_signatures(public_signers, guard.payload(), 3))
            root2, _ = authority(2, 2, "blocked-legacy")
            legacy = ledger.recovery.make_intent(root1, root2, rec1.recovery)
            custody = ledger.break_glass_custody_payload(root2)
            with self.assertRaises(sqlite3.DatabaseError):
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
            ledger, _, root1, rec1, rec1_raw, _, public_signers, _ = self.make_ledger(path)
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
