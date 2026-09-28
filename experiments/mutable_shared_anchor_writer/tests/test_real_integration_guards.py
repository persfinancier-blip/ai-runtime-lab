import importlib.util
import sqlite3
import sys
import tempfile
import types
import unittest
from pathlib import Path

# Load the integration module against minimal class stubs. These tests exercise
# the connection-local authorization and real-schema triggers directly; they are
# not counted as the final LAB-080/LAB-082 integration gate.
import experiments

mods = {
    "experiments.asymmetric_provider_history": types.ModuleType("experiments.asymmetric_provider_history"),
    "experiments.asymmetric_provider_history.protocol": types.ModuleType("experiments.asymmetric_provider_history.protocol"),
    "experiments.asymmetric_provider_history.supported": types.ModuleType("experiments.asymmetric_provider_history.supported"),
    "experiments.shared_anchor_intent_ledger": types.ModuleType("experiments.shared_anchor_intent_ledger"),
    "experiments.shared_anchor_intent_ledger.protocol": types.ModuleType("experiments.shared_anchor_intent_ledger.protocol"),
}
for name, mod in mods.items():
    sys.modules[name] = mod
    parent_name, child = name.rsplit(".", 1)
    parent = sys.modules.get(parent_name)
    if parent is not None:
        setattr(parent, child, mod)


class Base:
    pass


mods["experiments.asymmetric_provider_history.protocol"].HistoricalVerificationError = RuntimeError
mods["experiments.asymmetric_provider_history.supported"].SupportedAsymmetricHistoricalSharedAnchorLedger = Base
for name in (
    "IntentConflict",
    "IntentGap",
    "IntentSubstitution",
    "PendingIntent",
    "ProviderMismatch",
    "UnexplainedAdvance",
):
    setattr(mods["experiments.shared_anchor_intent_ledger.protocol"], name, RuntimeError)


class Intent:
    pass


mods["experiments.shared_anchor_intent_ledger.protocol"].Intent = Intent

