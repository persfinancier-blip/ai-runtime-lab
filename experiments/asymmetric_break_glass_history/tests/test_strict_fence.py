import sqlite3
import unittest

from experiments.asymmetric_break_glass_history.strict_fence import (
    assert_public_mutation_fence_locked,
    install_public_mutation_fence_locked,
    remove_public_mutation_fence_locked,
)


class StrictPublicMutationFenceTests(unittest.TestCase):
    def make_db(self):
        q = sqlite3.connect(":memory:")
        q.executescript(
            """
            CREATE TABLE provider_asymmetric_break_glass_boundary(
              singleton INTEGER PRIMARY KEY);
            INSERT INTO provider_asymmetric_break_glass_boundary VALUES(1);
            CREATE TABLE provider_recovery_public_authorities(
              authority_id TEXT PRIMARY KEY);
            INSERT INTO provider_recovery_public_authorities VALUES('old');
            CREATE TABLE provider_recovery_public_transitions(
              new_authority_id TEXT,old_authority_id TEXT,root_authority_id TEXT);
            CREATE TABLE provider_recovery_public_head(
              singleton INTEGER PRIMARY KEY,authority_id TEXT);
            INSERT INTO provider_recovery_public_head VALUES(1,'old');
            CREATE TABLE provider_rotation_authority_head(
              singleton INTEGER PRIMARY KEY,authority_id TEXT,version INTEGER,generation INTEGER);
            INSERT INTO provider_rotation_authority_head VALUES(1,'root',1,1);
            CREATE TABLE provider_asymmetric_recovery_public_root_proofs(
              new_public_authority_id TEXT PRIMARY KEY,old_public_authority_id TEXT,
              root_authority_id TEXT,root_version INTEGER,root_generation INTEGER,
              intent_digest TEXT,root_signatures_json TEXT);
            """
        )
        install_public_mutation_fence_locked(q)
        q.commit()
        return q

    def test_forged_proof_row_is_not_mutation_authority(self):
        q = self.make_db()
        q.execute(
            "INSERT INTO provider_asymmetric_recovery_public_root_proofs VALUES(?,?,?,?,?,?,?)",
            ("new", "old", "root", 1, 1, "0" * 64, "[]"),
        )
        q.commit()
        with self.assertRaises(sqlite3.IntegrityError):
            q.execute("INSERT INTO provider_recovery_public_authorities VALUES('new')")
        q.rollback()
        self.assertEqual(
            q.execute("SELECT authority_id FROM provider_recovery_public_head").fetchone()[0],
            "old",
        )
        self.assertEqual(
            q.execute("SELECT COUNT(*) FROM provider_recovery_public_authorities").fetchone()[0],
            1,
        )

    def test_write_locked_controlled_mutation_reinstalls_fence_before_commit(self):
        q = self.make_db()
        q.execute("BEGIN IMMEDIATE")
        remove_public_mutation_fence_locked(q)
        q.execute("INSERT INTO provider_recovery_public_authorities VALUES('new')")
        q.execute(
            "INSERT INTO provider_recovery_public_transitions VALUES('new','old','root')"
        )
        q.execute(
            "UPDATE provider_recovery_public_head SET authority_id='new' WHERE singleton=1"
        )
        install_public_mutation_fence_locked(q)
        self.assertTrue(assert_public_mutation_fence_locked(q))
        q.commit()
        self.assertEqual(
            q.execute("SELECT authority_id FROM provider_recovery_public_head").fetchone()[0],
            "new",
        )
        with self.assertRaises(sqlite3.IntegrityError):
            q.execute("INSERT INTO provider_recovery_public_authorities VALUES('later')")
        q.rollback()

    def test_rollback_after_temporary_fence_removal_restores_policy(self):
        q = self.make_db()
        q.execute("BEGIN IMMEDIATE")
        remove_public_mutation_fence_locked(q)
        q.execute("INSERT INTO provider_recovery_public_authorities VALUES('rolled-back')")
        q.rollback()
        self.assertTrue(assert_public_mutation_fence_locked(q))
        with self.assertRaises(sqlite3.IntegrityError):
            q.execute("INSERT INTO provider_recovery_public_authorities VALUES('later')")
        q.rollback()
        self.assertEqual(
            q.execute("SELECT COUNT(*) FROM provider_recovery_public_authorities").fetchone()[0],
            1,
        )

    def test_obsolete_proof_row_triggers_are_replaced(self):
        q = self.make_db()
        remove_public_mutation_fence_locked(q)
        q.execute(
            """CREATE TRIGGER lab086_public_authority_requires_root_proof
            BEFORE INSERT ON provider_recovery_public_authorities
            WHEN 0 BEGIN SELECT RAISE(ABORT,'obsolete'); END"""
        )
        install_public_mutation_fence_locked(q)
        self.assertTrue(assert_public_mutation_fence_locked(q))
        names = {
            row[0]
            for row in q.execute(
                "SELECT name FROM sqlite_master WHERE type='trigger'"
            ).fetchall()
        }
        self.assertNotIn("lab086_public_authority_requires_root_proof", names)


if __name__ == "__main__":
    unittest.main()
