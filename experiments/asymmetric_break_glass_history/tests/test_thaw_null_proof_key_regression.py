import sqlite3
import unittest

from experiments.asymmetric_break_glass_history.strict_fence import (
    install_public_mutation_fence_locked,
    remove_public_mutation_fence_locked,
)


PROOF_TABLES = (
    "provider_asymmetric_break_glass_proofs",
    "provider_asymmetric_recovery_public_root_proofs",
)


def make_db(*, seed_null=False):
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
        CREATE TABLE provider_asymmetric_recovery_public_root_proofs(
          new_public_authority_id TEXT PRIMARY KEY,
          marker TEXT NOT NULL
        );
        """
    )
    if seed_null:
        for table in PROOF_TABLES:
            q.execute(f"INSERT INTO {table} VALUES(NULL, 'original-null')")
        q.commit()
    install_public_mutation_fence_locked(q)
    return q


class ThawNullProofKeyRegressionTests(unittest.TestCase):
    def test_thaw_never_allows_null_proof_identity(self):
        q = make_db()
        try:
            q.execute("BEGIN IMMEDIATE")
            remove_public_mutation_fence_locked(q)

            for table in PROOF_TABLES:
                with self.assertRaises(sqlite3.IntegrityError):
                    q.execute(f"INSERT INTO {table} VALUES(NULL, 'null-proof')")
                self.assertEqual(q.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0], 0)
            q.rollback()
        finally:
            q.close()

    def test_existing_null_key_cannot_be_replaced_or_duplicated_during_thaw(self):
        q = make_db(seed_null=True)
        try:
            q.execute("BEGIN IMMEDIATE")
            remove_public_mutation_fence_locked(q)

            for table in PROOF_TABLES:
                with self.assertRaises(sqlite3.IntegrityError):
                    q.execute(f"INSERT OR REPLACE INTO {table} VALUES(NULL, 'tampered')")
                rows = q.execute(f"SELECT marker FROM {table} ORDER BY rowid").fetchall()
                self.assertEqual(rows, [("original-null",)])
            q.rollback()
        finally:
            q.close()


if __name__ == "__main__":
    unittest.main()
