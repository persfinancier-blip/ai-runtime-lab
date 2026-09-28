from __future__ import annotations

import os
import sqlite3
import tempfile
import unittest

from experiments.mutable_shared_anchor_writer.adoption_secondary_indexes import (
    AdoptionSecondaryIndexError,
    validate_secondary_index_collations,
)


_CANONICAL_SCHEMA = """
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
"""

_INSERT = (
    "intent-a",
    "component-b",
    "RECONCILE",
    "0" * 64,
    "provider-a",
    1,
    0,
    1,
    "request-a",
    "PREPARED",
    None,
)


def _create_legacy_db(index_sql: str) -> str:
    fd, path = tempfile.mkstemp(suffix=".sqlite")
    os.close(fd)
    q = sqlite3.connect(path)
    q.create_function("legacy_only", 1, lambda value: len(value or ""), deterministic=True)
    q.executescript(_CANONICAL_SCHEMA)
    q.execute(index_sql)
    q.commit()
    q.close()
    return path


class AdoptionSecondaryIndexExpressionPartialRegressionTests(unittest.TestCase):
    def test_legacy_expression_secondary_index_is_rejected(self):
        path = _create_legacy_db(
            "CREATE INDEX intents_component_expr "
            "ON shared_anchor_intents(legacy_only(component_id))"
        )
        try:
            reopened = sqlite3.connect(path)
            try:
                with self.assertRaisesRegex(sqlite3.OperationalError, "unknown function"):
                    reopened.execute(
                        "INSERT INTO shared_anchor_intents VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                        _INSERT,
                    )
            finally:
                reopened.close()

            verifier = sqlite3.connect(path)
            verifier.create_function(
                "legacy_only", 1, lambda value: len(value or ""), deterministic=True
            )
            try:
                verifier.execute("BEGIN IMMEDIATE")
                with self.assertRaisesRegex(
                    AdoptionSecondaryIndexError,
                    "uses an expression",
                ):
                    validate_secondary_index_collations(verifier)
                verifier.rollback()
            finally:
                verifier.close()
        finally:
            os.unlink(path)

    def test_legacy_partial_secondary_index_is_rejected(self):
        path = _create_legacy_db(
            "CREATE INDEX intents_component_partial "
            "ON shared_anchor_intents(component_id) "
            "WHERE legacy_only(component_id) > 0"
        )
        try:
            reopened = sqlite3.connect(path)
            try:
                with self.assertRaisesRegex(sqlite3.OperationalError, "unknown function"):
                    reopened.execute(
                        "INSERT INTO shared_anchor_intents VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                        _INSERT,
                    )
            finally:
                reopened.close()

            verifier = sqlite3.connect(path)
            verifier.create_function(
                "legacy_only", 1, lambda value: len(value or ""), deterministic=True
            )
            try:
                verifier.execute("BEGIN IMMEDIATE")
                with self.assertRaisesRegex(
                    AdoptionSecondaryIndexError,
                    "is partial",
                ):
                    validate_secondary_index_collations(verifier)
                verifier.rollback()
            finally:
                verifier.close()
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
