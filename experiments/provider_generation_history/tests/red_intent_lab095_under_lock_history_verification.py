from __future__ import annotations

import sqlite3
import tempfile
import unittest
from dataclasses import dataclass
from pathlib import Path

from experiments.provider_generation_history.database_identity_migration import (
    prepare_database_identity,
)
from experiments.provider_generation_history.protocol import HistoricalVerificationError


_BOOTSTRAP = "b" * 64


@dataclass(frozen=True)
class _Current:
    provider_id: str = "provider-alpha"
    generation: int = 1


class _Bootstrap:
    generation_id = _BOOTSTRAP


class _HistoryWithCorruptLockedChain:
    """Pre-lock view is valid; locked full-history recheck detects later corruption."""

    def __init__(self, path: Path):
        self.path = str(path)
        self.bootstrap = _Bootstrap()
        self.locked_checks = 0

    def verify_durable(self):
        return True

    def current(self):
        return _Current()

    def _verify_durable_locked(self, q):
        self.locked_checks += 1
        raise HistoricalVerificationError("corrupt transition proof under writer lock")


class _Ledger:
    def __init__(self, path: Path):
        self.path = str(path)

    def _provider(self):
        return ("provider-alpha", 1)


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


class UnderLockHistoryVerificationRedIntent(unittest.TestCase):
    def test_prepare_requires_full_history_reverification_under_same_writer_lock(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db.sqlite"
            _init_database(path)
            history = _HistoryWithCorruptLockedChain(path)

            with self.assertRaisesRegex(
                HistoricalVerificationError,
                "corrupt transition proof under writer lock",
            ):
                prepare_database_identity(_Ledger(path), history)

            self.assertEqual(history.locked_checks, 1)
            q = sqlite3.connect(path)
            try:
                self.assertEqual(
                    q.execute(
                        "SELECT COUNT(*) FROM shared_anchor_intents"
                    ).fetchone()[0],
                    0,
                )
                relation = q.execute(
                    "SELECT type FROM sqlite_master "
                    "WHERE name='provider_history_database_identity'"
                ).fetchone()
                if relation is not None:
                    self.assertEqual(
                        q.execute(
                            "SELECT COUNT(*) FROM provider_history_database_identity"
                        ).fetchone()[0],
                        0,
                    )
            finally:
                q.close()


if __name__ == "__main__":
    unittest.main()
