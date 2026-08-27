import sqlite3
import unittest

from experiments.asymmetric_break_glass_history.strict_fence import (
    install_public_mutation_fence_locked,
    remove_public_mutation_fence_locked,
)


class ThawHistoryKeyCollisionRegressionTests(unittest.TestCase):
    def make_db(self):
        q = sqlite3.connect(":memory:")
        q.executescript(
            """
            CREATE TABLE provider_asymmetric_break_glass_boundary(
              singleton INTEGER PRIMARY KEY
            );
            INSERT INTO provider_asymmetric_break_glass_boundary VALUES(1);

            CREATE TABLE provider_recovery_public_authorities(
              authority_id TEXT PRIMARY KEY,marker TEXT NOT NULL
            );
            INSERT INTO provider_recovery_public_authorities VALUES('public-1','original');
            CREATE TABLE provider_recovery_public_transitions(
              new_authority_id TEXT PRIMARY KEY,marker TEXT NOT NULL
            );
            INSERT INTO provider_recovery_public_transitions VALUES('public-1','original');
            CREATE TABLE provider_recovery_public_head(
              singleton INTEGER PRIMARY KEY,authority_id TEXT NOT NULL
            );
            INSERT INTO provider_recovery_public_head VALUES(1,'public-1');

            CREATE TABLE provider_rotation_authorities(
              authority_id TEXT PRIMARY KEY,marker TEXT NOT NULL
            );
            INSERT INTO provider_rotation_authorities VALUES('root-1','original');
            CREATE TABLE provider_rotation_authority_transitions(
              new_authority_id TEXT PRIMARY KEY,marker TEXT NOT NULL
            );
            INSERT INTO provider_rotation_authority_transitions VALUES('root-1','original');
            CREATE TABLE provider_rotation_threshold_proofs(
              new_provider_generation_id TEXT PRIMARY KEY,marker TEXT NOT NULL
            );
            INSERT INTO provider_rotation_threshold_proofs VALUES('generation-1','original');

            CREATE TABLE asymmetric_provider_generations(
              generation_id TEXT PRIMARY KEY,marker TEXT NOT NULL
            );
            INSERT INTO asymmetric_provider_generations VALUES('generation-1','original');
            CREATE TABLE asymmetric_provider_transitions(
              new_generation_id TEXT PRIMARY KEY,marker TEXT NOT NULL
            );
            INSERT INTO asymmetric_provider_transitions VALUES('generation-1','original');
            """
        )
        install_public_mutation_fence_locked(q)
        q.commit()
        return q

    def test_thaw_allows_new_history_key_but_never_replace_or_null_identity(self):
        q = self.make_db()
        try:
            q.execute("BEGIN IMMEDIATE")
            remove_public_mutation_fence_locked(q)
            cases = (
                ("provider_recovery_public_authorities", "authority_id", "public-1", "public-2"),
                ("provider_recovery_public_transitions", "new_authority_id", "public-1", "public-2"),
                ("provider_rotation_authorities", "authority_id", "root-1", "root-2"),
                ("provider_rotation_authority_transitions", "new_authority_id", "root-1", "root-2"),
                ("provider_rotation_threshold_proofs", "new_provider_generation_id", "generation-1", "generation-2"),
                ("asymmetric_provider_generations", "generation_id", "generation-1", "generation-2"),
                ("asymmetric_provider_transitions", "new_generation_id", "generation-1", "generation-2"),
            )
            for table, key_column, existing_key, new_key in cases:
                with self.subTest(table=table, mode="replace"):
                    with self.assertRaises(sqlite3.IntegrityError):
                        q.execute(
                            f"INSERT OR REPLACE INTO {table} VALUES(?, 'tampered')",
                            (existing_key,),
                        )
                    self.assertEqual(
                        q.execute(
                            f"SELECT marker FROM {table} WHERE {key_column} IS ?",
                            (existing_key,),
                        ).fetchone()[0],
                        "original",
                    )
                with self.subTest(table=table, mode="null"):
                    with self.assertRaises(sqlite3.IntegrityError):
                        q.execute(f"INSERT INTO {table} VALUES(NULL, 'null-key')")
                with self.subTest(table=table, mode="new"):
                    q.execute(f"INSERT INTO {table} VALUES(?, 'new')", (new_key,))
                    self.assertEqual(
                        q.execute(
                            f"SELECT marker FROM {table} WHERE {key_column} IS ?",
                            (new_key,),
                        ).fetchone()[0],
                        "new",
                    )
            q.rollback()
        finally:
            q.close()


if __name__ == "__main__":
    unittest.main()
