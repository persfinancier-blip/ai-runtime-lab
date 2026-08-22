import hashlib
import json
import sqlite3
import tempfile
import unittest
from dataclasses import dataclass
from pathlib import Path

from experiments.migration_anchor_binding.protocol import (
    MigrationAnchorCoordinator,
    MigrationAnchorPending,
    MigrationAnchorSubstitution,
    MigrationAnchorUnavailable,
    MigrationRollbackDetected,
    UnsafeLocalOnlyMigration,
)


@dataclass(frozen=True)
class Checkpoint:
    checkpoint_id: str
    cutoff_sequence: int
    terminal_authority_id: str
    terminal_authority_version: int
    terminal_authority_epoch: int


class FakeMigration:
    def __init__(self, path):
        self.path = str(path)
        q = self._con()
        q.executescript("""
            CREATE TABLE IF NOT EXISTS checkpoint(
              singleton INTEGER PRIMARY KEY, checkpoint_id TEXT, cutoff INTEGER,
              authority_id TEXT, authority_version INTEGER, authority_epoch INTEGER,
              valid INTEGER NOT NULL);
        """)
        q.close()

    def _con(self):
        return sqlite3.connect(self.path, timeout=5, isolation_level=None)

    def establish(self, checkpoint_id="cp-1", valid=1):
        q = self._con()
        q.execute("INSERT OR REPLACE INTO checkpoint VALUES(1,?,?,?,?,?,?)",
                  (checkpoint_id, 7, "root-A", 3, 9, valid))
        q.commit(); q.close()

    def verify_mixed_history(self):
        q = self._con(); row = q.execute("SELECT valid FROM checkpoint WHERE singleton=1").fetchone(); q.close()
        if row is None or row[0] != 1:
            raise RuntimeError("migration checkpoint missing/corrupt")
        return True

    def _load_checkpoint_locked(self, q):
        r = q.execute("SELECT checkpoint_id,cutoff,authority_id,authority_version,authority_epoch,valid FROM checkpoint WHERE singleton=1").fetchone()
        if r is None or r[5] != 1:
            raise RuntimeError("checkpoint")
        return Checkpoint(r[0], r[1], r[2], r[3], r[4]), object()


@dataclass(frozen=True)
class Expected:
    provider_id: str
    generation: int


@dataclass(frozen=True)
class Obs:
    position: int


class FakeVerifier:
    def __init__(self):
        self.expected = Expected("anchor-A", 4)


class FakeAttested:
    def __init__(self, value=0):
        self.value = value; self.available = True; self.verifier = FakeVerifier(); self.calls = 0; self.results = {}

    def authenticated_read(self, request_id):
        if not self.available:
            raise RuntimeError("unavailable")
        return Obs(self.value)

    def catch_up_one(self, db_sequence, request_id, timeout_after_commit=False):
        if not self.available:
            raise RuntimeError("unavailable")
        self.calls += 1
        if request_id in self.results:
            return self.results[request_id]
        if self.value > db_sequence:
            raise RuntimeError("anchor ahead")
        if self.value == db_sequence:
            receipt = hashlib.sha256(f"read:{request_id}:{self.value}".encode()).hexdigest()
            self.results[request_id] = receipt
            return receipt
        if self.value != db_sequence - 1:
            raise RuntimeError("unsafe gap")
        self.value += 1
        receipt = hashlib.sha256(f"increment:{request_id}:{self.value}".encode()).hexdigest()
        self.results[request_id] = receipt
        return receipt


class Tests(unittest.TestCase):
    def make(self, td):
        m = FakeMigration(Path(td) / "db.sqlite")
        a = FakeAttested(0)
        return m, a, MigrationAnchorCoordinator(m, a)

    def test_local_migration_not_consequential_before_anchor(self):
        with tempfile.TemporaryDirectory() as td:
            m, a, c = self.make(td); m.establish()
            self.assertTrue(UnsafeLocalOnlyMigration().consequential(m))
            with self.assertRaises(MigrationAnchorPending): c.verify_restart()

    def test_clean_bind_and_restart(self):
        with tempfile.TemporaryDirectory() as td:
            m, a, c = self.make(td); m.establish(); s = c.catch_up()
            self.assertEqual((s.sequence, s.status, a.value), (1, "CONFIRMED", 1))
            self.assertTrue(c.verify_restart())

    def test_timeout_after_anchor_commit_reconciles_once(self):
        with tempfile.TemporaryDirectory() as td:
            m, a, c = self.make(td); m.establish(); s = c.catch_up(timeout_after_commit=True)
            self.assertEqual(a.value, 1); self.assertEqual(s.status, "CONFIRMED")
            again = c.catch_up(); self.assertEqual(a.value, 1); self.assertEqual(again.anchor_receipt_ref, s.anchor_receipt_ref)

    def test_pre_migration_db_rollback_with_anchor_ahead(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db.sqlite"; m = FakeMigration(path); a = FakeAttested(0); m.establish(); c = MigrationAnchorCoordinator(m, a); c.catch_up()
            q=m._con(); q.execute("DELETE FROM checkpoint"); q.execute("DELETE FROM migration_anchor_binding"); q.execute("UPDATE migration_anchor_meta SET global_sequence=0"); q.commit(); q.close()
            with self.assertRaises(MigrationRollbackDetected): c.verify_restart()

    def test_anchor_rollback_detected(self):
        with tempfile.TemporaryDirectory() as td:
            m,a,c=self.make(td); m.establish(); c.catch_up(); a.value=0
            with self.assertRaises(MigrationRollbackDetected): c.verify_restart()

    def test_same_position_checkpoint_substitution_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            m,a,c=self.make(td); m.establish(); c.catch_up(); q=m._con(); q.execute("UPDATE checkpoint SET checkpoint_id='cp-evil'"); q.commit(); q.close()
            with self.assertRaises(MigrationAnchorSubstitution): c.verify_restart()

    def test_wrong_provider_generation_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            m,a,c=self.make(td); m.establish(); c.catch_up(); a.verifier.expected=Expected("anchor-A",5)
            with self.assertRaises(MigrationAnchorSubstitution): c.verify_restart()

    def test_unavailable_anchor_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            m,a,c=self.make(td); m.establish(); c.catch_up(); a.available=False
            with self.assertRaises(MigrationAnchorUnavailable): c.verify_restart()

    def test_sql_commit_before_anchor_is_pending_then_catchup(self):
        with tempfile.TemporaryDirectory() as td:
            m,a,c=self.make(td); m.establish(); c.prepare()
            with self.assertRaises(MigrationAnchorPending): c.verify_restart()
            self.assertEqual(a.value,0); c.catch_up(); self.assertTrue(c.verify_restart())

    def test_binding_substitution_rejected_on_prepare(self):
        with tempfile.TemporaryDirectory() as td:
            m,a,c=self.make(td); m.establish(); c.prepare(); q=m._con(); q.execute("UPDATE migration_anchor_binding SET payload_digest=?",("0"*64,)); q.commit(); q.close()
            with self.assertRaises(MigrationAnchorSubstitution): c.prepare()

    def test_external_position_ahead_of_current_snapshot_fails(self):
        with tempfile.TemporaryDirectory() as td:
            m,a,c=self.make(td); m.establish(); c.catch_up(); a.value=2
            with self.assertRaises(MigrationRollbackDetected): c.verify_restart()

if __name__ == "__main__": unittest.main()
