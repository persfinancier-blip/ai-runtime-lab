import sqlite3
import tempfile
import unittest
from pathlib import Path

from experiments.asymmetric_break_glass_history.final_supported import (
    SupportedFencedAsymmetricBreakGlassLedger,
)
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


class StalePublicCustodyWriterRegressionTests(unittest.TestCase):
    def test_old_lab085_public_custody_writer_cannot_rotate_after_cutoff(self):
        helper = AsymmetricSuffixIntegrationTests()
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            base, _, _, _, _, _, _, old_public_signers, _ = helper.make_ledger(path)
            ledger = SupportedFencedAsymmetricBreakGlassLedger.from_existing(base)
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

            custody_q = ledger.public_recovery_custody._con()
            try:
                old = ledger.public_recovery_custody.current_locked(custody_q)
            finally:
                custody_q.close()
            root = ledger.rotation_authority.current()
            new_public, new_public_signers = public_recovery(2, 2, "stale-writer")
            payload = custody_rotation_payload(old, new_public, root.authority_id)

            # This is the old LAB-085 public-custody API, intentionally bypassing
            # the final LAB-086 rotation method. The database fence must reject it
            # before any authority/transition/head mutation can commit.
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
            self.assertEqual(
                q.execute(
                    "SELECT COUNT(*) FROM provider_asymmetric_recovery_public_root_proofs"
                ).fetchone()[0],
                0,
            )
            q.close()

    def test_final_supported_rotation_commits_proof_and_successor_atomically(self):
        helper = AsymmetricSuffixIntegrationTests()
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            (
                base,
                _,
                _,
                root_raw,
                _,
                _,
                _,
                old_public_signers,
                _,
            ) = helper.make_ledger(path)
            ledger = SupportedFencedAsymmetricBreakGlassLedger.from_existing(base)
            helper.migrate(ledger, old_public_signers)

            new_public, new_public_signers = public_recovery(2, 2, "fenced-success")
            payload = ledger.public_recovery_rotation_payload(new_public)
            result = ledger.rotate_public_recovery_authority(
                new_public,
                public_signatures(old_public_signers, payload, 3),
                public_signatures(new_public_signers, payload, 3),
                signatures(root_raw, payload, 2),
            )
            self.assertEqual(result["new_public_authority_id"], new_public.authority_id)

            q = sqlite3.connect(path)
            try:
                self.assertEqual(
                    q.execute(
                        "SELECT authority_id FROM provider_recovery_public_head WHERE singleton=1"
                    ).fetchone()[0],
                    new_public.authority_id,
                )
                self.assertEqual(
                    q.execute(
                        "SELECT COUNT(*) FROM provider_asymmetric_recovery_public_root_proofs "
                        "WHERE new_public_authority_id=?",
                        (new_public.authority_id,),
                    ).fetchone()[0],
                    1,
                )
            finally:
                q.close()
            self.assertTrue(ledger.verify_durable())


if __name__ == "__main__":
    unittest.main()
