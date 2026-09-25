from __future__ import annotations

import sqlite3
import tempfile
import unittest
from dataclasses import dataclass
from pathlib import Path

from experiments.provider_generation_history.database_identity import (
    IDENTITY_INTENT_ID,
    IdentityCustodyState,
)
from experiments.provider_generation_history.database_identity_migration import (
    DatabaseIdentityMigrationError,
    migrate_database_identity,
    prepare_database_identity,
)
from experiments.shared_anchor_intent_ledger.protocol import LedgerEntry


_BOOTSTRAP = "b" * 64
_RECEIPT = "d" * 64


@dataclass(frozen=True)
class _Current:
    provider_id: str = "provider-alpha"
    generation: int = 1


class _Bootstrap:
    generation_id = _BOOTSTRAP


class _History:
    def __init__(self, path: Path, *, mutate_head_after_current: bool = False):
        self.path = str(path)
        self.bootstrap = _Bootstrap()
        self.mutate_head_after_current = mutate_head_after_current

    def verify_durable(self):
        return True

    def current(self):
        current = _Current()
        if self.mutate_head_after_current:
            q = sqlite3.connect(self.path)
            q.execute(
                "UPDATE provider_generation_head SET generation=2 WHERE singleton=1"
            )
            q.commit()
            q.close()
        return current

    def _verify_durable_locked(self, q):
        row = q.execute(
            "SELECT generation FROM provider_generation_head WHERE singleton=1"
        ).fetchone()
        if row is None:
            raise RuntimeError("missing provider generation head")
        return _Current(generation=row[0])


class _Ledger:
    def __init__(self, path: Path, *, fail_after_confirm_once: bool = False):
        self.path = str(path)
        self.fail_after_confirm_once = fail_after_confirm_once
        self.failed = False

    def _provider(self):
        return ("provider-alpha", 1)

    def execute(self, intent, *, timeout_after_commit=False):
        q = sqlite3.connect(self.path, timeout=5, isolation_level=None)
        q.execute("BEGIN IMMEDIATE")
        row = q.execute(
            "SELECT status,payload_digest FROM shared_anchor_intents WHERE intent_id=?",
            (intent.intent_id,),
        ).fetchone()
        if row is None or row[1] != intent.payload_digest:
            q.rollback()
            q.close()
            raise AssertionError("intent reconstruction drift")
        if row[0] == "PREPARED":
            q.execute(
                """UPDATE shared_anchor_intents
                   SET status='CONFIRMED',receipt_binding=?
                   WHERE intent_id=?""",
                (_RECEIPT, intent.intent_id),
            )
        q.commit()
        entry_row = q.execute(
            """SELECT intent_id,component_id,intent_type,payload_digest,provider_id,
                      provider_generation,predecessor_position,position,request_id,
                      status,receipt_binding
               FROM shared_anchor_intents WHERE intent_id=?""",
            (intent.intent_id,),
        ).fetchone()
        q.close()
        if self.fail_after_confirm_once and not self.failed:
            self.failed = True
            raise RuntimeError("simulated timeout after confirmation")
        return LedgerEntry(*entry_row)


def _init_database(path: Path):
    q = sqlite3.connect(path, isolation_level=None)
    q.executescript(
        f"""
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
        CREATE TABLE provider_generations(
          generation_id TEXT PRIMARY KEY,
          provider_id TEXT NOT NULL,
          generation INTEGER NOT NULL,
          verification_key_hex TEXT NOT NULL,
          UNIQUE(provider_id,generation)
        );
        INSERT INTO provider_generations
        VALUES('{_BOOTSTRAP}','provider-alpha',1,'00');
        CREATE TABLE provider_generation_head(
          singleton INTEGER PRIMARY KEY CHECK(singleton=1),
          generation_id TEXT NOT NULL,
          generation INTEGER NOT NULL
        );
        INSERT INTO provider_generation_head VALUES(1,'{_BOOTSTRAP}',1);
        """
    )
    q.close()


class DatabaseIdentityMigrationTests(unittest.TestCase):
    def test_prepare_is_atomic_and_retry_reuses_nonce_and_request(self):
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
            first = q.execute(
                """SELECT nonce_hex,intent_request_id
                   FROM provider_history_database_identity"""
            ).fetchone()
            intent = q.execute(
                """SELECT status,request_id FROM shared_anchor_intents
                   WHERE intent_id=?""",
                (IDENTITY_INTENT_ID,),
            ).fetchone()
            q.close()
            self.assertEqual(len(first[0]), 64)
            self.assertEqual(intent, ("PREPARED", first[1]))

            self.assertEqual(
                prepare_database_identity(ledger, history),
                IdentityCustodyState.PREPARED,
            )
            q = sqlite3.connect(path)
            second = q.execute(
                """SELECT nonce_hex,intent_request_id
                   FROM provider_history_database_identity"""
            ).fetchone()
            q.close()
            self.assertEqual(second, first)

    def test_confirmed_restart_finalizes_same_custody_without_new_request(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db.sqlite"
            _init_database(path)
            ledger = _Ledger(path, fail_after_confirm_once=True)
            history = _History(path)

            with self.assertRaises(RuntimeError):
                migrate_database_identity(ledger, history)

            q = sqlite3.connect(path)
            before = q.execute(
                """SELECT status,nonce_hex,intent_request_id
                   FROM provider_history_database_identity"""
            ).fetchone()
            external = q.execute(
                """SELECT status FROM shared_anchor_intents
                   WHERE intent_id=?""",
                (IDENTITY_INTENT_ID,),
            ).fetchone()
            q.close()
            self.assertEqual(before[0], "PREPARED")
            self.assertEqual(external, ("CONFIRMED",))

            digest = migrate_database_identity(ledger, history)
            q = sqlite3.connect(path)
            after = q.execute(
                """SELECT status,nonce_hex,intent_request_id,
                          logical_database_identity_digest
                   FROM provider_history_database_identity"""
            ).fetchone()
            q.close()
            self.assertEqual(after[0], "CONFIRMED")
            self.assertEqual(after[1:3], before[1:3])
            self.assertEqual(after[3], digest)

    def test_path_divergence_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            a = Path(td) / "a.sqlite"
            b = Path(td) / "b.sqlite"
            _init_database(a)
            _init_database(b)
            with self.assertRaises(DatabaseIdentityMigrationError):
                prepare_database_identity(_Ledger(a), _History(b))

    def test_provider_head_change_between_precheck_and_lock_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db.sqlite"
            _init_database(path)
            with self.assertRaisesRegex(
                DatabaseIdentityMigrationError,
                "provider history changed under migration lock",
            ):
                prepare_database_identity(
                    _Ledger(path),
                    _History(path, mutate_head_after_current=True),
                )


if __name__ == "__main__":
    unittest.main()
