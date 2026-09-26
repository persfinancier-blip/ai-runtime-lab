from __future__ import annotations

import sqlite3
import unittest

from experiments.mutable_shared_anchor_writer.adoption_schema_domains import (
    AdoptionSchemaDomainError,
    validate_required_not_null_contract,
)


def _create_schema(q, *, position_type: str = "INTEGER") -> None:
    q.execute(
        """CREATE TABLE shared_anchor_meta(
          singleton INTEGER PRIMARY KEY CHECK(singleton=1),
          reserved_position INTEGER NOT NULL CHECK(reserved_position>=0)
        )"""
    )
    q.execute(
        f"""CREATE TABLE shared_anchor_intents(
          intent_id TEXT PRIMARY KEY,
          component_id TEXT NOT NULL,
          intent_type TEXT NOT NULL,
          payload_digest TEXT NOT NULL,
          provider_id TEXT NOT NULL,
          provider_generation INTEGER NOT NULL,
          predecessor_position INTEGER NOT NULL,
          position {position_type} NOT NULL UNIQUE,
          request_id TEXT NOT NULL UNIQUE,
          status TEXT NOT NULL CHECK(status IN ('PREPARED','CONFIRMED')),
          receipt_binding TEXT
        )"""
    )
    q.execute(
        """CREATE TABLE component_anchor_watermarks(
          component_id TEXT PRIMARY KEY,
          position INTEGER NOT NULL CHECK(position>=0)
        )"""
    )


class AdoptionAffinityRegressionTests(unittest.TestCase):
    def test_canonical_affinity_is_accepted(self):
        q = sqlite3.connect(":memory:")
        _create_schema(q)
        q.execute("BEGIN IMMEDIATE")
        self.assertTrue(validate_required_not_null_contract(q))
        q.rollback()

    def test_text_affinity_for_integer_position_is_rejected(self):
        q = sqlite3.connect(":memory:")
        _create_schema(q, position_type="TEXT")
        q.execute("BEGIN IMMEDIATE")
        with self.assertRaises(AdoptionSchemaDomainError):
            validate_required_not_null_contract(q)
        q.rollback()

    def test_text_affinity_changes_new_value_before_before_trigger(self):
        q = sqlite3.connect(":memory:")
        q.execute("CREATE TABLE t(position TEXT NOT NULL)")
        seen = []
        q.create_function(
            "capture_new_position",
            1,
            lambda value: seen.append((value, type(value))) or 1,
        )
        q.execute(
            """CREATE TRIGGER capture BEFORE INSERT ON t
               BEGIN
                 SELECT capture_new_position(NEW.position);
               END"""
        )
        q.execute("INSERT INTO t(position) VALUES(?)", (1,))
        self.assertEqual(seen, [("1", str)])
        self.assertEqual(q.execute("SELECT typeof(position) FROM t").fetchone()[0], "text")


if __name__ == "__main__":
    unittest.main()
