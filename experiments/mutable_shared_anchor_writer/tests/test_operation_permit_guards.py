import sqlite3
import unittest

from experiments.mutable_shared_anchor_writer.operation_permit import (
    PermitConnection,
    install_operation_permit_udf,
    one_shot_permit,
)
from experiments.mutable_shared_anchor_writer.operation_permit_guards import (
    install_operation_scoped_guards,
)


class OperationScopedGuardTests(unittest.TestCase):
    def make(self):
        q = sqlite3.connect(":memory:", isolation_level=None, factory=PermitConnection)
        install_operation_permit_udf(q)
        q.executescript(
            """
            CREATE TABLE shared_anchor_meta(
              singleton INTEGER PRIMARY KEY CHECK(singleton=1),
              reserved_position INTEGER NOT NULL CHECK(reserved_position>=0)
            );
            INSERT INTO shared_anchor_meta VALUES(1,0);
            CREATE TABLE component_anchor_watermarks(
              component_id TEXT PRIMARY KEY,
              position INTEGER NOT NULL
            );
            INSERT INTO component_anchor_watermarks VALUES('component-A',1);
            """
        )
        q.execute("BEGIN IMMEDIATE")
        install_operation_scoped_guards(q)
        q.commit()
        return q

    def test_broad_transaction_cannot_jump_meta_tail(self):
        q = self.make()
        q.execute("BEGIN IMMEDIATE")
        with self.assertRaises(sqlite3.IntegrityError):
            q.execute("UPDATE shared_anchor_meta SET reserved_position=999 WHERE singleton=1")
        q.rollback()

    def test_exact_meta_permit_allows_only_exact_cas(self):
        q = self.make()
        q.execute("BEGIN IMMEDIATE")
        with one_shot_permit(q, kind="meta-update", identity="1", old_value="0", new_value="1"):
            q.execute("UPDATE shared_anchor_meta SET reserved_position=1 WHERE singleton=1 AND reserved_position=0")
        with self.assertRaises(sqlite3.IntegrityError):
            q.execute("UPDATE shared_anchor_meta SET reserved_position=999 WHERE singleton=1")
        q.commit()
        self.assertEqual(q.execute("SELECT reserved_position FROM shared_anchor_meta").fetchone()[0], 1)

    def test_broad_transaction_cannot_jump_watermark(self):
        q = self.make()
        q.execute("BEGIN IMMEDIATE")
        with self.assertRaises(sqlite3.IntegrityError):
            q.execute("UPDATE component_anchor_watermarks SET position=999 WHERE component_id='component-A'")
        q.rollback()

    def test_exact_watermark_update_permit_is_one_shot(self):
        q = self.make()
        q.execute("BEGIN IMMEDIATE")
        with one_shot_permit(q, kind="watermark-update", identity="component-A", old_value="1", new_value="2"):
            q.execute("UPDATE component_anchor_watermarks SET position=2 WHERE component_id='component-A' AND position=1")
        with self.assertRaises(sqlite3.IntegrityError):
            q.execute("UPDATE component_anchor_watermarks SET position=3 WHERE component_id='component-A'")
        q.commit()

    def test_exact_watermark_insert_permit(self):
        q = self.make()
        q.execute("BEGIN IMMEDIATE")
        with one_shot_permit(q, kind="watermark-insert", identity="component-B", old_value="", new_value="7"):
            q.execute("INSERT INTO component_anchor_watermarks VALUES('component-B',7)")
        with self.assertRaises(sqlite3.IntegrityError):
            q.execute("INSERT INTO component_anchor_watermarks VALUES('component-C',8)")
        q.commit()

    def test_wrong_new_value_does_not_consume_then_grant(self):
        q = self.make()
        q.execute("BEGIN IMMEDIATE")
        with self.assertRaises(sqlite3.IntegrityError):
            with one_shot_permit(q, kind="meta-update", identity="1", old_value="0", new_value="1"):
                q.execute("UPDATE shared_anchor_meta SET reserved_position=999 WHERE singleton=1")
        with self.assertRaises(sqlite3.IntegrityError):
            q.execute("UPDATE shared_anchor_meta SET reserved_position=1 WHERE singleton=1")
        q.rollback()


if __name__ == "__main__":
    unittest.main()
