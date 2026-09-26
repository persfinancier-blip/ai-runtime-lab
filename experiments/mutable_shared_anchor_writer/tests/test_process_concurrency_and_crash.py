import contextlib
import importlib.util
import multiprocessing
import os
import sqlite3
import sys
import tempfile
import types
import unittest
from collections import namedtuple
from pathlib import Path

import experiments

shared_pkg = types.ModuleType("experiments.shared_anchor_intent_ledger")
shared = types.ModuleType("experiments.shared_anchor_intent_ledger.protocol")
sys.modules["experiments.shared_anchor_intent_ledger"] = shared_pkg
sys.modules["experiments.shared_anchor_intent_ledger.protocol"] = shared
setattr(experiments, "shared_anchor_intent_ledger", shared_pkg)
setattr(shared_pkg, "protocol", shared)

class Intent: pass
class IntentSubstitution(RuntimeError): pass
class PendingIntent(RuntimeError): pass
shared.Intent = Intent
shared.IntentSubstitution = IntentSubstitution
shared.PendingIntent = PendingIntent

from experiments.mutable_shared_anchor_writer.operation_permit import (
    PermitConnection,
    install_operation_permit_udf,
    one_shot_permit,
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
        q.execute("PRAGMA busy_timeout=5000")
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
            a.intent_id,a.component_id,a.intent_type,a.payload_digest,a.provider_id,
            a.provider_generation,a.predecessor_position,a.position,a.request_id,
        ) == (
            b.intent_id,b.component_id,b.intent_type,b.payload_digest,b.provider_id,
            b.provider_generation,b.predecessor_position,b.position,b.request_id,
        )

    @staticmethod
    def _entry_token(entry, *, status=None, receipt_binding=...):
        status = entry.status if status is None else status
        receipt_binding = entry.receipt_binding if receipt_binding is ... else receipt_binding
        return "|".join([
            entry.intent_id,entry.request_id,status,
            "" if receipt_binding is None else receipt_binding,
        ])

    def entry(self, intent_id):
        q = sqlite3.connect(self.path)
        row = q.execute(
            "SELECT intent_id,component_id,intent_type,payload_digest,"
            "provider_id,provider_generation,predecessor_position,position,"
            "request_id,status,receipt_binding FROM shared_anchor_intents WHERE intent_id=?",
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


def _confirm_worker(path, barrier, output):
    ledger = Ledger.__new__(Ledger)
    ledger.path = path
    entry = Entry("i","c","migration","d"*64,"p",1,0,1,"r","PREPARED",None)
    barrier.wait()
    try:
        result = ledger._commit_confirmation("i", entry, "b"*64)
        output.put(("ok", result.status, result.receipt_binding))
    except Exception as exc:
        output.put(("err", type(exc).__name__, str(exc)))


def _crash_worker(path):
    q = sqlite3.connect(path, isolation_level=None, factory=PermitConnection, timeout=5)
    install_operation_permit_udf(q)
    q.execute("BEGIN IMMEDIATE")
    old = "i|r|PREPARED|"
    new = "i|r|CONFIRMED|" + "b"*64
    with one_shot_permit(
        q, kind="intent-confirm", identity="i", old_value=old, new_value=new
    ):
        q.execute(
            "UPDATE shared_anchor_intents SET status='CONFIRMED',receipt_binding=? "
            "WHERE intent_id='i' AND status='PREPARED'",
            ("b"*64,),
        )
    os._exit(17)


class ProcessConcurrencyAndCrashTests(unittest.TestCase):
    def make(self, td):
        path = str(Path(td) / "db")
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
            INSERT INTO shared_anchor_intents VALUES(
              'i','c','migration','dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd',
              'p',1,0,1,'r','PREPARED',NULL
            );
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
        q.commit(); q.close()
        return path

    def test_two_processes_converge_on_same_confirmation(self):
        if "fork" not in multiprocessing.get_all_start_methods():
            self.skipTest("fork start method required for deterministic stub inheritance")
        ctx = multiprocessing.get_context("fork")
        with tempfile.TemporaryDirectory() as td:
            path = self.make(td)
            barrier = ctx.Barrier(2)
            output = ctx.Queue()
            workers = [
                ctx.Process(target=_confirm_worker, args=(path, barrier, output))
                for _ in range(2)
            ]
            for worker in workers: worker.start()
            for worker in workers: worker.join(10)
            self.assertTrue(all(not worker.is_alive() for worker in workers))
            results = [output.get(timeout=2) for _ in workers]
            self.assertEqual(results.count(("ok","CONFIRMED","b"*64)), 2)
            q = sqlite3.connect(path)
            row = q.execute(
                "SELECT status,receipt_binding FROM shared_anchor_intents WHERE intent_id='i'"
            ).fetchone()
            q.close()
            self.assertEqual(row, ("CONFIRMED","b"*64))

    def test_process_death_before_commit_rolls_back_authorized_update(self):
        if "fork" not in multiprocessing.get_all_start_methods():
            self.skipTest("fork start method required")
        ctx = multiprocessing.get_context("fork")
        with tempfile.TemporaryDirectory() as td:
            path = self.make(td)
            worker = ctx.Process(target=_crash_worker, args=(path,))
            worker.start(); worker.join(10)
            self.assertEqual(worker.exitcode, 17)
            q = sqlite3.connect(path)
            row = q.execute(
                "SELECT status,receipt_binding FROM shared_anchor_intents WHERE intent_id='i'"
            ).fetchone()
            q.close()
            self.assertEqual(row, ("PREPARED", None))


if __name__ == "__main__":
    unittest.main()
