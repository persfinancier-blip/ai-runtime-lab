import sqlite3
import unittest

from experiments.mutable_shared_anchor_writer.adoption_schema_domains import (
    AdoptionSchemaDomainError,
    validate_required_not_null_contract,
)


class AdoptionRestrictiveCheckRegressionTests(unittest.TestCase):
    def make_db(self, *, restrictive_check=False, omit_canonical_checks=False):
        q = sqlite3.connect(":memory:", isolation_level=None)
        meta_checks = "" if omit_canonical_checks else " CHECK(singleton=1)"
        reserved_check = "" if omit_canonical_checks else " CHECK(reserved_position>=0)"
        status_check = (
            "" if omit_canonical_checks else " CHECK(status IN ('PREPARED','CONFIRMED'))"
        )
        watermark_check = "" if omit_canonical_checks else " CHECK(position>=0)"
        component_check = (
            " CHECK(component_id='component-a')" if restrictive_check else ""
        )
        q.executescript(
            f"""
            CREATE TABLE shared_anchor_meta(
              singleton INTEGER PRIMARY KEY{meta_checks},
              reserved_position INTEGER NOT NULL{reserved_check}
            );
            CREATE TABLE shared_anchor_intents(
              intent_id TEXT PRIMARY KEY,
              component_id TEXT NOT NULL{component_check},
              intent_type TEXT NOT NULL,
              payload_digest TEXT NOT NULL,
              provider_id TEXT NOT NULL,
              provider_generation INTEGER NOT NULL,
              predecessor_position INTEGER NOT NULL,
              position INTEGER NOT NULL UNIQUE,
              request_id TEXT NOT NULL UNIQUE,
              status TEXT NOT NULL{status_check},
              receipt_binding TEXT
            );
            CREATE TABLE component_anchor_watermarks(
              component_id TEXT PRIMARY KEY,
              position INTEGER NOT NULL{watermark_check}
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
            return validate_required_not_null_contract(q)
        finally:
            q.rollback()

    def test_canonical_checks_are_accepted(self):
        self.assertTrue(self.validate(self.make_db()))

    def test_missing_canonical_checks_remain_guard_compatible(self):
        self.assertTrue(self.validate(self.make_db(omit_canonical_checks=True)))

    def test_extra_check_that_can_reject_supported_write_is_rejected(self):
        q = self.make_db(restrictive_check=True)
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
        with self.assertRaises(AdoptionSchemaDomainError):
            self.validate(q)


if __name__ == "__main__":
    unittest.main()
