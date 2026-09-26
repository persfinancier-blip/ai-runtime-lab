import importlib.util
import sqlite3
import sys
import tempfile
import types
import unittest
from pathlib import Path

# Load the current integration against minimal class stubs. This is a RED
# regression for the transaction-wide boolean writer-authority gap.
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
    "real_integration_operation_scope",
    Path(__file__).parents[1] / "real_integration.py",
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
Ledger = module.SupportedMutableAsymmetricSharedAnchorLedger


class OperationScopedPermitRegression(unittest.TestCase):
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
            INSERT INTO component_anchor_watermarks VALUES('component-A',1);
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
        return ledger

    def test_authorized_transaction_cannot_jump_meta_tail(self):
        with tempfile.TemporaryDirectory() as td:
            ledger = self.make(td)
            q = ledger._con()
            with self.assertRaises(sqlite3.IntegrityError):
                with ledger._authorized_txn(q):
                    q.execute(
                        "UPDATE shared_anchor_meta SET reserved_position=999 WHERE singleton=1"
                    )
            q.close()

    def test_authorized_transaction_cannot_jump_watermark(self):
        with tempfile.TemporaryDirectory() as td:
            ledger = self.make(td)
            q = ledger._con()
            with self.assertRaises(sqlite3.IntegrityError):
                with ledger._authorized_txn(q):
                    q.execute(
                        "UPDATE component_anchor_watermarks SET position=999 WHERE component_id='component-A'"
                    )
            q.close()


if __name__ == "__main__":
    unittest.main()
