import sqlite3
import unittest

from experiments.asymmetric_break_glass_history.strict_fence import (
    install_public_mutation_fence_locked,
)


class PostCutoffEvidenceDmlFenceTests(unittest.TestCase):
    def setUp(self):
        self.q = sqlite3.connect(":memory:")
        self.q.executescript(
            """
            CREATE TABLE provider_asymmetric_break_glass_boundary(
              singleton INTEGER PRIMARY KEY CHECK(singleton=1)
            );
            INSERT INTO provider_asymmetric_break_glass_boundary VALUES(1);

            CREATE TABLE provider_recovery_public_authorities(
              authority_id TEXT PRIMARY KEY
            );
            CREATE TABLE provider_recovery_public_transitions(
              new_authority_id TEXT PRIMARY KEY
            );
            CREATE TABLE provider_recovery_public_head(
              singleton INTEGER PRIMARY KEY CHECK(singleton=1),
              authority_id TEXT NOT NULL
            );

            CREATE TABLE provider_asymmetric_break_glass_proofs(
              new_rotation_authority_id TEXT PRIMARY KEY,
              intent_digest TEXT NOT NULL
            );
            CREATE TABLE provider_asymmetric_recovery_public_root_proofs(
              new_public_authority_id TEXT PRIMARY KEY,
              intent_digest TEXT NOT NULL
            );

            INSERT INTO provider_asymmetric_break_glass_proofs
              VALUES('root-2','digest-a');
            INSERT INTO provider_asymmetric_recovery_public_root_proofs
              VALUES('public-2','digest-b');
            """
        )
        install_public_mutation_fence_locked(self.q)

    def tearDown(self):
        self.q.close()

    def _assert_existing_row_is_frozen(self, table, key_column, key, digest):
        with self.assertRaises(sqlite3.IntegrityError):
            self.q.execute(
                f"UPDATE {table} SET intent_digest='attacker' WHERE {key_column}=?",
                (key,),
            )
        self.q.rollback()

        with self.assertRaises(sqlite3.IntegrityError):
            self.q.execute(f"DELETE FROM {table} WHERE {key_column}=?", (key,))
        self.q.rollback()

        with self.assertRaises(sqlite3.IntegrityError):
            self.q.execute(
                f"INSERT OR REPLACE INTO {table}({key_column},intent_digest) VALUES(?,?)",
                (key, "attacker"),
            )
        self.q.rollback()

        with self.assertRaises(sqlite3.IntegrityError):
            self.q.execute(
                f"INSERT INTO {table}({key_column},intent_digest) VALUES(?,?) "
                f"ON CONFLICT({key_column}) DO UPDATE SET intent_digest=excluded.intent_digest",
                (key, "attacker"),
            )
        self.q.rollback()

        self.assertEqual(
            self.q.execute(
                f"SELECT intent_digest FROM {table} WHERE {key_column}=?", (key,)
            ).fetchone(),
            (digest,),
        )

    def test_break_glass_proof_is_immutable_after_cutoff(self):
        self._assert_existing_row_is_frozen(
            "provider_asymmetric_break_glass_proofs",
            "new_rotation_authority_id",
            "root-2",
            "digest-a",
        )

    def test_public_rotation_root_proof_is_immutable_after_cutoff(self):
        self._assert_existing_row_is_frozen(
            "provider_asymmetric_recovery_public_root_proofs",
            "new_public_authority_id",
            "public-2",
            "digest-b",
        )


if __name__ == "__main__":
    unittest.main()
