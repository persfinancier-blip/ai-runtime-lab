import sqlite3
import unittest

from experiments.mutable_shared_anchor_writer.adoption_foreign_keys import (
    AdoptionForeignKeyError,
    validate_no_foreign_key_constraints,
)


class AdoptionForeignKeyRegressionTests(unittest.TestCase):
    def make_db(self, *, restrictive_foreign_key=False):
        q = sqlite3.connect(":memory:", isolation_level=None)
        q.execute("PRAGMA foreign_keys=ON")
        reference = (
            " REFERENCES legacy_components(component_id)"
            if restrictive_foreign_key
            else ""
        )
        q.executescript(
            f"""
            CREATE TABLE legacy_components(component_id TEXT PRIMARY KEY);
            CREATE TABLE shared_anchor_meta(
              singleton INTEGER PRIMARY KEY CHECK(singleton=1),
              reserved_position INTEGER NOT NULL CHECK(reserved_position>=0)
            );
            CREATE TABLE shared_anchor_intents(
              intent_id TEXT PRIMARY KEY,
              component_id TEXT NOT NULL{reference},
              intent_type TEXT NOT NULL,
              payload_digest TEXT NOT NULL,
              provider_id TEXT NOT NULL,
              provider_generation INTEGER NOT NULL,
              predecessor_position INTEGER NOT NULL,
              position INTEGER NOT NULL UNIQUE,
              request_id TEXT NOT NULL UNIQUE,
              status TEXT NOT NULL CHECK(status IN ('PREPARED','CONFIRMED')),
              receipt_binding TEXT
            );
            CREATE TABLE component_anchor_watermarks(
              component_id TEXT PRIMARY KEY,
              position INTEGER NOT NULL CHECK(position>=0)
            );
            CREATE TABLE asymmetric_provider_receipts(
              request_id TEXT PRIMARY KEY,
              provider_id TEXT NOT NULL,
              generation INTEGER NOT NULL,
              position INTEGER NOT NULL,
              kind TEXT NOT NULL,
              challenge TEXT NOT NULL,
              signature TEXT NOT NULL,
              stable_binding TEXT NOT NULL
            );
            """
        )
        return q

    def validate(self, q):
        q.execute("BEGIN IMMEDIATE")
        try:
            return validate_no_foreign_key_constraints(q)
        finally:
            q.rollback()

    def test_canonical_schema_without_foreign_keys_is_accepted(self):
        self.assertTrue(self.validate(self.make_db()))

    def test_restrictive_legacy_foreign_key_is_rejected(self):
        q = self.make_db(restrictive_foreign_key=True)
        with self.assertRaises(sqlite3.IntegrityError):
            q.execute(
                "INSERT INTO shared_anchor_intents VALUES(?,?,?,?,?,?,?,?,?,'PREPARED',NULL)",
                (
                    "intent-b",
                    "component-b",
                    "migration",
                    "a" * 64,
                    "provider",
                    1,
                    0,
                    1,
                    "b" * 64,
                ),
            )
        with self.assertRaises(AdoptionForeignKeyError):
            self.validate(q)


if __name__ == "__main__":
    unittest.main()
