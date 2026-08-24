import sqlite3
import tempfile
import unittest
from pathlib import Path

from experiments.asymmetric_break_glass_history.final_supported import (
    SupportedFencedAsymmetricBreakGlassLedger,
)
from experiments.asymmetric_break_glass_history.tests.test_suffix import (
    AsymmetricSuffixIntegrationTests,
    authority,
    public_signatures,
    signatures,
)


class FullLowerHistoryGuardTests(unittest.TestCase):
    @staticmethod
    def _root_state(path):
        q = sqlite3.connect(path)
        try:
            return {
                "head": q.execute(
                    "SELECT authority_id,version,generation "
                    "FROM provider_rotation_authority_head WHERE singleton=1"
                ).fetchone(),
                "authorities": q.execute(
                    "SELECT COUNT(*) FROM provider_rotation_authorities"
                ).fetchone()[0],
                "normal": q.execute(
                    "SELECT COUNT(*) FROM provider_rotation_authority_transitions"
                ).fetchone()[0],
                "asymmetric": q.execute(
                    "SELECT COUNT(*) FROM provider_asymmetric_break_glass_proofs"
                ).fetchone()[0],
            }
        finally:
            q.close()

    def make_migrated(self, path):
        helper = AsymmetricSuffixIntegrationTests()
        (
            ledger,
            _,
            root1,
            root1_raw,
            _,
            _,
            _,
            public1_signers,
            _,
        ) = helper.make_ledger(path)
        helper.migrate(ledger, public1_signers)
        return ledger, root1, root1_raw, public1_signers

    def test_corrupt_shared_anchor_history_blocks_final_root_rotation_without_mutation(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            ledger, root1, root1_raw, _ = self.make_migrated(path)
            final = SupportedFencedAsymmetricBreakGlassLedger.from_existing(ledger)
            q = sqlite3.connect(path)
            q.execute("UPDATE shared_anchor_meta SET reserved_position=99 WHERE singleton=1")
            q.commit()
            q.close()
            before = self._root_state(path)
            root2, root2_raw = authority(2, 2, "lower-history-normal")
            payload = final.rotation_authority.authority_rotation_payload(root1, root2)
            with self.assertRaises(Exception):
                final.rotate_rotation_authority(
                    root2,
                    signatures(root1_raw, payload, 2),
                    signatures(root2_raw, payload, 2),
                )
            self.assertEqual(self._root_state(path), before)

    def test_direct_suffix_asymmetric_recovery_is_fenced_after_cutoff(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            ledger, _, _, public1_signers = self.make_migrated(path)
            before = self._root_state(path)
            root2, _ = authority(2, 2, "direct-suffix-recovery")
            payload = ledger.asymmetric_recovery_payload(root2)
            with self.assertRaises(Exception):
                ledger.recover_rotation_authority_asymmetric(
                    root2, public_signatures(public1_signers, payload, 3)
                )
            self.assertEqual(self._root_state(path), before)

    def test_final_asymmetric_recovery_remains_available(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            ledger, _, _, public1_signers = self.make_migrated(path)
            final = SupportedFencedAsymmetricBreakGlassLedger.from_existing(ledger)
            root2, _ = authority(2, 2, "final-recovery")
            payload = final.asymmetric_recovery_payload(root2)
            out = final.recover_rotation_authority_asymmetric(
                root2, public_signatures(public1_signers, payload, 3)
            )
            self.assertEqual(out["new_rotation_authority_id"], root2.authority_id)
            self.assertTrue(final.verify_durable())


if __name__ == "__main__":
    unittest.main()
