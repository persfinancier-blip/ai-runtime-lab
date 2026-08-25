import sqlite3
import unittest

from experiments.asymmetric_break_glass_history.strict_fence import (
    assert_public_mutation_fence_locked,
    install_public_mutation_fence_locked,
    remove_public_mutation_fence_locked,
)


class CurrentAuthorityDmlFenceTests(unittest.TestCase):
    def make_db(self):
        q = sqlite3.connect(":memory:", isolation_level=None)
        q.executescript(
            """
            CREATE TABLE provider_asymmetric_break_glass_boundary(singleton INTEGER PRIMARY KEY);
            INSERT INTO provider_asymmetric_break_glass_boundary VALUES(1);
            CREATE TABLE provider_asymmetric_break_glass_proofs(x TEXT);
            CREATE TABLE provider_asymmetric_recovery_public_root_proofs(x TEXT);

            CREATE TABLE provider_recovery_public_authorities(authority_id TEXT PRIMARY KEY);
            CREATE TABLE provider_recovery_public_transitions(new_authority_id TEXT PRIMARY KEY);
            CREATE TABLE provider_recovery_public_head(singleton INTEGER PRIMARY KEY,authority_id TEXT);

            CREATE TABLE provider_rotation_authorities(
              authority_id TEXT PRIMARY KEY,authority_name TEXT,version INTEGER,generation INTEGER,
              threshold INTEGER,keys_json TEXT,revoked_json TEXT
            );
            INSERT INTO provider_rotation_authorities VALUES('root1','root',1,1,1,'{}','[]');
            CREATE TABLE provider_rotation_authority_head(
              singleton INTEGER PRIMARY KEY,authority_id TEXT,version INTEGER,generation INTEGER
            );
            INSERT INTO provider_rotation_authority_head VALUES(1,'root1',1,1);
            CREATE TABLE provider_rotation_authority_transitions(new_authority_id TEXT PRIMARY KEY);
            CREATE TABLE provider_rotation_threshold_proofs(new_provider_generation_id TEXT PRIMARY KEY);
            CREATE TABLE provider_rotation_threshold_enablement(
              singleton INTEGER PRIMARY KEY,start_provider_generation_id TEXT,
              start_provider_generation INTEGER,authority_id TEXT,authority_version INTEGER,
              authority_generation INTEGER,enablement_digest TEXT,signatures_json TEXT
            );
            INSERT INTO provider_rotation_threshold_enablement
              VALUES(1,'gen1',1,'root1',1,1,'digest','[]');

            CREATE TABLE asymmetric_provider_generations(
              generation_id TEXT PRIMARY KEY,provider_id TEXT,generation INTEGER,public_key_hex TEXT
            );
            INSERT INTO asymmetric_provider_generations VALUES('gen1','provider',1,'00');
            CREATE TABLE asymmetric_provider_transitions(new_generation_id TEXT PRIMARY KEY);
            CREATE TABLE asymmetric_provider_head(
              singleton INTEGER PRIMARY KEY,generation_id TEXT,generation INTEGER
            );
            INSERT INTO asymmetric_provider_head VALUES(1,'gen1',1);
            """
        )
        install_public_mutation_fence_locked(q)
        return q

    def _blocked(self, q, sql):
        with self.assertRaises(sqlite3.IntegrityError):
            q.execute(sql)

    def test_current_authority_rows_are_not_raw_dml_mutable(self):
        q = self.make_db()
        self._blocked(q, "INSERT INTO provider_rotation_authorities VALUES('root2','root',2,2,1,'{}','[]')")
        self._blocked(q, "UPDATE provider_rotation_authorities SET version=999 WHERE authority_id='root1'")
        self._blocked(q, "DELETE FROM provider_rotation_authorities WHERE authority_id='root1'")

        self._blocked(q, "INSERT INTO asymmetric_provider_generations VALUES('gen2','provider',2,'00')")
        self._blocked(q, "UPDATE asymmetric_provider_generations SET generation=999 WHERE generation_id='gen1'")
        self._blocked(q, "DELETE FROM asymmetric_provider_generations WHERE generation_id='gen1'")
        self._blocked(q, "UPDATE asymmetric_provider_head SET generation=999 WHERE singleton=1")
        self._blocked(q, "DELETE FROM asymmetric_provider_head WHERE singleton=1")

        self._blocked(q, "UPDATE provider_rotation_threshold_enablement SET authority_version=999 WHERE singleton=1")
        self._blocked(q, "DELETE FROM provider_rotation_threshold_enablement WHERE singleton=1")
        self.assertTrue(assert_public_mutation_fence_locked(q))
        q.close()

    def test_transaction_scoped_thaw_keeps_historical_rows_frozen(self):
        q = self.make_db()
        q.execute("BEGIN IMMEDIATE")
        remove_public_mutation_fence_locked(q)
        q.execute("INSERT INTO provider_rotation_authorities VALUES('root2','root',2,2,1,'{}','[]')")
        q.execute("INSERT INTO asymmetric_provider_generations VALUES('gen2','provider',2,'00')")
        q.execute(
            "UPDATE asymmetric_provider_head SET generation_id='gen2',generation=2 WHERE singleton=1"
        )

        self._blocked(q, "UPDATE provider_rotation_authorities SET version=999 WHERE authority_id='root1'")
        self._blocked(q, "DELETE FROM asymmetric_provider_generations WHERE generation_id='gen1'")
        self._blocked(q, "UPDATE provider_rotation_threshold_enablement SET authority_version=999")
        q.rollback()

        self.assertEqual(
            q.execute("SELECT COUNT(*) FROM provider_rotation_authorities").fetchone()[0], 1
        )
        self.assertEqual(
            q.execute("SELECT COUNT(*) FROM asymmetric_provider_generations").fetchone()[0], 1
        )
        self.assertTrue(assert_public_mutation_fence_locked(q))
        q.close()


if __name__ == "__main__":
    unittest.main()
