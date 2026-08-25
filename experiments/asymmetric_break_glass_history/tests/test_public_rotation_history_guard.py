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


class PublicRotationHistoryGuardTests(unittest.TestCase):
    def test_corrupt_asymmetric_root_history_blocks_public_rotation_without_mutation(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            helper = AsymmetricSuffixIntegrationTests()
            (
                ledger,
                _,
                _,
                _,
                _,
                _,
                _,
                public1_signers,
                _,
            ) = helper.make_ledger(path)
            helper.migrate(ledger, public1_signers)
            ledger = SupportedFencedAsymmetricBreakGlassLedger.from_existing(ledger)

            root2, root2_raw = authority(2, 2, "history-guard-root")
            root_payload = ledger.asymmetric_recovery_payload(root2)
            ledger.recover_rotation_authority_asymmetric(
                root2, public_signatures(public1_signers, root_payload, 3)
            )

            q = sqlite3.connect(path)
            # Ordinary DML is fenced. Drop only the asymmetric-proof UPDATE
            # guard to model out-of-band durable corruption; the final public
            # rotation must still refuse to mutate any public-recovery state.
            q.execute("DROP TRIGGER lab086_break_glass_proof_is_immutable")
            q.execute(
                "UPDATE provider_asymmetric_break_glass_proofs "
                "SET public_signatures_json='[]' WHERE new_rotation_authority_id=?",
                (root2.authority_id,),
            )
            before = {
                "head": q.execute(
                    "SELECT authority_id,version,generation "
                    "FROM provider_recovery_public_head WHERE singleton=1"
                ).fetchone(),
                "authorities": q.execute(
                    "SELECT COUNT(*) FROM provider_recovery_public_authorities"
                ).fetchone()[0],
                "transitions": q.execute(
                    "SELECT COUNT(*) FROM provider_recovery_public_transitions"
                ).fetchone()[0],
                "root_proofs": q.execute(
                    "SELECT COUNT(*) FROM provider_asymmetric_recovery_public_root_proofs"
                ).fetchone()[0],
            }
            q.commit()
            q.close()

            public2, public2_signers = public_recovery(2, 2, "history-guard-public")
            rotate_payload = ledger.public_recovery_rotation_payload(public2)
            with self.assertRaises(Exception):
                ledger.rotate_public_recovery_authority(
                    public2,
                    public_signatures(public1_signers, rotate_payload, 3),
                    public_signatures(public2_signers, rotate_payload, 3),
                    signatures(root2_raw, rotate_payload, 2),
                )

            q = sqlite3.connect(path)
            after = {
                "head": q.execute(
                    "SELECT authority_id,version,generation "
                    "FROM provider_recovery_public_head WHERE singleton=1"
                ).fetchone(),
                "authorities": q.execute(
                    "SELECT COUNT(*) FROM provider_recovery_public_authorities"
                ).fetchone()[0],
                "transitions": q.execute(
                    "SELECT COUNT(*) FROM provider_recovery_public_transitions"
                ).fetchone()[0],
                "root_proofs": q.execute(
                    "SELECT COUNT(*) FROM provider_asymmetric_recovery_public_root_proofs"
                ).fetchone()[0],
            }
            q.close()
            self.assertEqual(after, before)


if __name__ == "__main__":
    unittest.main()
