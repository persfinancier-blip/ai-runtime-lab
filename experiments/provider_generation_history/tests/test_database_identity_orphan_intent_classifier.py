from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from experiments.provider_generation_history import database_identity as dbid


class LAB095PublicClassifierOrphanIntentTests(unittest.TestCase):
    def _create_anchor_table(self, q: sqlite3.Connection) -> None:
        q.execute(
            """CREATE TABLE shared_anchor_intents(
              intent_id TEXT PRIMARY KEY,
              component_id TEXT NOT NULL,
              intent_type TEXT NOT NULL,
              payload_digest TEXT NOT NULL,
              provider_id TEXT NOT NULL,
              provider_generation INTEGER NOT NULL,
              predecessor_position INTEGER NOT NULL,
              position INTEGER NOT NULL,
              request_id TEXT NOT NULL,
              status TEXT NOT NULL,
              receipt_binding TEXT
            )"""
        )

    def _insert_orphan(self, q: sqlite3.Connection, *, status: str) -> None:
        q.execute(
            "INSERT INTO shared_anchor_intents VALUES(?,?,?,?,?,?,?,?,?,?,?)",
            (
                dbid.IDENTITY_INTENT_ID,
                dbid.IDENTITY_COMPONENT,
                "migration",
                "11" * 32,
                "provider-alpha",
                1,
                0,
                1,
                "shared-anchor:1:" + ("22" * 32),
                status,
                None if status == "PREPARED" else "33" * 32,
            ),
        )

    def test_zero_custody_without_identity_intent_is_absent(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "empty.sqlite"
            q = sqlite3.connect(path, isolation_level=None)
            self._create_anchor_table(q)
            dbid.install_custody_schema(q)
            q.close()
            self.assertEqual(
                dbid.classify_identity_custody(path),
                dbid.IdentityCustodyState.ABSENT,
            )

    def test_orphan_prepared_identity_intent_is_corrupt(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "prepared.sqlite"
            q = sqlite3.connect(path, isolation_level=None)
            self._create_anchor_table(q)
            dbid.install_custody_schema(q)
            self._insert_orphan(q, status="PREPARED")
            q.close()
            self.assertEqual(
                dbid.classify_identity_custody(path),
                dbid.IdentityCustodyState.CORRUPT,
            )

    def test_orphan_confirmed_identity_intent_is_corrupt(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "confirmed.sqlite"
            q = sqlite3.connect(path, isolation_level=None)
            self._create_anchor_table(q)
            dbid.install_custody_schema(q)
            self._insert_orphan(q, status="CONFIRMED")
            q.close()
            self.assertEqual(
                dbid.classify_identity_custody(path),
                dbid.IdentityCustodyState.CORRUPT,
            )

    def test_orphan_identity_intent_without_custody_relation_is_corrupt(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "no-custody-relation.sqlite"
            q = sqlite3.connect(path, isolation_level=None)
            self._create_anchor_table(q)
            self._insert_orphan(q, status="PREPARED")
            q.close()
            self.assertEqual(
                dbid.classify_identity_custody(path),
                dbid.IdentityCustodyState.CORRUPT,
            )


if __name__ == "__main__":
    unittest.main()
