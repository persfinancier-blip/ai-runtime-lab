import sqlite3
import unittest

from experiments.asymmetric_break_glass_history.strict_fence import (
    install_public_mutation_fence_locked,
    remove_public_mutation_fence_locked,
)


def make_db():
    q = sqlite3.connect(":memory:")
    q.executescript(
        """
        CREATE TABLE provider_asymmetric_break_glass_boundary(
          singleton INTEGER PRIMARY KEY
        );
        INSERT INTO provider_asymmetric_break_glass_boundary VALUES(1);

        CREATE TABLE provider_recovery_public_authorities(
          authority_id TEXT PRIMARY KEY
        );
        CREATE TABLE provider_recovery_public_transitions(
          new_authority_id TEXT PRIMARY KEY
        );
        CREATE TABLE provider_recovery_public_head(
          singleton INTEGER PRIMARY KEY,
          authority_id TEXT NOT NULL
        );

        CREATE TABLE provider_asymmetric_break_glass_proofs(
          new_rotation_authority_id TEXT PRIMARY KEY,
          marker TEXT NOT NULL
        );
        INSERT INTO provider_asymmetric_break_glass_proofs VALUES('root-2','original');

        CREATE TABLE provider_asymmetric_recovery_public_root_proofs(
          new_public_authority_id TEXT PRIMARY KEY,
          marker TEXT NOT NULL
        );
        INSERT INTO provider_asymmetric_recovery_public_root_proofs VALUES('public-2','original');
        """
    )
    install_public_mutation_fence_locked(q)
    return q


class ThawProofReplaceRegressionTests(unittest.TestCase):
    def test_thaw_allows_new_proof_key_but_never_replace_existing_history(self):
        q = make_db()
        try:
            q.execute("BEGIN IMMEDIATE")
            remove_public_mutation_fence_locked(q)

            cases = (
                (
                    "provider_asymmetric_break_glass_proofs",
                    "new_rotation_authority_id",
                    "root-2",
                    "root-3",
                ),
                (
                    "provider_asymmetric_recovery_public_root_proofs",
                    "new_public_authority_id",
                    "public-2",
                    "public-3",
                ),
            )
            for table, key_column, existing_key, new_key in cases:
                with self.assertRaises(sqlite3.IntegrityError):
                    q.execute(
                        f"INSERT OR REPLACE INTO {table} VALUES(?, 'tampered')",
                        (existing_key,),
                    )
                self.assertEqual(
                    q.execute(
                        f"SELECT marker FROM {table} WHERE {key_column}=?",
                        (existing_key,),
                    ).fetchone()[0],
                    "original",
                )

                q.execute(
                    f"INSERT INTO {table} VALUES(?, 'new')",
                    (new_key,),
                )
                self.assertEqual(
                    q.execute(
                        f"SELECT marker FROM {table} WHERE {key_column}=?",
                        (new_key,),
                    ).fetchone()[0],
                    "new",
                )
            q.rollback()
        finally:
            q.close()


if __name__ == "__main__":
    unittest.main()
