import sqlite3
import unittest

from experiments.asymmetric_break_glass_history.strict_fence import (
    install_public_mutation_fence_locked,
)


class PreCutoffOrphanEvidenceRegressionTests(unittest.TestCase):
    @staticmethod
    def make_db():
        q = sqlite3.connect(":memory:")
        q.executescript(
            """
            CREATE TABLE provider_asymmetric_break_glass_boundary(
              singleton INTEGER PRIMARY KEY CHECK(singleton=1)
            );
            CREATE TABLE provider_recovery_public_authorities(authority_id TEXT PRIMARY KEY);
            CREATE TABLE provider_recovery_public_transitions(new_authority_id TEXT PRIMARY KEY);
            CREATE TABLE provider_recovery_public_head(singleton INTEGER PRIMARY KEY,authority_id TEXT);
            CREATE TABLE provider_asymmetric_recovery_public_root_proofs(
              new_public_authority_id TEXT PRIMARY KEY
            );
            CREATE TABLE provider_asymmetric_break_glass_proofs(
              new_rotation_authority_id TEXT PRIMARY KEY
            );
            """
        )
        return q

    def test_orphan_public_rotation_root_proof_is_rejected_before_cutoff(self):
        q = self.make_db()
        q.execute(
            "INSERT INTO provider_asymmetric_recovery_public_root_proofs VALUES('orphan')"
        )
        with self.assertRaises(RuntimeError):
            install_public_mutation_fence_locked(q)
        self.assertIsNone(
            q.execute(
                "SELECT 1 FROM provider_asymmetric_break_glass_boundary WHERE singleton=1"
            ).fetchone()
        )
        q.close()

    def test_orphan_asymmetric_break_glass_proof_is_rejected_before_cutoff(self):
        q = self.make_db()
        q.execute("INSERT INTO provider_asymmetric_break_glass_proofs VALUES('orphan')")
        with self.assertRaises(RuntimeError):
            install_public_mutation_fence_locked(q)
        self.assertIsNone(
            q.execute(
                "SELECT 1 FROM provider_asymmetric_break_glass_boundary WHERE singleton=1"
            ).fetchone()
        )
        q.close()

    def test_empty_pre_cutoff_state_still_installs_fence(self):
        q = self.make_db()
        install_public_mutation_fence_locked(q)
        self.assertGreater(
            q.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='trigger'").fetchone()[0],
            0,
        )
        q.close()

    def test_post_cutoff_evidence_is_not_rejected_by_partial_state_guard(self):
        q = self.make_db()
        q.execute("INSERT INTO provider_asymmetric_break_glass_boundary VALUES(1)")
        q.execute(
            "INSERT INTO provider_asymmetric_recovery_public_root_proofs VALUES('expected')"
        )
        install_public_mutation_fence_locked(q)
        q.close()


if __name__ == "__main__":
    unittest.main()
