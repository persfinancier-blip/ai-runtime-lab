from __future__ import annotations

import sqlite3
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest import mock

from experiments.provider_generation_history.database_identity import (
    IDENTITY_COMPONENT,
    IDENTITY_INTENT_ID,
    IdentityCustodyState,
)
from experiments.provider_generation_history.database_identity_migration import (
    DatabaseIdentityMigrationError,
    prepare_database_identity,
)
from experiments.provider_generation_history.tests.test_database_identity_migration import (
    _History,
    _Ledger,
    _init_database,
)


class DatabaseIdentityMigrationRecoveryTests(unittest.TestCase):
    def test_crash_before_commit_rolls_back_schema_intent_tail_and_nonce(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db.sqlite"
            _init_database(path)
            ledger = _Ledger(path)
            history = _History(path)

            with mock.patch(
                "experiments.provider_generation_history.database_identity_migration.secrets.token_bytes",
                side_effect=RuntimeError("simulated crash before reservation commit"),
            ):
                with self.assertRaisesRegex(RuntimeError, "simulated crash"):
                    prepare_database_identity(ledger, history)

            q = sqlite3.connect(path)
            custody_relation = q.execute(
                "SELECT type FROM sqlite_master WHERE name='provider_history_database_identity'"
            ).fetchone()
            intent_count = q.execute(
                "SELECT COUNT(*) FROM shared_anchor_intents WHERE intent_id=?",
                (IDENTITY_INTENT_ID,),
            ).fetchone()[0]
            reserved = q.execute(
                "SELECT reserved_position FROM shared_anchor_meta WHERE singleton=1"
            ).fetchone()[0]
            q.close()
            self.assertIsNone(custody_relation)
            self.assertEqual(intent_count, 0)
            self.assertEqual(reserved, 0)

    def test_orphan_confirmed_identity_intent_is_corrupt_before_nonce_generation(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db.sqlite"
            _init_database(path)
            q = sqlite3.connect(path)
            q.execute(
                """INSERT INTO shared_anchor_intents
                   VALUES(?,?,?,?,?,?,?,?,?,'CONFIRMED',?)""",
                (
                    IDENTITY_INTENT_ID,
                    IDENTITY_COMPONENT,
                    "migration",
                    "a" * 64,
                    "provider-alpha",
                    1,
                    0,
                    1,
                    "orphan-confirmed-request",
                    "d" * 64,
                ),
            )
            q.execute(
                "UPDATE shared_anchor_meta SET reserved_position=1 WHERE singleton=1"
            )
            q.commit()
            q.close()

            with mock.patch(
                "experiments.provider_generation_history.database_identity_migration.secrets.token_bytes",
                side_effect=AssertionError("nonce generation must not occur"),
            ):
                with self.assertRaisesRegex(
                    DatabaseIdentityMigrationError,
                    "identity custody is corrupt",
                ):
                    prepare_database_identity(_Ledger(path), _History(path))

            q = sqlite3.connect(path)
            rows = q.execute(
                "SELECT intent_id,status FROM shared_anchor_intents"
            ).fetchall()
            reserved = q.execute(
                "SELECT reserved_position FROM shared_anchor_meta WHERE singleton=1"
            ).fetchone()[0]
            q.close()
            self.assertEqual(rows, [(IDENTITY_INTENT_ID, "CONFIRMED")])
            self.assertEqual(reserved, 1)

    def test_concurrent_installers_converge_on_one_nonce_and_request(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db.sqlite"
            _init_database(path)
            barrier = threading.Barrier(2)

            def install_once():
                ledger = _Ledger(path)
                history = _History(path)
                barrier.wait(timeout=5)
                return prepare_database_identity(ledger, history)

            with ThreadPoolExecutor(max_workers=2) as pool:
                results = list(pool.map(lambda _: install_once(), range(2)))

            self.assertEqual(results, [IdentityCustodyState.PREPARED] * 2)
            q = sqlite3.connect(path)
            custody = q.execute(
                """SELECT nonce_hex,intent_request_id
                   FROM provider_history_database_identity"""
            ).fetchall()
            intents = q.execute(
                """SELECT intent_id,request_id,status,position
                   FROM shared_anchor_intents WHERE intent_id=?""",
                (IDENTITY_INTENT_ID,),
            ).fetchall()
            reserved = q.execute(
                "SELECT reserved_position FROM shared_anchor_meta WHERE singleton=1"
            ).fetchone()[0]
            q.close()
            self.assertEqual(len(custody), 1)
            self.assertEqual(len(intents), 1)
            self.assertEqual(custody[0][1], intents[0][1])
            self.assertEqual(intents[0][2:], ("PREPARED", 1))
            self.assertEqual(reserved, 1)

    def test_legacy_history_reserves_exactly_next_shared_anchor_position(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db.sqlite"
            _init_database(path)
            q = sqlite3.connect(path)
            q.execute(
                """INSERT INTO shared_anchor_intents
                   VALUES(?,?,?,?,?,?,?,?,?,'CONFIRMED',?)""",
                (
                    "legacy:confirmed:1",
                    "legacy-component",
                    "legacy-event",
                    "e" * 64,
                    "provider-alpha",
                    1,
                    0,
                    1,
                    "legacy-request-1",
                    "f" * 64,
                ),
            )
            q.execute(
                "UPDATE shared_anchor_meta SET reserved_position=1 WHERE singleton=1"
            )
            q.commit()
            q.close()

            self.assertEqual(
                prepare_database_identity(_Ledger(path), _History(path)),
                IdentityCustodyState.PREPARED,
            )

            q = sqlite3.connect(path)
            identity = q.execute(
                """SELECT predecessor_position,position,status,request_id
                   FROM shared_anchor_intents WHERE intent_id=?""",
                (IDENTITY_INTENT_ID,),
            ).fetchone()
            custody_request = q.execute(
                "SELECT intent_request_id FROM provider_history_database_identity"
            ).fetchone()[0]
            reserved = q.execute(
                "SELECT reserved_position FROM shared_anchor_meta WHERE singleton=1"
            ).fetchone()[0]
            legacy = q.execute(
                "SELECT status,position FROM shared_anchor_intents WHERE intent_id='legacy:confirmed:1'"
            ).fetchone()
            q.close()
            self.assertEqual(identity[:3], (1, 2, "PREPARED"))
            self.assertEqual(identity[3], custody_request)
            self.assertEqual(reserved, 2)
            self.assertEqual(legacy, ("CONFIRMED", 1))


if __name__ == "__main__":
    unittest.main()
