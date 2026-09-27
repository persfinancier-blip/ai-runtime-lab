import sqlite3
import unittest

from experiments.asymmetric_break_glass_history.strict_fence import (
    install_public_mutation_fence_locked,
    remove_public_mutation_fence_locked,
)


class ThawRowidCollisionRegressionTests(unittest.TestCase):
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
            INSERT INTO provider_recovery_public_authorities
            VALUES('public-old','original');

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
            INSERT INTO provider_asymmetric_break_glass_proofs
            VALUES('root-old','original');

            CREATE TABLE asymmetric_provider_receipts(
              request_id TEXT PRIMARY KEY,
              marker TEXT NOT NULL
            );
            INSERT INTO asymmetric_provider_receipts
            VALUES('request-old','original');
            """
        )
        install_public_mutation_fence_locked(q)
        q.commit()
        return q

    def assert_row_unchanged(self, q, table, key_column, key):
        self.assertEqual(
            q.execute(
                f"SELECT {key_column},marker FROM {table} WHERE {key_column}=?",
                (key,),
            ).fetchone(),
            (key, "original"),
        )

    def test_thaw_cannot_replace_public_history_via_hidden_rowid(self):
        q = self.make_db()
        try:
            old_rowid = q.execute(
                "SELECT rowid FROM provider_recovery_public_authorities "
                "WHERE authority_id='public-old'"
            ).fetchone()[0]
            q.execute("BEGIN IMMEDIATE")
            remove_public_mutation_fence_locked(q)

            with self.assertRaises(sqlite3.IntegrityError):
                q.execute(
                    "INSERT OR REPLACE INTO provider_recovery_public_authorities"
                    "(rowid,authority_id,marker) VALUES(?,?,?)",
                    (old_rowid, "public-attacker", "tampered"),
                )

            self.assert_row_unchanged(
                q,
                "provider_recovery_public_authorities",
                "authority_id",
                "public-old",
            )
            q.execute(
                "INSERT INTO provider_recovery_public_authorities VALUES(?,?)",
                ("public-new", "successor"),
            )
            q.rollback()
        finally:
            q.close()

    def test_thaw_cannot_replace_post_cutoff_proof_via_hidden_rowid(self):
        q = self.make_db()
        try:
            old_rowid = q.execute(
                "SELECT rowid FROM provider_asymmetric_break_glass_proofs "
                "WHERE new_rotation_authority_id='root-old'"
            ).fetchone()[0]
            q.execute("BEGIN IMMEDIATE")
            remove_public_mutation_fence_locked(q)

            with self.assertRaises(sqlite3.IntegrityError):
                q.execute(
                    "INSERT OR REPLACE INTO provider_asymmetric_break_glass_proofs"
                    "(rowid,new_rotation_authority_id,marker) VALUES(?,?,?)",
                    (old_rowid, "root-attacker", "tampered"),
                )

            self.assert_row_unchanged(
                q,
                "provider_asymmetric_break_glass_proofs",
                "new_rotation_authority_id",
                "root-old",
            )
            q.execute(
                "INSERT INTO provider_asymmetric_break_glass_proofs VALUES(?,?)",
                ("root-new", "successor"),
            )
            q.rollback()
        finally:
            q.close()

    def test_provider_receipt_cannot_be_replaced_via_hidden_rowid(self):
        q = self.make_db()
        try:
            old_rowid = q.execute(
                "SELECT rowid FROM asymmetric_provider_receipts "
                "WHERE request_id='request-old'"
            ).fetchone()[0]

            with self.assertRaises(sqlite3.IntegrityError):
                q.execute(
                    "INSERT OR REPLACE INTO asymmetric_provider_receipts"
                    "(rowid,request_id,marker) VALUES(?,?,?)",
                    (old_rowid, "request-attacker", "tampered"),
                )

            self.assert_row_unchanged(
                q,
                "asymmetric_provider_receipts",
                "request_id",
                "request-old",
            )
            q.execute(
                "INSERT INTO asymmetric_provider_receipts VALUES(?,?)",
                ("request-new", "successor"),
            )
            q.rollback()
        finally:
            q.close()


if __name__ == "__main__":
    unittest.main()
