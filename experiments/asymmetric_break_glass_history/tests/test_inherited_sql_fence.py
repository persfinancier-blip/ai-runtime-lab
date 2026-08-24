import sqlite3
import unittest

from experiments.asymmetric_break_glass_history.strict_fence import (
    assert_public_mutation_fence_locked,
    install_public_mutation_fence_locked,
    remove_public_mutation_fence_locked,
)


class InheritedWriterSqlFenceTests(unittest.TestCase):
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
            """
        )
        install_public_mutation_fence_locked(q)
        q.commit()
        return q

    def test_direct_lower_root_and_provider_write_points_are_denied_after_cutoff(self):
        q = self.make_db()
        statements = (
            "INSERT INTO provider_rotation_authority_transitions VALUES('root-2')",
            "INSERT INTO provider_rotation_threshold_proofs VALUES('provider-2')",
            "INSERT INTO asymmetric_provider_transitions VALUES('provider-2')",
        )
        for statement in statements:
            with self.assertRaises(sqlite3.IntegrityError):
                q.execute(statement)
            q.rollback()
        self.assertTrue(assert_public_mutation_fence_locked(q))
        self.assertEqual(q.execute("SELECT COUNT(*) FROM provider_rotation_authority_transitions").fetchone()[0], 0)
        self.assertEqual(q.execute("SELECT COUNT(*) FROM provider_rotation_threshold_proofs").fetchone()[0], 0)
        self.assertEqual(q.execute("SELECT COUNT(*) FROM asymmetric_provider_transitions").fetchone()[0], 0)

    def test_existing_inherited_history_is_immutable_and_not_deletable_after_cutoff(self):
        q = self.make_db()
        q.execute("BEGIN IMMEDIATE")
        remove_public_mutation_fence_locked(q)
        q.execute("INSERT INTO provider_rotation_authority_transitions VALUES('root-2')")
        q.execute("INSERT INTO provider_rotation_threshold_proofs VALUES('provider-2')")
        q.execute("INSERT INTO asymmetric_provider_transitions VALUES('provider-2')")
        install_public_mutation_fence_locked(q)
        q.commit()

        cases = (
            (
                "provider_rotation_authority_transitions",
                "new_authority_id",
                "root-2",
                "root-attacker",
            ),
            (
                "provider_rotation_threshold_proofs",
                "new_provider_generation_id",
                "provider-2",
                "provider-attacker",
            ),
            (
                "asymmetric_provider_transitions",
                "new_generation_id",
                "provider-2",
                "provider-attacker",
            ),
        )
        for table, column, original, attacker in cases:
            with self.assertRaises(sqlite3.IntegrityError):
                q.execute(f"UPDATE {table} SET {column}=? WHERE {column}=?", (attacker, original))
            q.rollback()
            self.assertEqual(q.execute(f"SELECT {column} FROM {table}").fetchone()[0], original)
            with self.assertRaises(sqlite3.IntegrityError):
                q.execute(f"DELETE FROM {table} WHERE {column}=?", (original,))
            q.rollback()
            self.assertEqual(q.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0], 1)
        self.assertTrue(assert_public_mutation_fence_locked(q))

    def test_transaction_scoped_final_writer_can_remove_and_restore_all_fences(self):
        q = self.make_db()
        q.execute("BEGIN IMMEDIATE")
        remove_public_mutation_fence_locked(q)
        q.execute("INSERT INTO provider_rotation_authority_transitions VALUES('root-2')")
        q.execute("INSERT INTO provider_rotation_threshold_proofs VALUES('provider-2')")
        q.execute("INSERT INTO asymmetric_provider_transitions VALUES('provider-2')")
        install_public_mutation_fence_locked(q)
        self.assertTrue(assert_public_mutation_fence_locked(q))
        q.commit()

        with self.assertRaises(sqlite3.IntegrityError):
            q.execute("INSERT INTO provider_rotation_authority_transitions VALUES('root-3')")
        q.rollback()
        with self.assertRaises(sqlite3.IntegrityError):
            q.execute("INSERT INTO provider_rotation_threshold_proofs VALUES('provider-3')")
        q.rollback()
        with self.assertRaises(sqlite3.IntegrityError):
            q.execute("INSERT INTO asymmetric_provider_transitions VALUES('provider-3')")
        q.rollback()


if __name__ == "__main__":
    unittest.main()
