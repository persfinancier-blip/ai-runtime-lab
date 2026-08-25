import sqlite3
import tempfile
import unittest
from pathlib import Path

from experiments.sqlite_schema_control.protocol import (
    BrokerOwnedDatabase,
    RestrictedSQLViolation,
)


def make_db(td):
    path = Path(td) / "authority.db"
    broker = BrokerOwnedDatabase(path)
    q = broker.owner_connection
    q.executescript(
        """
        CREATE TABLE authority(id INTEGER PRIMARY KEY, value TEXT NOT NULL);
        INSERT INTO authority VALUES(1,'trusted');
        CREATE TABLE audit_log(id INTEGER PRIMARY KEY, value TEXT NOT NULL);
        CREATE TRIGGER protect_authority
        BEFORE UPDATE ON authority
        BEGIN SELECT RAISE(ABORT,'protected'); END;
        """
    )
    q.commit()
    return path, broker


class RestrictedConnectionTests(unittest.TestCase):
    def test_select_and_read_pragma_are_allowed(self):
        with tempfile.TemporaryDirectory() as td:
            path, broker = make_db(td)
            try:
                with broker.restricted() as worker:
                    self.assertEqual(worker.query_all("SELECT value FROM authority"), [("trusted",)])
                    columns = worker.query_all("PRAGMA table_info(authority)")
                    self.assertEqual([row[1] for row in columns], ["id", "value"])
            finally:
                broker.close()

    def test_consequential_dml_is_denied(self):
        with tempfile.TemporaryDirectory() as td:
            path, broker = make_db(td)
            try:
                with broker.restricted() as worker:
                    for statement in (
                        "INSERT INTO audit_log VALUES(1,'x')",
                        "UPDATE authority SET value='evil' WHERE id=1",
                        "DELETE FROM authority WHERE id=1",
                    ):
                        with self.assertRaises(RestrictedSQLViolation):
                            worker.execute(statement)
            finally:
                broker.close()

    def test_schema_and_attachment_actions_are_denied(self):
        with tempfile.TemporaryDirectory() as td:
            path, broker = make_db(td)
            try:
                with broker.restricted() as worker:
                    for statement in (
                        "DROP TRIGGER protect_authority",
                        "CREATE TABLE attacker(x INTEGER)",
                        "ALTER TABLE authority ADD COLUMN pwned TEXT",
                        "ATTACH DATABASE ':memory:' AS attacker",
                    ):
                        with self.assertRaises(RestrictedSQLViolation):
                            worker.execute(statement)
            finally:
                broker.close()

    def test_write_pragma_is_denied(self):
        with tempfile.TemporaryDirectory() as td:
            path, broker = make_db(td)
            try:
                with broker.restricted() as worker:
                    with self.assertRaises(RestrictedSQLViolation):
                        worker.execute("PRAGMA user_version=7")
            finally:
                broker.close()

    def test_unrestricted_connection_is_explicit_negative_control(self):
        """Authorizer on one handle cannot secure the DB file from another handle."""
        with tempfile.TemporaryDirectory() as td:
            path, broker = make_db(td)
            try:
                attacker = sqlite3.connect(str(path))
                try:
                    attacker.execute("DROP TRIGGER protect_authority")
                    attacker.execute("UPDATE authority SET value='evil' WHERE id=1")
                    attacker.commit()
                finally:
                    attacker.close()
                self.assertEqual(
                    broker.owner_connection.execute("SELECT value FROM authority WHERE id=1").fetchone()[0],
                    "evil",
                )
            finally:
                broker.close()

    def test_wrapper_does_not_publish_authorizer_mutation_api(self):
        with tempfile.TemporaryDirectory() as td:
            path, broker = make_db(td)
            try:
                worker = broker.restricted()
                try:
                    self.assertFalse(hasattr(worker, "set_authorizer"))
                    self.assertFalse(hasattr(worker, "connection"))
                finally:
                    worker.close()
            finally:
                broker.close()


if __name__ == "__main__":
    unittest.main()
