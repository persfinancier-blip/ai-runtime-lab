import sqlite3
import tempfile
import unittest
from pathlib import Path

from experiments.mutable_shared_anchor_writer.restart_safe_schema import (
    initialize_shared_anchor_schema,
)


META_INSERT_TRIGGER = """CREATE TRIGGER lab091_v2_meta_no_insert
BEFORE INSERT ON shared_anchor_meta
BEGIN SELECT RAISE(ABORT,'LAB-091 meta singleton already initialized'); END"""


class RestartSafeSchemaTests(unittest.TestCase):
    def test_fresh_database_initializes_singleton(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            q = sqlite3.connect(path, isolation_level=None)
            initialize_shared_anchor_schema(q)
            self.assertEqual(
                q.execute(
                    "SELECT singleton,reserved_position FROM shared_anchor_meta"
                ).fetchall(),
                [(1, 0)],
            )
            q.close()

    def test_persisted_insert_guard_does_not_break_normal_reopen(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            q = sqlite3.connect(path, isolation_level=None)
            initialize_shared_anchor_schema(q)
            q.execute(META_INSERT_TRIGGER)
            q.close()

            reopened = sqlite3.connect(path, isolation_level=None)
            initialize_shared_anchor_schema(reopened)
            self.assertEqual(
                reopened.execute(
                    "SELECT singleton,reserved_position FROM shared_anchor_meta"
                ).fetchall(),
                [(1, 0)],
            )
            reopened.close()

    def test_missing_singleton_under_persisted_guard_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            q = sqlite3.connect(path, isolation_level=None)
            initialize_shared_anchor_schema(q)
            q.execute(META_INSERT_TRIGGER)
            q.execute("DROP TRIGGER lab091_v2_meta_no_insert")
            q.execute("DELETE FROM shared_anchor_meta WHERE singleton=1")
            q.execute(META_INSERT_TRIGGER)
            q.close()

            reopened = sqlite3.connect(path, isolation_level=None)
            with self.assertRaises(sqlite3.IntegrityError):
                initialize_shared_anchor_schema(reopened)
            self.assertFalse(reopened.in_transaction)
            self.assertEqual(
                reopened.execute("SELECT COUNT(*) FROM shared_anchor_meta").fetchone()[0],
                0,
            )
            reopened.close()

    def test_historical_lab080_insert_or_ignore_pattern_reproduces_failure(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            q = sqlite3.connect(path, isolation_level=None)
            initialize_shared_anchor_schema(q)
            q.execute(META_INSERT_TRIGGER)
            q.close()

            reopened = sqlite3.connect(path, isolation_level=None)
            with self.assertRaises(sqlite3.IntegrityError):
                reopened.execute(
                    "INSERT OR IGNORE INTO shared_anchor_meta VALUES(1,0)"
                )
            reopened.close()


if __name__ == "__main__":
    unittest.main()
