import sqlite3
import unittest

from experiments.mutable_shared_anchor_writer.adoption_validation import (
    AdoptionValidationError,
    validate_existing_mutable_state_locked,
)


class AdoptionSchemaContractRegressionTests(unittest.TestCase):
    def make_canonical_db(self):
        q = sqlite3.connect(":memory:", isolation_level=None)
        q.executescript(
            """
            CREATE TABLE shared_anchor_meta(
              singleton INTEGER PRIMARY KEY CHECK(singleton=1),
              reserved_position INTEGER NOT NULL CHECK(reserved_position>=0)
            );
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
            INSERT INTO shared_anchor_meta VALUES(1,0);
            """
        )
        return q

    def make_weakened_db(self, target):
        q = sqlite3.connect(":memory:", isolation_level=None)
        schemas = {
            "meta": """
                CREATE TABLE shared_anchor_meta(singleton INTEGER,reserved_position INTEGER);
            """,
            "intent_id": """
                CREATE TABLE shared_anchor_intents(
                  intent_id TEXT, component_id TEXT NOT NULL, intent_type TEXT NOT NULL,
                  payload_digest TEXT NOT NULL, provider_id TEXT NOT NULL,
                  provider_generation INTEGER NOT NULL, predecessor_position INTEGER NOT NULL,
                  position INTEGER NOT NULL UNIQUE, request_id TEXT NOT NULL UNIQUE,
                  status TEXT NOT NULL, receipt_binding TEXT
                );
            """,
            "position": """
                CREATE TABLE shared_anchor_intents(
                  intent_id TEXT PRIMARY KEY, component_id TEXT NOT NULL, intent_type TEXT NOT NULL,
                  payload_digest TEXT NOT NULL, provider_id TEXT NOT NULL,
                  provider_generation INTEGER NOT NULL, predecessor_position INTEGER NOT NULL,
                  position INTEGER NOT NULL, request_id TEXT NOT NULL UNIQUE,
                  status TEXT NOT NULL, receipt_binding TEXT
                );
            """,
            "request_id": """
                CREATE TABLE shared_anchor_intents(
                  intent_id TEXT PRIMARY KEY, component_id TEXT NOT NULL, intent_type TEXT NOT NULL,
                  payload_digest TEXT NOT NULL, provider_id TEXT NOT NULL,
                  provider_generation INTEGER NOT NULL, predecessor_position INTEGER NOT NULL,
                  position INTEGER NOT NULL UNIQUE, request_id TEXT NOT NULL,
                  status TEXT NOT NULL, receipt_binding TEXT
                );
            """,
            "watermark": """
                CREATE TABLE component_anchor_watermarks(component_id TEXT,position INTEGER);
            """,
            "receipt": """
                CREATE TABLE asymmetric_provider_receipts(
                  request_id TEXT, provider_id TEXT NOT NULL, generation INTEGER NOT NULL,
                  position INTEGER NOT NULL, kind TEXT NOT NULL, challenge TEXT NOT NULL,
                  signature TEXT NOT NULL, stable_binding TEXT NOT NULL
                );
            """,
        }
        q.executescript(
            (schemas["meta"] if target == "meta" else """
                CREATE TABLE shared_anchor_meta(
                  singleton INTEGER PRIMARY KEY CHECK(singleton=1),
                  reserved_position INTEGER NOT NULL CHECK(reserved_position>=0)
                );
            """)
            + (schemas[target] if target in {"intent_id","position","request_id"} else """
                CREATE TABLE shared_anchor_intents(
                  intent_id TEXT PRIMARY KEY, component_id TEXT NOT NULL, intent_type TEXT NOT NULL,
                  payload_digest TEXT NOT NULL, provider_id TEXT NOT NULL,
                  provider_generation INTEGER NOT NULL, predecessor_position INTEGER NOT NULL,
                  position INTEGER NOT NULL UNIQUE, request_id TEXT NOT NULL UNIQUE,
                  status TEXT NOT NULL CHECK(status IN ('PREPARED','CONFIRMED')),
                  receipt_binding TEXT
                );
            """)
            + (schemas["watermark"] if target == "watermark" else """
                CREATE TABLE component_anchor_watermarks(
                  component_id TEXT PRIMARY KEY,
                  position INTEGER NOT NULL CHECK(position>=0)
                );
            """)
            + (schemas["receipt"] if target == "receipt" else """
                CREATE TABLE asymmetric_provider_receipts(
                  request_id TEXT PRIMARY KEY, provider_id TEXT NOT NULL, generation INTEGER NOT NULL,
                  position INTEGER NOT NULL, kind TEXT NOT NULL, challenge TEXT NOT NULL,
                  signature TEXT NOT NULL, stable_binding TEXT NOT NULL
                );
            """)
        )
        q.execute("INSERT INTO shared_anchor_meta VALUES(1,0)")
        return q

    def validate(self, q):
        q.execute("BEGIN IMMEDIATE")
        try:
            return validate_existing_mutable_state_locked(q)
        finally:
            q.rollback()

    def test_canonical_identity_constraints_are_accepted(self):
        self.assertTrue(self.validate(self.make_canonical_db()))

    def test_missing_identity_constraints_fail_closed_even_with_clean_rows(self):
        for target in ("meta", "intent_id", "position", "request_id", "watermark", "receipt"):
            with self.subTest(target=target):
                with self.assertRaises(AdoptionValidationError):
                    self.validate(self.make_weakened_db(target))


if __name__ == "__main__":
    unittest.main()
