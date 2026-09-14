import sqlite3
import unittest

from experiments.asymmetric_break_glass_history.strict_fence import (
    assert_public_mutation_fence_locked,
    install_public_mutation_fence_locked,
    remove_public_mutation_fence_locked,
)


class RootHeadFenceTests(unittest.TestCase):
    def make_db(self):
        q = sqlite3.connect(":memory:")
        q.executescript(
            """
            CREATE TABLE provider_asymmetric_break_glass_boundary(singleton INTEGER PRIMARY KEY);
            INSERT INTO provider_asymmetric_break_glass_boundary VALUES(1);
            CREATE TABLE provider_recovery_public_authorities(authority_id TEXT PRIMARY KEY);
            CREATE TABLE provider_recovery_public_transitions(new_authority_id TEXT PRIMARY KEY);
            CREATE TABLE provider_recovery_public_head(singleton INTEGER PRIMARY KEY);
            CREATE TABLE provider_rotation_authority_transitions(new_authority_id TEXT PRIMARY KEY);
            CREATE TABLE provider_rotation_threshold_proofs(new_provider_generation_id TEXT PRIMARY KEY);
            CREATE TABLE asymmetric_provider_transitions(new_generation_id TEXT PRIMARY KEY);
            CREATE TABLE provider_rotation_authority_head(
              singleton INTEGER PRIMARY KEY, authority_id TEXT, version INTEGER, generation INTEGER);
            INSERT INTO provider_rotation_authority_head VALUES(1,'root-1',1,1);
            """
        )
        install_public_mutation_fence_locked(q)
        q.commit()
        return q

    def assert_root1(self, q):
        self.assertEqual(
            q.execute(
                "SELECT authority_id,version,generation FROM provider_rotation_authority_head"
            ).fetchone(),
            ("root-1", 1, 1),
        )
        self.assertTrue(assert_public_mutation_fence_locked(q))

    def test_direct_root_head_update_is_denied_after_cutoff(self):
        q = self.make_db()
        with self.assertRaises(sqlite3.IntegrityError):
            q.execute(
                "UPDATE provider_rotation_authority_head "
                "SET authority_id='attacker',version=2,generation=2 WHERE singleton=1"
            )
        q.rollback()
        self.assert_root1(q)

    def test_insert_or_replace_cannot_bypass_root_head_update_fence(self):
        q = self.make_db()
        with self.assertRaises(sqlite3.IntegrityError):
            q.execute(
                "INSERT OR REPLACE INTO provider_rotation_authority_head "
                "VALUES(1,'attacker',2,2)"
            )
        q.rollback()
        self.assert_root1(q)

    def test_direct_root_head_delete_is_denied_after_cutoff(self):
        q = self.make_db()
        with self.assertRaises(sqlite3.IntegrityError):
            q.execute(
                "DELETE FROM provider_rotation_authority_head WHERE singleton=1"
            )
        q.rollback()
        self.assert_root1(q)

    def test_final_writer_can_remove_and_restore_root_head_fence_transactionally(self):
        q = self.make_db()
        q.execute("BEGIN IMMEDIATE")
        remove_public_mutation_fence_locked(q)
        q.execute(
            "UPDATE provider_rotation_authority_head "
            "SET authority_id='root-2',version=2,generation=2 WHERE singleton=1"
        )
        install_public_mutation_fence_locked(q)
        self.assertTrue(assert_public_mutation_fence_locked(q))
        q.commit()
        self.assertEqual(
            q.execute(
                "SELECT authority_id,version,generation FROM provider_rotation_authority_head"
            ).fetchone(),
            ("root-2", 2, 2),
        )
        with self.assertRaises(sqlite3.IntegrityError):
            q.execute(
                "UPDATE provider_rotation_authority_head "
                "SET authority_id='root-3',version=3,generation=3 WHERE singleton=1"
            )
        q.rollback()


if __name__ == "__main__":
    unittest.main()
