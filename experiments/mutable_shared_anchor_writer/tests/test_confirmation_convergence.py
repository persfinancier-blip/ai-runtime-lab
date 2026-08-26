import contextlib
import importlib.util
import sqlite3
import sys
import tempfile
import types
import unittest
from collections import namedtuple
from pathlib import Path

import experiments

# Stub only the parent integration and shared protocol. The test exercises the
# new confirmation-convergence algorithm against a real SQLite row + one-shot
# trigger, not the full LAB-080/LAB-082 stack.
shared_pkg = types.ModuleType("experiments.shared_anchor_intent_ledger")
shared = types.ModuleType("experiments.shared_anchor_intent_ledger.protocol")
sys.modules["experiments.shared_anchor_intent_ledger"] = shared_pkg
sys.modules["experiments.shared_anchor_intent_ledger.protocol"] = shared
setattr(experiments, "shared_anchor_intent_ledger", shared_pkg)
setattr(shared_pkg, "protocol", shared)


class Intent:
    pass


class IntentSubstitution(RuntimeError):
    pass


class PendingIntent(RuntimeError):
    pass


shared.Intent = Intent
shared.IntentSubstitution = IntentSubstitution
shared.PendingIntent = PendingIntent

from experiments.mutable_shared_anchor_writer.operation_permit import (
    PermitConnection,
    install_operation_permit_udf,
)

Entry = namedtuple(
    "Entry",
    "intent_id component_id intent_type payload_digest provider_id "
    "provider_generation predecessor_position position request_id status receipt_binding",
)

parent_mod = types.ModuleType(
    "experiments.mutable_shared_anchor_writer.operation_scoped_integration"
)


class Parent:
    def _con(self):
        q = sqlite3.connect(
            self.path, isolation_level=None, factory=PermitConnection, timeout=5
        )
        install_operation_permit_udf(q)
        return q

    @contextlib.contextmanager
    def _write_txn(self, q):
        q.execute("BEGIN IMMEDIATE")
        try:
            yield q
            q.commit()
        except Exception:
            if q.in_transaction:
                q.rollback()
            raise

    @staticmethod
    def _row_entry(row):
        return Entry(*row)

    @staticmethod
    def _same_request(a, b):
        return (
            a.intent_id,
            a.component_id,
            a.intent_type,
            a.payload_digest,
            a.provider_id,
            a.provider_generation,
            a.predecessor_position,
            a.position,
            a.request_id,
        ) == (
            b.intent_id,
            b.component_id,
            b.intent_type,
            b.payload_digest,
            b.provider_id,
            b.provider_generation,
            b.predecessor_position,
            b.position,
            b.request_id,
        )

    @staticmethod
    def _entry_token(entry, *, status=None, receipt_binding=...):
        status = entry.status if status is None else status
        receipt_binding = (
            entry.receipt_binding if receipt_binding is ... else receipt_binding
        )
        return "|".join(
            [
                entry.intent_id,
                entry.request_id,
                status,
                "" if receipt_binding is None else receipt_binding,
            ]
        )

    def entry(self, intent_id):
        q = sqlite3.connect(self.path)
        row = q.execute(
            "SELECT intent_id,component_id,intent_type,payload_digest,"
            "provider_id,provider_generation,predecessor_position,position,"
            "request_id,status,receipt_binding "
            "FROM shared_anchor_intents WHERE intent_id=?",
            (intent_id,),
        ).fetchone()
        q.close()
        return Entry(*row)


parent_mod.SupportedOperationScopedAsymmetricSharedAnchorLedger = Parent
sys.modules[
    "experiments.mutable_shared_anchor_writer.operation_scoped_integration"
] = parent_mod

spec = importlib.util.spec_from_file_location(
    "experiments.mutable_shared_anchor_writer.convergent_operation_scoped",
    Path(__file__).parents[1] / "convergent_operation_scoped.py",
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
Ledger = module.SupportedConvergentOperationScopedAsymmetricSharedAnchorLedger


class ConfirmationConvergenceTests(unittest.TestCase):
    def make(self, td, *, status="PREPARED", receipt=None, payload_digest=None):
        path = Path(td) / "db"
        q = sqlite3.connect(path)
        q.executescript(
            """
            CREATE TABLE shared_anchor_intents(
              intent_id TEXT PRIMARY KEY,
              component_id TEXT NOT NULL,
              intent_type TEXT NOT NULL,
              payload_digest TEXT NOT NULL,
              provider_id TEXT NOT NULL,
              provider_generation INTEGER NOT NULL,
              predecessor_position INTEGER NOT NULL,
              position INTEGER NOT NULL,
              request_id TEXT NOT NULL UNIQUE,
              status TEXT NOT NULL,
              receipt_binding TEXT
            );
            """
        )
        q.execute(
            "INSERT INTO shared_anchor_intents VALUES(?,?,?,?,?,?,?,?,?,?,?)",
            (
                "i",
                "c",
                "migration",
                (payload_digest or "d" * 64),
                "p",
                1,
                0,
                1,
                "r",
                status,
                receipt,
            ),
        )
        q.executescript(
            """
            CREATE TRIGGER exact_confirm
            BEFORE UPDATE ON shared_anchor_intents
            WHEN lab091_consume_permit(
              'intent-confirm',
              OLD.intent_id,
              OLD.intent_id || '|' || OLD.request_id || '|' || OLD.status || '|' ||
                COALESCE(OLD.receipt_binding,''),
              NEW.intent_id || '|' || NEW.request_id || '|' || NEW.status || '|' ||
                COALESCE(NEW.receipt_binding,'')
            )!=1
            BEGIN SELECT RAISE(ABORT,'exact permit required'); END;
            """
        )
        q.commit()
        q.close()
        ledger = Ledger.__new__(Ledger)
        ledger.path = str(path)
        prepared = Entry(
            "i", "c", "migration", "d" * 64, "p", 1, 0, 1, "r", "PREPARED", None
        )
        return ledger, prepared

    def test_prepared_worker_can_confirm(self):
        with tempfile.TemporaryDirectory() as td:
            ledger, entry = self.make(td)
            out = ledger._commit_confirmation("i", entry, "b" * 64)
            self.assertEqual(out.status, "CONFIRMED")
            self.assertEqual(out.receipt_binding, "b" * 64)

    def test_identical_loser_converges_on_confirmed_winner(self):
        with tempfile.TemporaryDirectory() as td:
            ledger, entry = self.make(td, status="CONFIRMED", receipt="b" * 64)
            out = ledger._commit_confirmation("i", entry, "b" * 64)
            self.assertEqual(out.status, "CONFIRMED")
            self.assertEqual(out.receipt_binding, "b" * 64)

    def test_confirmed_winner_with_different_receipt_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            ledger, entry = self.make(td, status="CONFIRMED", receipt="x" * 64)
            with self.assertRaises(IntentSubstitution):
                ledger._commit_confirmation("i", entry, "b" * 64)

    def test_confirmed_winner_with_different_request_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            ledger, entry = self.make(
                td,
                status="CONFIRMED",
                receipt="b" * 64,
                payload_digest="e" * 64,
            )
            with self.assertRaises(IntentSubstitution):
                ledger._commit_confirmation("i", entry, "b" * 64)


if __name__ == "__main__":
    unittest.main()
