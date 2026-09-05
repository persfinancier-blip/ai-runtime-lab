import sqlite3
import unittest

from experiments.mutable_shared_anchor_writer.adoption_schema_domains import (
    AdoptionSchemaDomainError,
    validate_required_not_null_contract,
)


class AdoptionRestrictiveUniqueRegressionTests(unittest.TestCase):
    def make_db(self, *, nocase_intent_pk=False, extra_unique=False):
        q = sqlite3.connect(":memory:", isolation_level=None)
        intent_pk = (
            "intent_id TEXT COLLATE NOCASE PRIMARY KEY"
            if nocase_intent_pk
            else "intent_id TEXT PRIMARY KEY"
        )
        q.executescript(
            f"""
            CREATE TABLE shared_anchor_meta(
              singleton INTEGER PRIMARY KEY CHECK(singleton=1),
              reserved_position INTEGER NOT NULL CHECK(reserved_position>=0)
            );
            CREATE TABLE shared_anchor_intents(
              {intent_pk},
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
            """
        )
        if nocase_intent_pk:
            q.execute(
                "CREATE UNIQUE INDEX intent_id_binary_overlay "
                "ON shared_anchor_intents(intent_id COLLATE BINARY)"
            )
        if extra_unique:
            q.execute(
                "CREATE UNIQUE INDEX intent_payload_extra "
                "ON shared_anchor_intents(payload_digest)"
            )
        return q

    def validate(self, q):
        q.execute("BEGIN IMMEDIATE")
        try:
            return validate_required_not_null_contract(q)
        finally:
            q.rollback()

    def test_canonical_unique_contract_is_accepted(self):
        self.assertTrue(self.validate(self.make_db()))

    def test_nocase_primary_key_plus_binary_overlay_is_rejected(self):
        q = self.make_db(nocase_intent_pk=True)
        q.execute(
            "INSERT INTO shared_anchor_intents VALUES(?,?,?,?,?,?,?,?,?,'PREPARED',NULL)",
            (
                "Alpha",
                "component",
                "migration",
                "a" * 64,
                "provider",
                1,
                0,
                1,
                "b" * 64,
            ),
        )
        with self.assertRaises(sqlite3.IntegrityError):
            q.execute(
                "INSERT INTO shared_anchor_intents VALUES(?,?,?,?,?,?,?,?,?,'PREPARED',NULL)",
                (
                    "alpha",
                    "component-2",
                    "migration",
                    "c" * 64,
                    "provider",
                    1,
                    1,
                    2,
                    "d" * 64,
                ),
            )
        with self.assertRaises(AdoptionSchemaDomainError):
            self.validate(q)

    def test_extra_unique_constraint_that_can_reject_supported_writes_is_rejected(self):
        with self.assertRaises(AdoptionSchemaDomainError):
            self.validate(self.make_db(extra_unique=True))


if __name__ == "__main__":
    unittest.main()
