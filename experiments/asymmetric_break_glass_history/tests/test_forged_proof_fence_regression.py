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
)


class ForgedProofFenceRegressionTests(unittest.TestCase):
    def test_forged_root_proof_row_does_not_authorize_stale_public_writer(self):
        helper = AsymmetricSuffixIntegrationTests()
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            base, _, _, _, _, _, _, old_public_signers, _ = helper.make_ledger(path)
            ledger = SupportedFencedAsymmetricBreakGlassLedger.from_existing(base)
            helper.migrate(ledger, old_public_signers)

            custody_q = ledger.public_recovery_custody._con()
            try:
                old = ledger.public_recovery_custody.current_locked(custody_q)
            finally:
                custody_q.close()
            root = ledger.rotation_authority.current()
            new_public, new_public_signers = public_recovery(2, 2, "forged-proof")
            payload = custody_rotation_payload(old, new_public, root.authority_id)

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
            # This row has the exact structural predecessor/successor/root metadata
            # expected by the old SQL fence, but its digest/signatures are forged.
            q.execute(
                "INSERT INTO provider_asymmetric_recovery_public_root_proofs "
                "VALUES(?,?,?,?,?,?,?)",
                (
                    new_public.authority_id,
                    old.authority_id,
                    root.authority_id,
                    root.version,
                    root.generation,
                    "0" * 64,
                    "[]",
                ),
            )
            q.commit()
            q.close()

            # A stale LAB-085 writer has valid old/new public quorum signatures but
            # no LAB-086 current-root coauthorization. A forged durable proof row
            # must never become mutation authority.
            with self.assertRaises(Exception):
                ledger.public_recovery_custody.rotate(
                    new_public,
                    root.authority_id,
                    public_signatures(old_public_signers, payload, 3),
                    public_signatures(new_public_signers, payload, 3),
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
                        "SELECT intent_digest,root_signatures_json "
                        "FROM provider_asymmetric_recovery_public_root_proofs "
                        "WHERE new_public_authority_id=?",
                        (new_public.authority_id,),
                    ).fetchone(),
                    ("0" * 64, "[]"),
                )
            finally:
                q.close()


if __name__ == "__main__":
    unittest.main()
