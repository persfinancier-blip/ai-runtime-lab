import hashlib
import sqlite3
import unittest

from experiments.mutable_shared_anchor_writer.operation_permit import PermitConnection
from experiments.mutable_shared_anchor_writer.history_binding_guards import install_history_binding_guards
from experiments.mutable_shared_anchor_writer.state_machine_udfs import (
    expected_request_id,
    install_state_machine_udfs,
)


def digest(tag):
    return hashlib.sha256(tag.encode()).hexdigest()


class HistoryBindingGuardTests(unittest.TestCase):
    def make(self):
        q=sqlite3.connect(":memory:", isolation_level=None, factory=PermitConnection)
        install_state_machine_udfs(q)
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
            """
        )
        q.execute("BEGIN IMMEDIATE")
        install_history_binding_guards(q)
        q.commit()
        return q

    def insert_intent(self, q, pos, *, status="CONFIRMED", request_id=None, receipt=True):
        iid=f"intent-{pos}"
        pd=digest(f"payload-{pos}")
        if request_id is None:
            request_id=expected_request_id(pos,iid,"component-A","migration",pd)
        q.execute(
            "INSERT INTO shared_anchor_intents VALUES(?,?,?,?,?,?,?,?,?,?,?)",
            (
                iid,"component-A","migration",pd,"anchor-A",1,pos-1,pos,
                request_id,status,digest(f"receipt-{pos}") if receipt else None,
            ),
        )

    def test_wrong_request_id_is_blocked(self):
        q=self.make()
        with self.assertRaises(sqlite3.IntegrityError):
            self.insert_intent(q,1,request_id="attacker-request")

    def test_exact_request_id_is_accepted(self):
        q=self.make()
        self.insert_intent(q,1)
        self.assertEqual(q.execute("SELECT COUNT(*) FROM shared_anchor_intents").fetchone()[0],1)

    def test_watermark_insert_requires_complete_confirmed_prefix(self):
        q=self.make()
        self.insert_intent(q,1)
        self.insert_intent(q,2,status="PREPARED",receipt=False)
        with self.assertRaises(sqlite3.IntegrityError):
            q.execute("INSERT INTO component_anchor_watermarks VALUES('component-A',2)")

    def test_watermark_insert_accepts_complete_confirmed_prefix(self):
        q=self.make()
        self.insert_intent(q,1); self.insert_intent(q,2)
        q.execute("INSERT INTO component_anchor_watermarks VALUES('component-A',2)")
        self.assertEqual(q.execute("SELECT position FROM component_anchor_watermarks").fetchone()[0],2)

    def test_watermark_update_requires_complete_confirmed_delta(self):
        q=self.make()
        self.insert_intent(q,1)
        q.execute("INSERT INTO component_anchor_watermarks VALUES('component-A',1)")
        self.insert_intent(q,2)
        self.insert_intent(q,3,status="PREPARED",receipt=False)
        with self.assertRaises(sqlite3.IntegrityError):
            q.execute("UPDATE component_anchor_watermarks SET position=3 WHERE component_id='component-A'")

    def test_watermark_update_accepts_complete_confirmed_delta(self):
        q=self.make()
        self.insert_intent(q,1)
        q.execute("INSERT INTO component_anchor_watermarks VALUES('component-A',1)")
        self.insert_intent(q,2); self.insert_intent(q,3)
        q.execute("UPDATE component_anchor_watermarks SET position=3 WHERE component_id='component-A'")
        self.assertEqual(q.execute("SELECT position FROM component_anchor_watermarks").fetchone()[0],3)

    def test_gap_cannot_be_hidden_by_count(self):
        q=self.make()
        self.insert_intent(q,1)
        iid="intent-2"; pd=digest("payload-2")
        rid=expected_request_id(2,iid,"component-A","migration",pd)
        q.execute(
          "INSERT INTO shared_anchor_intents VALUES(?,?,?,?,?,?,?,?,?,?,?)",
          (iid,"component-A","migration",pd,"anchor-A",1,0,2,rid,"CONFIRMED",digest("r2"))
        )
        with self.assertRaises(sqlite3.IntegrityError):
            q.execute("INSERT INTO component_anchor_watermarks VALUES('component-A',2)")


if __name__ == "__main__":
    unittest.main()
