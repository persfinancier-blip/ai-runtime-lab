import tempfile
import unittest
from pathlib import Path

from experiments.asymmetric_break_glass_history.tests.test_suffix import (
    AsymmetricSuffixIntegrationTests,
)
from experiments.provider_recovery_authority_lifecycle.asymmetric_custody import (
    custody_rotation_payload,
)
from experiments.provider_recovery_authority_lifecycle.tests.test_public_custody_supported import (
    public_recovery,
    public_signatures,
    signatures,
)


class UnfencedSupportedSurfaceRegressionTests(unittest.TestCase):
    def test_direct_supported_suffix_cannot_rotate_public_recovery_after_cutoff(self):
        """The underlying LAB-086 class must not remain a weaker supported authority.

        final_supported adds proof-first SQL fencing, but callers can still import
        SupportedAsymmetricBreakGlassLedger directly.  After cutoff that direct
        surface must fail closed rather than execute its older mutation-first
        public-recovery rotation path.
        """
        helper = AsymmetricSuffixIntegrationTests()
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
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
            ) = helper.make_ledger(path)
            helper.migrate(ledger, old_public_signers)

            new_public, new_public_signers = public_recovery(2, 2, "direct-surface")
            payload = custody_rotation_payload(
                ledger.public_recovery_custody.current(),
                new_public,
                ledger.rotation_authority.current().authority_id,
            )

            with self.assertRaises(Exception):
                ledger.rotate_public_recovery_authority(
                    new_public,
                    public_signatures(old_public_signers, payload, 3),
                    public_signatures(new_public_signers, payload, 3),
                    signatures(root_raw, payload, 2),
                )


if __name__ == "__main__":
    unittest.main()
