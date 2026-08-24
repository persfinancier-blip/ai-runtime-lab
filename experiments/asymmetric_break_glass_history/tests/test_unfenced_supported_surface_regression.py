import sqlite3
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

        The migration boundary itself installs the proof-first SQL fence.  A caller
        that imports SupportedAsymmetricBreakGlassLedger directly must therefore
        fail before any authority/transition/head mutation can commit, rather than
        falling through to a later verifier error after corrupting durable state.
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

            q = sqlite3.connect(path)
            before_head = q.execute(
                "SELECT authority_id,version,generation "
                "FROM provider_recovery_public_head WHERE singleton=1"
            ).fetchone()
            before_authorities = q.execute(
                "SELECT COUNT(*) FROM provider_recovery_public_authorities"
            ).fetchone()[0]
            before_transitions = q.execute(
                "SELECT COUNT(*) FROM provider_recovery_public_transitions"
            ).fetchone()[0]
            before_proofs = q.execute(
                "SELECT COUNT(*) FROM provider_asymmetric_recovery_public_root_proofs"
            ).fetchone()[0]
            q.close()

            new_public, new_public_signers = public_recovery(2, 2, "direct-surface")
            custody_q = ledger.public_recovery_custody._con()
            try:
                old_public = ledger.public_recovery_custody.current_locked(custody_q)
            finally:
                custody_q.close()
            payload = custody_rotation_payload(
                old_public,
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

            q = sqlite3.connect(path)
            try:
                self.assertEqual(
                    q.execute(
                        "SELECT authority_id,version,generation "
                        "FROM provider_recovery_public_head WHERE singleton=1"
                    ).fetchone(),
                    before_head,
                )
                self.assertEqual(
                    q.execute(
                        "SELECT COUNT(*) FROM provider_recovery_public_authorities"
                    ).fetchone()[0],
                    before_authorities,
                )
                self.assertEqual(
                    q.execute(
                        "SELECT COUNT(*) FROM provider_recovery_public_transitions"
                    ).fetchone()[0],
                    before_transitions,
                )
                self.assertEqual(
                    q.execute(
                        "SELECT COUNT(*) FROM provider_asymmetric_recovery_public_root_proofs"
                    ).fetchone()[0],
                    before_proofs,
                )
            finally:
                q.close()


if __name__ == "__main__":
    unittest.main()