spec = importlib.util.spec_from_file_location(
    "real_integration",
    Path(__file__).parents[1] / "real_integration.py",
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
Ledger = module.SupportedMutableAsymmetricSharedAnchorLedger


class GuardTests(unittest.TestCase):
    def make(self, td):
        path = Path(td) / "shared.db"
        q = sqlite3.connect(path)
        q.executescript(
            """
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
              status TEXT NOT NULL,
              receipt_binding TEXT
            );
            CREATE TABLE component_anchor_watermarks(
              component_id TEXT PRIMARY KEY,
              position INTEGER NOT NULL
            );
            CREATE TABLE asymmetric_provider_receipts(
              request_id TEXT PRIMARY KEY,
              provider_id TEXT NOT NULL,
              generation INTEGER NOT NULL,
              position INTEGER NOT NULL,
              kind TEXT NOT NULL,
              challenge TEXT NOT NULL,
              signature TEXT NOT NULL,
              stable_binding TEXT NOT NULL
            );
            """
        )
        q.commit()
        q.close()
        ledger = Ledger.__new__(Ledger)
        ledger.path = str(path)
        ledger._install_guards()
        return path, ledger

    def test_direct_mutable_dml_is_denied(self):
        with tempfile.TemporaryDirectory() as td:
            _, ledger = self.make(td)
            q = ledger._con()
            with self.assertRaises(sqlite3.IntegrityError):
                q.execute(
                    "UPDATE shared_anchor_meta SET reserved_position=9 WHERE singleton=1"
                )
            with self.assertRaises(sqlite3.IntegrityError):
                q.execute(
                    "INSERT INTO shared_anchor_intents VALUES(?,?,?,?,?,?,?,?,?,'PREPARED',NULL)",
                    ("i", "c", "migration", "d" * 64, "p", 1, 0, 1, "r"),
                )
            with self.assertRaises(sqlite3.IntegrityError):
                q.execute(
                    "INSERT INTO asymmetric_provider_receipts VALUES(?,?,?,?,?,?,?,?)",
                    ("r", "p", 1, 1, "RECONCILE", "c", "s", "b" * 64),
                )
            q.close()

    def test_authorized_state_is_connection_local_and_transaction_scoped(self):
        with tempfile.TemporaryDirectory() as td:
            _, ledger = self.make(td)
            q = ledger._con()
            other = ledger._con()
            self.assertEqual(
                q.execute("SELECT lab091_writer_authorized()").fetchone()[0], 0
            )
            with ledger._authorized_txn(q):
                self.assertEqual(
                    q.execute("SELECT lab091_writer_authorized()").fetchone()[0], 1
                )
                self.assertEqual(
                    other.execute("SELECT lab091_writer_authorized()").fetchone()[0],
                    0,
                )
                q.execute(
                    "UPDATE shared_anchor_meta SET reserved_position=1 WHERE singleton=1"
                )
            self.assertEqual(
                q.execute("SELECT lab091_writer_authorized()").fetchone()[0], 0
            )
            q.close()
            other.close()

    def test_authorized_exact_flow_and_receipt_append(self):
        with tempfile.TemporaryDirectory() as td:
            path, ledger = self.make(td)
            q = ledger._con()
            with ledger._authorized_txn(q):
                q.execute(
                    "INSERT INTO shared_anchor_intents VALUES(?,?,?,?,?,?,?,?,?,'PREPARED',NULL)",
                    ("i", "c", "migration", "d" * 64, "p", 1, 0, 1, "r"),
                )
                q.execute(
                    "UPDATE shared_anchor_meta SET reserved_position=1 WHERE singleton=1"
                )
            with ledger._authorized_txn(q):
                q.execute(
                    "INSERT INTO asymmetric_provider_receipts VALUES(?,?,?,?,?,?,?,?)",
                    (
                        "r",
                        "p",
                        1,
                        1,
                        "RECONCILE",
                        "challenge",
                        "signature",
                        "b" * 64,
                    ),
                )
                q.execute(
                    "UPDATE shared_anchor_intents SET status='CONFIRMED',receipt_binding=? WHERE intent_id='i'",
                    ("b" * 64,),
                )
                q.execute(
                    "INSERT INTO component_anchor_watermarks VALUES('c',1)"
                )
            q.close()
            r = sqlite3.connect(path)
            self.assertEqual(
                r.execute("SELECT status FROM shared_anchor_intents").fetchone()[0],
                "CONFIRMED",
            )
            self.assertEqual(
                r.execute(
                    "SELECT position FROM component_anchor_watermarks"
                ).fetchone()[0],
                1,
            )
            r.close()

    def test_replace_existing_receipt_denied_even_authorized(self):
        with tempfile.TemporaryDirectory() as td:
            _, ledger = self.make(td)
            q = ledger._con()
            with ledger._authorized_txn(q):
                q.execute(
                    "INSERT INTO asymmetric_provider_receipts VALUES(?,?,?,?,?,?,?,?)",
                    ("r", "p", 1, 1, "RECONCILE", "c", "s", "b" * 64),
                )
            with self.assertRaises(sqlite3.IntegrityError):
                with ledger._authorized_txn(q):
                    q.execute(
                        "INSERT OR REPLACE INTO asymmetric_provider_receipts VALUES(?,?,?,?,?,?,?,?)",
                        ("r", "p", 1, 2, "RECONCILE", "x", "x", "c" * 64),
                    )
            q.close()

    def test_invalid_confirm_mutation_denied_even_authorized(self):
        with tempfile.TemporaryDirectory() as td:
            _, ledger = self.make(td)
            q = ledger._con()
            with ledger._authorized_txn(q):
                q.execute(
                    "INSERT INTO shared_anchor_intents VALUES(?,?,?,?,?,?,?,?,?,'PREPARED',NULL)",
                    ("i", "c", "migration", "d" * 64, "p", 1, 0, 1, "r"),
                )
                q.execute(
                    "UPDATE shared_anchor_meta SET reserved_position=1 WHERE singleton=1"
                )
            with self.assertRaises(sqlite3.IntegrityError):
                with ledger._authorized_txn(q):
                    q.execute(
                        "UPDATE shared_anchor_intents SET component_id='attacker',status='CONFIRMED',receipt_binding=? WHERE intent_id='i'",
                        ("b" * 64,),
                    )
            q.close()

    def test_watermark_rollback_denied_even_authorized(self):
        with tempfile.TemporaryDirectory() as td:
            _, ledger = self.make(td)
            q = ledger._con()
            with ledger._authorized_txn(q):
                q.execute("INSERT INTO component_anchor_watermarks VALUES('c',2)")
            with self.assertRaises(sqlite3.IntegrityError):
                with ledger._authorized_txn(q):
                    q.execute(
                        "UPDATE component_anchor_watermarks SET position=1 WHERE component_id='c'"
                    )
            q.close()

    def test_exception_rolls_back_and_clears_authorization(self):
        with tempfile.TemporaryDirectory() as td:
            path, ledger = self.make(td)
            q = ledger._con()
            with self.assertRaisesRegex(RuntimeError, "boom"):
                with ledger._authorized_txn(q):
                    q.execute(
                        "UPDATE shared_anchor_meta SET reserved_position=1 WHERE singleton=1"
                    )
                    raise RuntimeError("boom")
            self.assertEqual(
                q.execute("SELECT lab091_writer_authorized()").fetchone()[0], 0
            )
            q.close()
            r = sqlite3.connect(path)
            self.assertEqual(
                r.execute(
                    "SELECT reserved_position FROM shared_anchor_meta"
                ).fetchone()[0],
                0,
            )
            r.close()


if __name__ == "__main__":
    unittest.main()
