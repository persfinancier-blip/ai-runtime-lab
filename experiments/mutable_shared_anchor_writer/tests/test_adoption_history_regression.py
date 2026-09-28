import sqlite3
import unittest

from experiments.mutable_shared_anchor_writer.adoption_validation import (
    AdoptionValidationError,
    validate_existing_mutable_state_locked,
)


class AdoptionHistoryRegressionTests(unittest.TestCase):
    def make_db(self):
        q = sqlite3.connect(":memory:", isolation_level=None)
        q.executescript(
            """
            CREATE TABLE shared_anchor_meta(
              singleton INTEGER PRIMARY KEY CHECK(singleton=1),
              reserved_position INTEGER NOT NULL CHECK(reserved_position>=0)
            );
            INSERT INTO shared_anchor_meta VALUES(1,0);
            CREATE TABLE shared_anchor_intents(
              intent_id TEXT PRIMARY KEY,
              component_id TEXT NOT NULL,
              intent_type TEXT NOT NULL,
              payload_digest TEXT NOT NULL,
              provider_id TEXT NOT NULL,
              provider_generation INTEGER NOT NULL,
              predecessor_position INTEGER NOT NULL,
              position INTEGER NOT NULL UNIQUE,
              request_id TEXT NOT NULL UNIQUE,
              status TEXT NOT NULL,
              receipt_binding TEXT
            );
            CREATE TABLE component_anchor_watermarks(
              component_id TEXT PRIMARY KEY,
              position INTEGER NOT NULL CHECK(position>=0)
            );
            CREATE TABLE asymmetric_provider_receipts(request_id TEXT PRIMARY KEY);
            """
        )
        return q

    def assert_rejected(self, q):
        q.execute("BEGIN IMMEDIATE")
        with self.assertRaises(AdoptionValidationError):
            validate_existing_mutable_state_locked(q)
        q.rollback()

    def test_reserved_tail_without_history_is_rejected(self):
        q = self.make_db()
        q.execute("UPDATE shared_anchor_meta SET reserved_position=5 WHERE singleton=1")
        self.assert_rejected(q)

    def test_watermark_ahead_of_history_is_rejected(self):
        q = self.make_db()
        q.execute("INSERT INTO component_anchor_watermarks VALUES('component-A',5)")
        self.assert_rejected(q)

    def test_empty_fresh_state_is_allowed(self):
        q = self.make_db()
        q.execute("BEGIN IMMEDIATE")
        self.assertTrue(validate_existing_mutable_state_locked(q))
        q.rollback()


if __name__ == "__main__":
    unittest.main()
