import sqlite3
import tempfile
import unittest
from pathlib import Path

from experiments.asymmetric_break_glass_history.migration_guard import (
    AuthenticatedBreakGlassMigrationGuard,
)
from experiments.asymmetric_break_glass_history.suffix import (
    SupportedAsymmetricBreakGlassLedger,
)
from experiments.asymmetric_provider_history.protocol import GenerationSigner
from experiments.provider_threshold_rotation.enablement import ThresholdEnablement
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


class ScrubbedLegacyPrefixIntegrationTests(unittest.TestCase):
    def test_scrubbed_legacy_prefix_and_asymmetric_suffix_restart_together(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            signer = GenerationSigner.from_seed("anchor-A", 1, b"A" * 32)
            _, a1 = attested(1, b"hmac-1")
            root1, root_raw = authority()
            rec1, rec1_raw = recovery()
            public1, public_signers = public_recovery()
            base = ThresholdEnablement(
                signer.public.generation_id, 1, root1.authority_id, 1, 1, ()
            )
            enable = ThresholdEnablement(
                base.start_provider_generation_id,
                1,
                root1.authority_id,
                1,
                1,
                signatures(root_raw, base.payload, 2),
            )
            enable_payload = custody_enablement_payload(root1, rec1, public1)
            legacy = SupportedRecoveryCustodyLedger(
                path,
                a1,
                signer.public,
                signer,
                root1,
                enable,
                rec1.recovery,
                public1,
                custody_enablement_signatures=public_signatures(
                    public_signers, enable_payload, 3
                ),
            )
            root2, _ = authority(2, 2, "legacy")
            legacy_intent = legacy.recovery.make_intent(root1, root2, rec1.recovery)
            custody = legacy.break_glass_custody_payload(root2)
            legacy.recover_rotation_authority_with_custody(
                root2,
                public_signatures(public_signers, custody, 3),
                signatures(rec1_raw, legacy_intent.payload, 3),
            )
            guard = AuthenticatedBreakGlassMigrationGuard(legacy)
            guard.establish(public_signatures(public_signers, guard.payload(), 3))

            q = sqlite3.connect(path)
            self.assertEqual(
                q.execute(
                    "SELECT signatures_json FROM provider_rotation_recovery_transitions"
                ).fetchall(),
                [("[]",)],
            )
            q.close()

            migrated = SupportedAsymmetricBreakGlassLedger(
                path,
                legacy.attested,
                signer.public,
                signer,
                root1,
                enable,
                rec1.recovery,
                public1,
            )
            root3, _ = authority(3, 3, "asymmetric")
            payload = migrated.asymmetric_recovery_payload(root3)
            migrated.recover_rotation_authority_asymmetric(
                root3, public_signatures(public_signers, payload, 3)
            )
            self.assertTrue(migrated.verify_durable())

            restarted = SupportedAsymmetricBreakGlassLedger(
                path,
                migrated.attested,
                signer.public,
                signer,
                root1,
                enable,
                rec1.recovery,
                public1,
            )
            self.assertTrue(restarted.verify_durable())
            self.assertEqual(
                restarted.rotation_authority.current().authority_id,
                root3.authority_id,
            )


if __name__ == "__main__":
    unittest.main()
