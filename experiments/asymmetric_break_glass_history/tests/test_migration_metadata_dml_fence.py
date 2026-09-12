import sqlite3
import unittest

from experiments.asymmetric_break_glass_history.strict_fence import (
    assert_public_mutation_fence_locked,
    install_public_mutation_fence_locked,
    remove_public_mutation_fence_locked,
)


class MigrationMetadataDmlFenceTests(unittest.TestCase):
    def make_db(self, *, complete=True):
        q = sqlite3.connect(":memory:")
        q.executescript(
            """
            CREATE TABLE provider_asymmetric_break_glass_boundary(
              singleton INTEGER PRIMARY KEY,x TEXT);
            CREATE TABLE provider_asymmetric_break_glass_legacy_projection(
              singleton INTEGER PRIMARY KEY,x TEXT);
            CREATE TABLE provider_asymmetric_break_glass_root_proof(
              singleton INTEGER PRIMARY KEY,x TEXT);
            CREATE TABLE provider_recovery_public_authorities(
              authority_id TEXT PRIMARY KEY);
            INSERT INTO provider_recovery_public_authorities VALUES('old');
            CREATE TABLE provider_recovery_public_transitions(
              new_authority_id TEXT PRIMARY KEY,old_authority_id TEXT,root_authority_id TEXT);
            CREATE TABLE provider_recovery_public_head(
              singleton INTEGER PRIMARY KEY,authority_id TEXT);
            INSERT INTO provider_recovery_public_head VALUES(1,'old');
            """
        )
        install_public_mutation_fence_locked(q)
        if complete:
            # Preserve the real migration ordering. Metadata triggers exist but
            # stay dormant until all three rows have been inserted atomically.
            q.execute("BEGIN")
            q.execute(
                "INSERT INTO provider_asymmetric_break_glass_legacy_projection VALUES(1,'projection')"
            )
            q.execute(
                "INSERT INTO provider_asymmetric_break_glass_boundary VALUES(1,'boundary')"
            )
            q.execute(
                "INSERT INTO provider_asymmetric_break_glass_root_proof VALUES(1,'root-proof')"
            )
            q.commit()
        return q

    def assert_blocked(self, q, sql):
        with self.assertRaises(sqlite3.IntegrityError):
            q.execute(sql)
        q.rollback()

    def test_first_atomic_cutoff_order_remains_allowed(self):
        q = self.make_db(complete=False)
        q.execute("BEGIN")
        q.execute(
            "INSERT INTO provider_asymmetric_break_glass_legacy_projection VALUES(1,'projection')"
        )
        q.execute(
            "INSERT INTO provider_asymmetric_break_glass_boundary VALUES(1,'boundary')"
        )
        q.execute(
            "INSERT INTO provider_asymmetric_break_glass_root_proof VALUES(1,'root-proof')"
        )
        q.commit()
        self.assertTrue(assert_public_mutation_fence_locked(q))

    def test_completed_cutoff_metadata_rejects_update_delete_replace_and_upsert(self):
        q = self.make_db()
        attacks = (
            "UPDATE provider_asymmetric_break_glass_boundary SET x='evil' WHERE singleton=1",
            "DELETE FROM provider_asymmetric_break_glass_boundary WHERE singleton=1",
            "INSERT OR REPLACE INTO provider_asymmetric_break_glass_boundary VALUES(1,'evil')",
            "INSERT INTO provider_asymmetric_break_glass_boundary VALUES(1,'evil') ON CONFLICT(singleton) DO UPDATE SET x='evil'",
            "UPDATE provider_asymmetric_break_glass_legacy_projection SET x='evil' WHERE singleton=1",
            "DELETE FROM provider_asymmetric_break_glass_legacy_projection WHERE singleton=1",
            "INSERT OR REPLACE INTO provider_asymmetric_break_glass_legacy_projection VALUES(1,'evil')",
            "INSERT INTO provider_asymmetric_break_glass_legacy_projection VALUES(1,'evil') ON CONFLICT(singleton) DO UPDATE SET x='evil'",
            "UPDATE provider_asymmetric_break_glass_root_proof SET x='evil' WHERE singleton=1",
            "DELETE FROM provider_asymmetric_break_glass_root_proof WHERE singleton=1",
            "INSERT OR REPLACE INTO provider_asymmetric_break_glass_root_proof VALUES(1,'evil')",
            "INSERT INTO provider_asymmetric_break_glass_root_proof VALUES(1,'evil') ON CONFLICT(singleton) DO UPDATE SET x='evil'",
        )
        for attack in attacks:
            self.assert_blocked(q, attack)
        self.assertEqual(
            q.execute("SELECT x FROM provider_asymmetric_break_glass_boundary").fetchone()[0],
            "boundary",
        )
        self.assertEqual(
            q.execute("SELECT x FROM provider_asymmetric_break_glass_legacy_projection").fetchone()[0],
            "projection",
        )
        self.assertEqual(
            q.execute("SELECT x FROM provider_asymmetric_break_glass_root_proof").fetchone()[0],
            "root-proof",
        )

    def test_final_writer_thaw_does_not_remove_migration_metadata_fence(self):
        q = self.make_db()
        q.execute("BEGIN IMMEDIATE")
        remove_public_mutation_fence_locked(q)
        with self.assertRaises(sqlite3.IntegrityError):
            q.execute(
                "UPDATE provider_asymmetric_break_glass_boundary SET x='evil' WHERE singleton=1"
            )
        q.rollback()
        self.assertTrue(assert_public_mutation_fence_locked(q))
        self.assertEqual(
            q.execute("SELECT x FROM provider_asymmetric_break_glass_boundary").fetchone()[0],
            "boundary",
        )


if __name__ == "__main__":
    unittest.main()
