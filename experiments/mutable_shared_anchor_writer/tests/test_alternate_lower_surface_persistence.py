import sqlite3
import tempfile
import unittest
from pathlib import Path

from experiments.mutable_shared_anchor_writer.full_operation_guards import (
    install_full_operation_guards,
)
from experiments.mutable_shared_anchor_writer.operation_permit import (
    PermitConnection,
    install_operation_permit_udf,
)
from experiments.mutable_shared_anchor_writer.row_tokens import install_row_token_udfs


class AlternateLowerSurfacePersistenceTests(unittest.TestCase):
    def make_db(self, td):
        path = Path(td) / "authority.db"
        q = sqlite3.connect(path, isolation_level=None, factory=PermitConnection)
        install_operation_permit_udf(q)
        install_row_token_udfs(q)
        q.executescript(
            """
            CREATE TABLE shared_anchor_meta(
              singleton INTEGER PRIMARY KEY CHECK(singleton=1),
              reserved_position INTEGER NOT NULL CHECK(reserved_position>=0)
            );
            INSERT INTO shared_anchor_meta VALUES(1,0);

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
        )
        q.execute("BEGIN IMMEDIATE")
        install_full_operation_guards(q)
        q.commit()
        q.close()
        return path

    def assert_lower_connection_cannot_write(self, q):
        statements = (
            ("UPDATE shared_anchor_meta SET reserved_position=1 WHERE singleton=1", ()),
            (
                "INSERT INTO shared_anchor_intents VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                (
                    "intent-1",
                    "component-A",
                    "migration",
                    "d" * 64,
                    "anchor-A",
                    1,
                    0,
                    1,
                    "request-1",
                    "PREPARED",
                    None,
                ),
            ),
            ("INSERT INTO component_anchor_watermarks VALUES('component-A',0)", ()),
            (
                "INSERT INTO asymmetric_provider_receipts VALUES(?,?,?,?,?,?,?,?)",
                (
                    "request-1",
                    "anchor-A",
                    1,
                    1,
                    "RECONCILE",
                    "challenge",
                    "signature",
                    "b" * 64,
                ),
            ),
        )
        for sql, params in statements:
            with self.assertRaises(sqlite3.DatabaseError):
                q.execute(sql, params)
            q.rollback()

        self.assertEqual(
            q.execute(
                "SELECT reserved_position FROM shared_anchor_meta WHERE singleton=1"
            ).fetchone()[0],
            0,
        )
        self.assertEqual(q.execute("SELECT COUNT(*) FROM shared_anchor_intents").fetchone()[0], 0)
        self.assertEqual(
            q.execute("SELECT COUNT(*) FROM component_anchor_watermarks").fetchone()[0], 0
        )
        self.assertEqual(
            q.execute("SELECT COUNT(*) FROM asymmetric_provider_receipts").fetchone()[0], 0
        )

    def test_plain_lab080_style_connection_fails_closed_after_guard_install(self):
        with tempfile.TemporaryDirectory() as td:
            path = self.make_db(td)
            q = sqlite3.connect(path)
            try:
                self.assert_lower_connection_cannot_write(q)
            finally:
                q.close()

    def test_legacy_boolean_udf_does_not_restore_broad_write_authority(self):
        with tempfile.TemporaryDirectory() as td:
            path = self.make_db(td)
            q = sqlite3.connect(path)
            q.create_function("lab091_writer_authorized", 0, lambda: 1)
            try:
                self.assert_lower_connection_cannot_write(q)
            finally:
                q.close()


if __name__ == "__main__":
    unittest.main()
