from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from experiments.provider_generation_history import database_identity as dbid


class LAB095DatabaseIdentityAuditTests(unittest.TestCase):
    def test_absent_classifier_does_not_create_database(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "missing.sqlite"
            self.assertFalse(path.exists())
            self.assertEqual(
                dbid.classify_identity_custody(path),
                dbid.IdentityCustodyState.ABSENT,
            )
            self.assertFalse(path.exists())

    def test_same_name_noncanonical_custody_schema_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "altered.sqlite"
            q = sqlite3.connect(path, isolation_level=None)
            q.execute(
                """CREATE TABLE provider_history_database_identity(
                  singleton INTEGER PRIMARY KEY,
                  status TEXT NOT NULL,
                  nonce_hex TEXT NOT NULL,
                  bootstrap_generation_id TEXT NOT NULL,
                  payload_digest TEXT NOT NULL,
                  intent_request_id TEXT NOT NULL,
                  provider_id TEXT,
                  provider_generation INTEGER,
                  position INTEGER,
                  receipt_binding TEXT,
                  logical_database_identity_digest TEXT
                )"""
            )
            q.close()
            self.assertEqual(
                dbid.classify_identity_custody(path),
                dbid.IdentityCustodyState.CORRUPT,
            )


if __name__ == "__main__":
    unittest.main()
