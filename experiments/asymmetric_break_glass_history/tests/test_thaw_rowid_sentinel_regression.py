import sqlite3
import unittest

from experiments.asymmetric_break_glass_history.strict_fence import (
    install_public_mutation_fence_locked,
    remove_public_mutation_fence_locked,
)


class ThawRowidSentinelRegressionTests(unittest.TestCase):
    def make_db(self):
        q = sqlite3.connect(":memory:")
        q.executescript(
            """
            CREATE TABLE provider_asymmetric_break_glass_boundary(
              singleton INTEGER PRIMARY KEY
            );
            INSERT INTO provider_asymmetric_break_glass_boundary VALUES(1);

            CREATE TABLE provider_recovery_public_authorities(
              authority_id TEXT PRIMARY KEY,
              marker TEXT NOT NULL
            );
            CREATE TABLE provider_recovery_public_transitions(
              new_authority_id TEXT PRIMARY KEY
            );
            CREATE TABLE provider_recovery_public_head(
              singleton INTEGER PRIMARY KEY
            );
            CREATE TABLE provider_asymmetric_break_glass_proofs(
              new_rotation_authority_id TEXT PRIMARY KEY,
              marker TEXT NOT NULL
            );
            CREATE TABLE asymmetric_provider_receipts(
              request_id TEXT PRIMARY KEY,
              marker TEXT NOT NULL
            );
            """
        )
        install_public_mutation_fence_locked(q)
        q.commit()
        return q

    def test_explicit_reserved_rowid_minus_one_is_rejected_during_thaw(self):
        q = self.make_db()
        try:
            q.execute("BEGIN IMMEDIATE")
            remove_public_mutation_fence_locked(q)

            for table, key_column, key in (
                ("provider_recovery_public_authorities", "authority_id", "public-minus-one"),
                ("provider_asymmetric_break_glass_proofs", "new_rotation_authority_id", "proof-minus-one"),
            ):
                with self.assertRaises(sqlite3.IntegrityError):
                    q.execute(
                        f"INSERT INTO {table}(rowid,{key_column},marker) VALUES(-1,?,?)",
                        (key, "must-not-persist"),
                    )
                self.assertIsNone(
                    q.execute(
                        f"SELECT rowid FROM {table} WHERE {key_column}=?",
                        (key,),
                    ).fetchone()
                )

            q.rollback()
        finally:
            q.close()

    def test_omitted_rowid_still_allows_genuine_successors_during_thaw(self):
        q = self.make_db()
        try:
            q.execute("BEGIN IMMEDIATE")
            remove_public_mutation_fence_locked(q)
            q.execute(
                "INSERT INTO provider_recovery_public_authorities(authority_id,marker) VALUES(?,?)",
                ("public-successor", "ok"),
            )
            rowid = q.execute(
                "SELECT rowid FROM provider_recovery_public_authorities WHERE authority_id=?",
                ("public-successor",),
            ).fetchone()[0]
            self.assertNotEqual(rowid, -1)
            q.rollback()
        finally:
            q.close()


if __name__ == "__main__":
    unittest.main()
