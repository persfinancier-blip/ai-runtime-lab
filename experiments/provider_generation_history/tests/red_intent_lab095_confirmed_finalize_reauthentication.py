from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from experiments.provider_generation_history.database_identity import IDENTITY_INTENT_ID
from experiments.provider_generation_history.database_identity_migration import (
    DatabaseIdentityMigrationError,
    migrate_database_identity,
)
from experiments.provider_generation_history.tests.test_database_identity_migration import (
    _History,
    _Ledger,
    _init_database,
)


class _AuthenticatedThenTamperLedger(_Ledger):
    """Model the post-reauthentication / pre-finalize SQLite race.

    The returned snapshot represents what a real SharedAnchorLedger.execute()
    reauthenticated.  The durable row is then changed before LAB-095 opens its
    local finalization transaction.
    """

    def execute(self, intent, *, timeout_after_commit=False):
        q = sqlite3.connect(self.path, timeout=5, isolation_level=None)
        q.execute("BEGIN IMMEDIATE")
        row = q.execute(
            """SELECT intent_id,component_id,intent_type,payload_digest,provider_id,
                      provider_generation,predecessor_position,position,request_id,
                      status,receipt_binding
               FROM shared_anchor_intents WHERE intent_id=?""",
            (intent.intent_id,),
        ).fetchone()
        if row is None:
            q.rollback()
            q.close()
            raise AssertionError("identity intent disappeared")
        if row[9] == "PREPARED":
            q.execute(
                """UPDATE shared_anchor_intents
                   SET status='CONFIRMED',receipt_binding=?
                   WHERE intent_id=?""",
                ("d" * 64, intent.intent_id),
            )
        q.commit()
        authenticated = q.execute(
            """SELECT intent_id,component_id,intent_type,payload_digest,provider_id,
                      provider_generation,predecessor_position,position,request_id,
                      status,receipt_binding
               FROM shared_anchor_intents WHERE intent_id=?""",
            (intent.intent_id,),
        ).fetchone()
        q.close()

        fields = (
            "intent_id component_id intent_type payload_digest provider_id "
            "provider_generation predecessor_position position request_id "
            "status receipt_binding"
        ).split()
        authenticated_snapshot = SimpleNamespace(**dict(zip(fields, authenticated)))

        # Simulate a same-host SQLite writer changing authority-bearing fields
        # after external reauthentication but before LAB-095 local finalization.
        q = sqlite3.connect(self.path, timeout=5, isolation_level=None)
        q.execute("BEGIN IMMEDIATE")
        q.execute(
            """UPDATE shared_anchor_intents
               SET provider_id=?,provider_generation=?,position=?,receipt_binding=?
               WHERE intent_id=? AND status='CONFIRMED'""",
            (
                "attacker-provider",
                99,
                99,
                "e" * 64,
                IDENTITY_INTENT_ID,
            ),
        )
        q.commit()
        q.close()
        return authenticated_snapshot


class ConfirmedFinalizeReauthenticationTests(unittest.TestCase):
    def test_authenticated_confirmed_snapshot_must_not_be_replaced_before_finalize(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db.sqlite"
            _init_database(path)
            ledger = _AuthenticatedThenTamperLedger(path)
            history = _History(path)

            with self.assertRaisesRegex(
                DatabaseIdentityMigrationError,
                "confirmed identity intent changed after authentication",
            ):
                migrate_database_identity(ledger, history)

            q = sqlite3.connect(path)
            custody = q.execute(
                """SELECT status,provider_id,provider_generation,position,
                          receipt_binding,logical_database_identity_digest
                   FROM provider_history_database_identity"""
            ).fetchone()
            q.close()
            self.assertEqual(custody, ("PREPARED", None, None, None, None, None))


if __name__ == "__main__":
    unittest.main()
