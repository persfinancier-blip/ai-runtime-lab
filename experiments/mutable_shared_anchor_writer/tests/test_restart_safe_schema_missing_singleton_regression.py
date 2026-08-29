from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from experiments.mutable_shared_anchor_writer.restart_safe_schema import (
    RestartSchemaError,
    initialize_shared_anchor_schema,
)


_CANONICAL_SCHEMA_WITHOUT_SINGLETON = """
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
"""


class RestartSafeSchemaMissingSingletonRegression(unittest.TestCase):
    def _connect(self, path: Path):
        return sqlite3.connect(path, isolation_level=None)

    def test_fresh_database_gets_initial_singleton(self):
        with tempfile.TemporaryDirectory() as td:
            q = self._connect(Path(td) / "fresh.db")
            try:
                initialize_shared_anchor_schema(q)
                self.assertEqual(
                    [(1, 0)],
                    q.execute(
                        "SELECT singleton,reserved_position FROM shared_anchor_meta"
                    ).fetchall(),
                )
            finally:
                q.close()

    def test_preexisting_mutable_schema_missing_singleton_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            q = self._connect(Path(td) / "legacy.db")
            try:
                q.executescript(_CANONICAL_SCHEMA_WITHOUT_SINGLETON)
                with self.assertRaisesRegex(
                    RestartSchemaError,
                    "preexisting mutable shared-anchor schema is missing metadata singleton",
                ):
                    initialize_shared_anchor_schema(q)
                self.assertEqual(
                    [], q.execute("SELECT * FROM shared_anchor_meta").fetchall()
                )
            finally:
                q.close()


if __name__ == "__main__":
    unittest.main()
