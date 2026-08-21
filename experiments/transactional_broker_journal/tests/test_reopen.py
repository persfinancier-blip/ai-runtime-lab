import sqlite3
import tempfile
import unittest
from pathlib import Path

from experiments.transactional_broker_journal.protocol import (
    CorruptJournal,
    Request,
    TransactionalJournal,
)
from experiments.transactional_broker_journal.reopen import reopen_journal


class ReopenTests(unittest.TestCase):
    def test_restart_after_rotation_loads_generation_from_sql_authority(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "journal.db"
            journal = TransactionalJournal(path, 1)
            self.assertEqual(journal.rotate(), 2)
            restarted = reopen_journal(path)
            self.assertEqual(restarted.generation(), 2)
            self.assertTrue(restarted.verify_durable())

    def test_restart_refuses_missing_journal_without_creating_it(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "missing.db"
            self.assertFalse(path.exists())
            with self.assertRaises(CorruptJournal):
                reopen_journal(path)
            self.assertFalse(path.exists())

    def test_restart_refuses_corrupt_meta(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "journal.db"
            TransactionalJournal(path, 1)
            q = sqlite3.connect(path)
            q.execute("PRAGMA ignore_check_constraints=ON")
            q.execute("UPDATE broker_meta SET credential_generation=0")
            q.commit()
            q.close()
            with self.assertRaises(CorruptJournal):
                reopen_journal(path)

    def test_restart_refuses_non_hex_request_digest(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "journal.db"
            journal = TransactionalJournal(path, 1)
            journal.reserve(Request("req-1", "task-1", "scope-1", 1, "payload"))
            q = sqlite3.connect(path)
            q.execute(
                "UPDATE broker_requests SET request_digest=? WHERE request_id='req-1'",
                ("z" * 64,),
            )
            q.commit()
            q.close()
            with self.assertRaises(CorruptJournal):
                journal.verify_durable()
            with self.assertRaises(CorruptJournal):
                reopen_journal(path)


if __name__ == "__main__":
    unittest.main()
