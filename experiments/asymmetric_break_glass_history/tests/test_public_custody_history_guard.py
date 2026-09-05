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
    public_recovery,
    public_signatures,
    signatures,
)


class PublicCustodyHistoryGuardTests(unittest.TestCase):
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
                "normal_transitions": q.execute(
                    "SELECT COUNT(*) FROM provider_rotation_authority_transitions"
                ).fetchone()[0],
            }
        finally:
            q.close()

    def test_corrupt_public_custody_transition_blocks_new_root_rotation_without_mutation(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            helper = AsymmetricSuffixIntegrationTests()
            (
                base,
                _,
                root1,
                root1_raw,
                _,
                _,
                _,
                public1_signers,
                _,
            ) = helper.make_ledger(path)
            helper.migrate(base, public1_signers)
            ledger = SupportedFencedAsymmetricBreakGlassLedger.from_existing(base)

            public2, public2_signers = public_recovery(2, 2, "history-guard-public")
            rotate_payload = ledger.public_recovery_rotation_payload(public2)
            ledger.rotate_public_recovery_authority(
                public2,
                public_signatures(public1_signers, rotate_payload, 3),
                public_signatures(public2_signers, rotate_payload, 3),
                signatures(root1_raw, rotate_payload, 2),
            )

            # Ordinary post-cutoff DML is denied by LAB-086. Drop only the
            # transition UPDATE guard to model out-of-band durable corruption;
            # the final supported writer must still re-authenticate LAB-085's
            # Ed25519 transition history before changing the root.
            q = sqlite3.connect(path)
            q.execute("DROP TRIGGER lab086_public_transition_is_immutable")
            q.execute(
                "UPDATE provider_recovery_public_transitions "
                "SET old_signatures_json='[]' WHERE new_authority_id=?",
                (public2.authority_id,),
            )
            q.commit()
            q.close()

            before = self._root_state(path)
            root2, root2_raw = authority(2, 2, "history-guard-root")
            payload = ledger.rotation_authority.authority_rotation_payload(root1, root2)
            with self.assertRaises(Exception):
                ledger.rotate_rotation_authority(
                    root2,
                    signatures(root1_raw, payload, 2),
                    signatures(root2_raw, payload, 2),
                )
            self.assertEqual(self._root_state(path), before)


if __name__ == "__main__":
    unittest.main()
