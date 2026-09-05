import sqlite3
import tempfile
import unittest
from pathlib import Path


class UnsafeRawDmlBaseline(unittest.TestCase):
    def test_unrestricted_mutable_ledger_should_reject_raw_update_but_does_not(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            q = sqlite3.connect(path)
            q.executescript(
                """
                CREATE TABLE shared_anchor_meta(
                  singleton INTEGER PRIMARY KEY CHECK(singleton=1),
                  reserved_position INTEGER NOT NULL
                );
                INSERT INTO shared_anchor_meta VALUES(1,0);
                """
            )
            q.execute("UPDATE shared_anchor_meta SET reserved_position=99 WHERE singleton=1")
            q.commit()
            observed = q.execute(
                "SELECT reserved_position FROM shared_anchor_meta WHERE singleton=1"
            ).fetchone()[0]
            q.close()
            self.assertEqual(observed, 0, "unsafe raw DML changed authoritative mutable state")


if __name__ == "__main__":
    unittest.main()
