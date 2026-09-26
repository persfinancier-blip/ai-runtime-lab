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


class AdoptionSecondaryIndexCollationRegressionTests(unittest.TestCase):
    def test_canonical_schema_and_binary_secondary_index_are_accepted(self):
        q = sqlite3.connect(":memory:")
        try:
            q.executescript(_CANONICAL_SCHEMA)
            q.execute(
                "CREATE INDEX intents_component_binary "
                "ON shared_anchor_intents(component_id COLLATE BINARY)"
            )
            q.execute("BEGIN IMMEDIATE")
            self.assertTrue(validate_secondary_index_collations(q))
            q.rollback()
        finally:
            q.close()

    def test_legacy_custom_collation_secondary_index_is_rejected(self):
        fd, path = tempfile.mkstemp(suffix=".sqlite")
        os.close(fd)
        try:
            q = sqlite3.connect(path)
            q.create_collation(
                "LEGACY_ONLY",
                lambda left, right: (left > right) - (left < right),
            )
            q.executescript(_CANONICAL_SCHEMA)
            q.execute(
                "CREATE INDEX intents_component_legacy "
                "ON shared_anchor_intents(component_id COLLATE LEGACY_ONLY)"
            )
            q.commit()
            q.close()

            # LAB-091 does not register a legacy-only collation on reopen. Before
            # this adoption guard, the schema could be accepted and the next
            # otherwise-valid supported INSERT would fail while maintaining the
            # inherited secondary index.
            reopened = sqlite3.connect(path)
            try:
                with self.assertRaisesRegex(
                    sqlite3.OperationalError,
                    "no such collation sequence: LEGACY_ONLY",
                ):
                    reopened.execute(
                        "INSERT INTO shared_anchor_intents VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                        (
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
                        ),
                    )
            finally:
                reopened.close()

            verifier = sqlite3.connect(path)
            verifier.create_collation(
                "LEGACY_ONLY",
                lambda left, right: (left > right) - (left < right),
            )
            try:
                verifier.execute("BEGIN IMMEDIATE")
                with self.assertRaisesRegex(
                    AdoptionSecondaryIndexError,
                    "non-BINARY collation",
                ):
                    validate_secondary_index_collations(verifier)
                verifier.rollback()
            finally:
                verifier.close()
        finally:
            if os.path.exists(path):
                os.unlink(path)


if __name__ == "__main__":
    unittest.main()
