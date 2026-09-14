import hashlib
import sqlite3
import tempfile
import unittest
from pathlib import Path

from experiments.mutable_shared_anchor_writer.history_binding_guards import (
    HISTORY_TRIGGER_NAMES,
    install_history_binding_guards,
)
from experiments.mutable_shared_anchor_writer.operation_permit import (
    PermitConnection,
    install_operation_permit_udf,
)
from experiments.mutable_shared_anchor_writer.state_machine_udfs import (
    expected_request_id,
    install_state_machine_udfs,
)


def digest(tag):
    return hashlib.sha256(tag.encode()).hexdigest()


def connect(path, *, install_udfs=True):
    q = sqlite3.connect(path, isolation_level=None, factory=PermitConnection)
    install_operation_permit_udf(q)
    if install_udfs:
        install_state_machine_udfs(q)
    return q


class V4RestartPersistenceTests(unittest.TestCase):
    def create_database(self, path):
        q = connect(path)
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
        q.execute("BEGIN IMMEDIATE")
        install_history_binding_guards(q)
        q.commit()
        q.close()

    @staticmethod
    def intent_row(position=1, *, request_id=None, status="PREPARED", receipt_binding=None):
        intent_id = f"intent-{position}"
        component_id = "component-A"
        intent_type = "migration"
        payload_digest = digest(f"payload-{position}")
        if request_id is None:
            request_id = expected_request_id(
                position, intent_id, component_id, intent_type, payload_digest
            )
        return (
            intent_id,
            component_id,
            intent_type,
            payload_digest,
            "anchor-A",
            1,
            position - 1,
            position,
            request_id,
            status,
            receipt_binding,
        )

    def test_trigger_set_survives_close_and_reopen(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            self.create_database(path)
            q = connect(path)
            names = {
                row[0]
                for row in q.execute(
                    "SELECT name FROM sqlite_master WHERE type='trigger' AND name LIKE 'lab091_v4_%'"
                ).fetchall()
            }
            q.close()
            self.assertEqual(names, set(HISTORY_TRIGGER_NAMES))

    def test_reopened_connection_still_enforces_request_and_confirmation_binding(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            self.create_database(path)
            q = connect(path)
            bad = self.intent_row(request_id="attacker-request")
            with self.assertRaises(sqlite3.IntegrityError):
                q.execute("INSERT INTO shared_anchor_intents VALUES(?,?,?,?,?,?,?,?,?,?,?)", bad)

            row = self.intent_row()
            q.execute("INSERT INTO shared_anchor_intents VALUES(?,?,?,?,?,?,?,?,?,?,?)", row)
            binding = digest("binding-1")
            with self.assertRaises(sqlite3.IntegrityError):
                q.execute(
                    "UPDATE shared_anchor_intents SET status='CONFIRMED',receipt_binding=? WHERE intent_id=?",
                    (binding, row[0]),
                )
            q.execute(
                "INSERT INTO asymmetric_provider_receipts VALUES(?,?,?,?,?,?,?,?)",
                (row[8], row[4], row[5], row[7], "RECONCILE", "c", "s", binding),
            )
            q.execute(
                "UPDATE shared_anchor_intents SET status='CONFIRMED',receipt_binding=? WHERE intent_id=?",
                (binding, row[0]),
            )
            q.execute("INSERT INTO component_anchor_watermarks VALUES('component-A',1)")
            q.close()

            restarted = connect(path)
            self.assertEqual(
                restarted.execute(
                    "SELECT status,receipt_binding FROM shared_anchor_intents WHERE intent_id=?",
                    (row[0],),
                ).fetchone(),
                ("CONFIRMED", binding),
            )
            self.assertEqual(
                restarted.execute(
                    "SELECT position FROM component_anchor_watermarks WHERE component_id='component-A'"
                ).fetchone()[0],
                1,
            )
            restarted.close()

    def test_missing_restart_udf_fails_closed_instead_of_bypassing_trigger(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            self.create_database(path)
            q = connect(path, install_udfs=False)
            row = self.intent_row()
            with self.assertRaises(sqlite3.OperationalError):
                q.execute("INSERT INTO shared_anchor_intents VALUES(?,?,?,?,?,?,?,?,?,?,?)", row)
            self.assertEqual(q.execute("SELECT COUNT(*) FROM shared_anchor_intents").fetchone()[0], 0)
            q.close()


if __name__ == "__main__":
    unittest.main()
