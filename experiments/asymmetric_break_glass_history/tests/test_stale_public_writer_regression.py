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
)


class StalePublicCustodyWriterRegressionTests(unittest.TestCase):
    def test_old_lab085_public_custody_writer_cannot_rotate_after_cutoff(self):
        helper = AsymmetricSuffixIntegrationTests()
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            ledger, _, _, _, _, _, _, old_public_signers, _ = helper.make_ledger(path)
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
            q.close()

            old = ledger.public_recovery_custody.current_locked(
                ledger.public_recovery_custody._con()
            )
            root = ledger.rotation_authority.current()
            new_public, new_public_signers = public_recovery(2, 2, "stale-writer")
            payload = custody_rotation_payload(old, new_public, root.authority_id)

            # This is the old LAB-085 public-custody API, intentionally bypassing
            # SupportedAsymmetricBreakGlassLedger.rotate_public_recovery_authority().
            # Post-cutoff SQL fencing must reject it because there is no LAB-086
            # root-coauthorization proof for this successor.
            with self.assertRaises(Exception):
                ledger.public_recovery_custody.rotate(
                    new_public,
                    root.authority_id,
                    public_signatures(old_public_signers, payload, 3),
                    public_signatures(new_public_signers, payload, 3),
                )

            q = sqlite3.connect(path)
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
            q.close()


if __name__ == "__main__":
    unittest.main()
