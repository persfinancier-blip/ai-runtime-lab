from __future__ import annotations

import sqlite3
import unittest

from experiments.mutable_shared_anchor_writer.adoption_extra_columns import (
    AdoptionExtraColumnError,
    validate_no_required_extra_columns,
)


class RequiredExtraColumnAdoptionRegression(unittest.TestCase):
    def _schema(self, *, extra_intent_column: str = ""):
        q = sqlite3.connect(":memory:")
        q.executescript(
            f"""
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
              {extra_intent_column}
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
        q.execute("BEGIN IMMEDIATE")
        return q

    def test_canonical_schema_is_accepted(self):
        q = self._schema()
        try:
            self.assertTrue(validate_no_required_extra_columns(q))
        finally:
            q.rollback()
            q.close()

    def test_omittable_extra_columns_remain_accepted(self):
        for declaration in (", legacy_note TEXT", ", legacy_tag TEXT NOT NULL DEFAULT 'x'"):
            with self.subTest(declaration=declaration):
                q = self._schema(extra_intent_column=declaration)
                try:
                    self.assertTrue(validate_no_required_extra_columns(q))
                finally:
                    q.rollback()
                    q.close()

    def test_required_extra_column_is_rejected_before_supported_insert(self):
        q = self._schema(extra_intent_column=", extra_tag TEXT NOT NULL")
        try:
            with self.assertRaises(AdoptionExtraColumnError):
                validate_no_required_extra_columns(q)
            q.rollback()

            with self.assertRaisesRegex(sqlite3.IntegrityError, "extra_tag"):
                q.execute(
                    """INSERT INTO shared_anchor_intents(
                      intent_id,component_id,intent_type,payload_digest,provider_id,
                      provider_generation,predecessor_position,position,request_id,
                      status,receipt_binding
                    ) VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
                    (
                        "intent-1",
                        "component-b",
                        "RECONCILE",
                        "0" * 64,
                        "provider-1",
                        1,
                        0,
                        1,
                        "request-1",
                        "PREPARED",
                        None,
                    ),
                )
        finally:
            if q.in_transaction:
                q.rollback()
            q.close()


if __name__ == "__main__":
    unittest.main()
