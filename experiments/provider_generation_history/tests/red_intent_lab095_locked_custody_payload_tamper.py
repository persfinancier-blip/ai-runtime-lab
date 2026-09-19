from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from experiments.provider_generation_history.database_identity import IdentityCustodyState
from experiments.provider_generation_history.database_identity_migration import (
    DatabaseIdentityMigrationError,
    prepare_database_identity,
)
from experiments.provider_generation_history.tests.test_database_identity_migration import (
    _History,
    _Ledger,
    _init_database,
)


class LockedCustodyPayloadTamperTests(unittest.TestCase):
    def test_prepared_custody_nonce_tamper_fails_closed_before_retry(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db.sqlite"
            _init_database(path)
            ledger = _Ledger(path)
            history = _History(path)

            self.assertEqual(
                prepare_database_identity(ledger, history),
                IdentityCustodyState.PREPARED,
            )

            q = sqlite3.connect(path)
            before = q.execute(
                """SELECT payload_digest,intent_request_id
                   FROM provider_history_database_identity WHERE singleton=1"""
            ).fetchone()
            q.execute(
                """UPDATE provider_history_database_identity
                   SET nonce_hex=? WHERE singleton=1""",
                ("ff" * 32,),
            )
            q.commit()
            q.close()

            # Retry must reject the now-incoherent custody tuple while the writer
            # lock is held. It must not create a replacement nonce/request.
            with mock.patch(
                "experiments.provider_generation_history.database_identity_migration.secrets.token_bytes",
                side_effect=AssertionError("replacement nonce must not be generated"),
            ):
                with self.assertRaisesRegex(
                    DatabaseIdentityMigrationError,
                    "identity custody is corrupt",
                ):
                    prepare_database_identity(ledger, history)

            q = sqlite3.connect(path)
            after = q.execute(
                """SELECT payload_digest,intent_request_id
                   FROM provider_history_database_identity WHERE singleton=1"""
            ).fetchone()
            intent_count = q.execute(
                "SELECT COUNT(*) FROM shared_anchor_intents"
            ).fetchone()[0]
            q.close()
            self.assertEqual(after, before)
            self.assertEqual(intent_count, 1)


if __name__ == "__main__":
    unittest.main()
