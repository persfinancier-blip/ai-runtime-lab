import sqlite3
import unittest

from experiments.mutable_shared_anchor_writer.operation_permit import (
    OperationPermitError,
    PermitConnection,
    install_operation_permit_udf,
    one_shot_permit,
)


class OperationPermitPrimitiveTests(unittest.TestCase):
    def make_db(self):
        q = sqlite3.connect(":memory:", isolation_level=None, factory=PermitConnection)
        install_operation_permit_udf(q)
        q.executescript(
            """
            CREATE TABLE meta(singleton INTEGER PRIMARY KEY, value TEXT NOT NULL);
            INSERT INTO meta VALUES(1,'0');
            CREATE TRIGGER guarded_meta_update
            BEFORE UPDATE ON meta
            WHEN lab091_consume_permit('meta-update','1',OLD.value,NEW.value)!=1
            BEGIN SELECT RAISE(ABORT,'missing exact operation permit'); END;
            """
        )
        return q

    def test_unpermitted_write_is_blocked(self):
        q = self.make_db()
        q.execute("BEGIN IMMEDIATE")
        with self.assertRaises(sqlite3.IntegrityError):
            q.execute("UPDATE meta SET value='1' WHERE singleton=1")
        q.rollback()

    def test_exact_permit_allows_exact_transition(self):
        q = self.make_db()
        q.execute("BEGIN IMMEDIATE")
        with one_shot_permit(q, kind="meta-update", identity="1", old_value="0", new_value="1"):
            q.execute("UPDATE meta SET value='1' WHERE singleton=1")
        q.commit()
        self.assertEqual(q.execute("SELECT value FROM meta").fetchone()[0], "1")

    def test_permit_does_not_authorize_different_new_value(self):
        q = self.make_db()
        q.execute("BEGIN IMMEDIATE")
        with self.assertRaises(sqlite3.IntegrityError):
            with one_shot_permit(q, kind="meta-update", identity="1", old_value="0", new_value="1"):
                q.execute("UPDATE meta SET value='999' WHERE singleton=1")
        q.rollback()

    def test_permit_is_consumed_by_one_statement(self):
        q = self.make_db()
        q.execute("BEGIN IMMEDIATE")
        with one_shot_permit(q, kind="meta-update", identity="1", old_value="0", new_value="1"):
            q.execute("UPDATE meta SET value='1' WHERE singleton=1")
            with self.assertRaises(sqlite3.IntegrityError):
                q.execute("UPDATE meta SET value='1' WHERE singleton=1")
        q.rollback()

    def test_failed_statement_clears_permit(self):
        q = self.make_db()
        q.execute("BEGIN IMMEDIATE")
        with self.assertRaises(sqlite3.IntegrityError):
            with one_shot_permit(q, kind="meta-update", identity="1", old_value="0", new_value="1"):
                q.execute("UPDATE meta SET value='999' WHERE singleton=1")
        with self.assertRaises(sqlite3.IntegrityError):
            q.execute("UPDATE meta SET value='1' WHERE singleton=1")
        q.rollback()

    def test_permit_requires_transaction(self):
        q = self.make_db()
        with self.assertRaises(OperationPermitError):
            with one_shot_permit(q, kind="meta-update", identity="1", old_value="0", new_value="1"):
                pass


if __name__ == "__main__":
    unittest.main()
