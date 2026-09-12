import sqlite3
import unittest

from experiments.asymmetric_break_glass_history.migration_guard import (
    AuthenticatedBreakGlassMigrationGuard,
)


class StaleTriggerUpgradeRegression(unittest.TestCase):
    def test_schema_upgrade_replaces_weaker_same_name_trigger(self):
        q = sqlite3.connect(":memory:")
        q.executescript(
            """
            CREATE TABLE provider_rotation_recovery_transitions(x INTEGER);
            CREATE TABLE provider_recovery_lifecycle_transitions(x INTEGER);
            CREATE TABLE provider_recovery_lifecycle_authorities(x INTEGER);
            CREATE TABLE provider_rotation_recovery_authorities(x INTEGER);
            CREATE TABLE provider_recovery_public_authorities(authority_id TEXT PRIMARY KEY);
            CREATE TABLE provider_recovery_public_head(
              singleton INTEGER PRIMARY KEY, authority_id TEXT NOT NULL
            );
            INSERT INTO provider_recovery_public_head VALUES(1,'old');
            CREATE TABLE provider_rotation_authority_head(
              singleton INTEGER PRIMARY KEY, authority_id TEXT NOT NULL,
              version INTEGER NOT NULL, generation INTEGER NOT NULL
            );
            INSERT INTO provider_rotation_authority_head VALUES(1,'root',1,1);
            CREATE TABLE provider_recovery_public_transitions(
              new_authority_id TEXT, old_authority_id TEXT, root_authority_id TEXT
            );

            -- Simulate a durable DB initialized by an older/weaker LAB-086 build.
            -- The current installer must replace this definition, not preserve it.
            CREATE TRIGGER lab086_public_head_requires_root_proof
            BEFORE UPDATE ON provider_recovery_public_head
            WHEN 0
            BEGIN SELECT RAISE(ABORT,'obsolete weak trigger'); END;
            """
        )

        q.execute("BEGIN IMMEDIATE")
        AuthenticatedBreakGlassMigrationGuard._ensure_schema_locked(q)
        q.execute(
            "INSERT INTO provider_asymmetric_break_glass_boundary "
            "VALUES(1,?,?,?,?,?,?,?,?,?)",
            ("0" * 64, "root", 1, 1, "pub", 1, 1, "1" * 64, "[]"),
        )
        q.commit()

        with self.assertRaises(sqlite3.IntegrityError):
            q.execute(
                "UPDATE provider_recovery_public_head "
                "SET authority_id='attacker' WHERE singleton=1"
            )
        self.assertEqual(
            q.execute(
                "SELECT authority_id FROM provider_recovery_public_head WHERE singleton=1"
            ).fetchone()[0],
            "old",
        )
        q.close()


if __name__ == "__main__":
    unittest.main()
