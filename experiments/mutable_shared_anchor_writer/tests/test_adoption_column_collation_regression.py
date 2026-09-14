from __future__ import annotations

import os
import sqlite3
import tempfile
import unittest

from experiments.mutable_shared_anchor_writer.adoption_column_collations import (
    AdoptionColumnCollationError,
    validate_resolvable_column_collations,
)


_INTENT_COLUMNS = """
  intent_id TEXT PRIMARY KEY,
  component_id TEXT NOT NULL,
  intent_type TEXT NOT NULL,
  payload_digest TEXT NOT NULL,
  provider_id TEXT NOT NULL,
  provider_generation INTEGER NOT NULL,
  predecessor_position INTEGER NOT NULL,
  position INTEGER NOT NULL UNIQUE,
  request_id TEXT NOT NULL UNIQUE,
  {status_decl},
  receipt_binding TEXT
"""


def _create_remaining_tables(q):
    q.execute(
        """CREATE TABLE component_anchor_watermarks(
          component_id TEXT PRIMARY KEY,
          position INTEGER NOT NULL CHECK(position>=0)
        )"""
    )
    q.execute(
        """CREATE TABLE asymmetric_provider_receipts(
          request_id TEXT PRIMARY KEY,
          provider_id TEXT NOT NULL,
          generation INTEGER NOT NULL,
          position INTEGER NOT NULL,
          kind TEXT NOT NULL,
          challenge TEXT NOT NULL,
          signature TEXT NOT NULL,
          stable_binding TEXT NOT NULL
        )"""
    )


class AdoptionColumnCollationRegression(unittest.TestCase):
    def test_canonical_binary_columns_are_accepted(self):
        q = sqlite3.connect(":memory:")
        try:
            q.execute(
                "CREATE TABLE shared_anchor_intents(" +
                _INTENT_COLUMNS.format(
                    status_decl="status TEXT NOT NULL CHECK(status IN ('PREPARED','CONFIRMED'))"
                ) + ")"
            )
            _create_remaining_tables(q)
            q.execute("BEGIN")
            self.assertTrue(validate_resolvable_column_collations(q))
            q.rollback()
        finally:
            q.close()

    def test_unavailable_persisted_status_collation_is_rejected_before_write(self):
        fd, path = tempfile.mkstemp(suffix=".sqlite3")
        os.close(fd)
        try:
            legacy = sqlite3.connect(path)
            legacy.create_collation(
                "LEGACY_ONLY", lambda left, right: (left > right) - (left < right)
            )
            legacy.execute(
                "CREATE TABLE shared_anchor_intents(" +
                _INTENT_COLUMNS.format(
                    status_decl="status TEXT COLLATE LEGACY_ONLY NOT NULL"
                ) + ")"
            )
            _create_remaining_tables(legacy)
            legacy.execute(
                """CREATE TRIGGER legacy_status_check
                BEFORE INSERT ON shared_anchor_intents
                WHEN NEW.status!='PREPARED'
                BEGIN SELECT RAISE(ABORT,'legacy bad status'); END"""
            )
            legacy.commit()
            legacy.close()

            q = sqlite3.connect(path)
            try:
                with self.assertRaisesRegex(
                    sqlite3.OperationalError, "no such collation sequence: LEGACY_ONLY"
                ):
                    q.execute(
                        """INSERT INTO shared_anchor_intents VALUES(
                        'intent-a','component-a','ANCHOR',?,
                        'provider-a',1,0,1,'request-a','PREPARED',NULL
                        )""",
                        ("a" * 64,),
                    )
                q.rollback()

                q.execute("BEGIN")
                with self.assertRaisesRegex(
                    AdoptionColumnCollationError,
                    "unavailable collation for shared_anchor_intents.status",
                ):
                    validate_resolvable_column_collations(q)
                q.rollback()
            finally:
                q.close()
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
