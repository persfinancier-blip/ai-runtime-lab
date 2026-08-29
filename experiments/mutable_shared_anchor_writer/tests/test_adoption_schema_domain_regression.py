import sqlite3
import unittest

from experiments.mutable_shared_anchor_writer.adoption_schema_domains import (
    AdoptionSchemaDomainError,
    validate_required_not_null_contract,
)


class AdoptionSchemaDomainRegressionTests(unittest.TestCase):
    def make_db(self, *, weaken_component_id=False):
        q = sqlite3.connect(":memory:", isolation_level=None)
        component_decl = "TEXT" if weaken_component_id else "TEXT NOT NULL"
        q.executescript(
            f"""
            CREATE TABLE shared_anchor_meta(
              singleton INTEGER PRIMARY KEY CHECK(singleton=1),
              reserved_position INTEGER NOT NULL CHECK(reserved_position>=0)
            );
            INSERT INTO shared_anchor_meta VALUES(1,0);
            CREATE TABLE shared_anchor_intents(
              intent_id TEXT PRIMARY KEY,
              component_id {component_decl},
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
            """
        )
        return q

    def validate(self, q):
        q.execute("BEGIN IMMEDIATE")
        try:
            return validate_required_not_null_contract(q)
        finally:
            q.rollback()

    def test_canonical_not_null_contract_is_accepted(self):
        self.assertTrue(self.validate(self.make_db()))

    def test_missing_component_not_null_fails_closed_on_clean_database(self):
        with self.assertRaises(AdoptionSchemaDomainError):
            self.validate(self.make_db(weaken_component_id=True))


if __name__ == "__main__":
    unittest.main()
