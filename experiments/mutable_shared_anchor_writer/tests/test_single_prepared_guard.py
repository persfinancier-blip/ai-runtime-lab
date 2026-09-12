import sqlite3
import unittest

from experiments.mutable_shared_anchor_writer.cross_table_guards import (
    install_cross_table_guards,
)
from experiments.mutable_shared_anchor_writer.operation_permit import PermitConnection


class SinglePreparedIntentGuardTests(unittest.TestCase):
    def make(self):
        q = sqlite3.connect(":memory:", isolation_level=None, factory=PermitConnection)
        q.executescript(
            """
            CREATE TABLE shared_anchor_meta(
              singleton INTEGER PRIMARY KEY CHECK(singleton=1),
              reserved_position INTEGER NOT NULL
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
            CREATE TABLE asymmetric_provider_generations(
              generation_id TEXT PRIMARY KEY,
              provider_id TEXT NOT NULL,
              generation INTEGER NOT NULL
            );
            CREATE TABLE asymmetric_provider_head(
              singleton INTEGER PRIMARY KEY CHECK(singleton=1),
              generation_id TEXT NOT NULL,
              generation INTEGER NOT NULL
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
            INSERT INTO asymmetric_provider_generations VALUES('g1','anchor-A',1);
            INSERT INTO asymmetric_provider_head VALUES(1,'g1',1);
            """
        )
        q.execute("BEGIN IMMEDIATE")
        install_cross_table_guards(q)
        q.commit()
        return q

    @staticmethod
    def insert_prepared(q, intent_id, predecessor, position):
        q.execute(
            "INSERT INTO shared_anchor_intents VALUES(?,?,?,?,?,?,?,?,?,'PREPARED',NULL)",
            (
                intent_id,
                "component-A",
                "migration",
                f"payload-{intent_id}",
                "anchor-A",
                1,
                predecessor,
                position,
                f"request-{intent_id}",
            ),
        )

    def test_second_prepared_intent_is_rejected_even_at_exact_next_tail(self):
        q = self.make()
        self.insert_prepared(q, "intent-1", 0, 1)
        q.execute("UPDATE shared_anchor_meta SET reserved_position=1 WHERE singleton=1")

        with self.assertRaises(sqlite3.IntegrityError):
            self.insert_prepared(q, "intent-2", 1, 2)

        rows = q.execute(
            "SELECT intent_id,status,position FROM shared_anchor_intents ORDER BY position"
        ).fetchall()
        self.assertEqual(rows, [("intent-1", "PREPARED", 1)])
        self.assertEqual(
            q.execute(
                "SELECT reserved_position FROM shared_anchor_meta WHERE singleton=1"
            ).fetchone()[0],
            1,
        )

    def test_next_intent_is_allowed_after_prior_intent_is_resolved(self):
        q = self.make()
        self.insert_prepared(q, "intent-1", 0, 1)
        q.execute("UPDATE shared_anchor_meta SET reserved_position=1 WHERE singleton=1")
        q.execute(
            "UPDATE shared_anchor_intents SET status='CONFIRMED',receipt_binding='receipt-1' "
            "WHERE intent_id='intent-1'"
        )

        self.insert_prepared(q, "intent-2", 1, 2)
        q.execute("UPDATE shared_anchor_meta SET reserved_position=2 WHERE singleton=1")

        rows = q.execute(
            "SELECT intent_id,status,position FROM shared_anchor_intents ORDER BY position"
        ).fetchall()
        self.assertEqual(
            rows,
            [("intent-1", "CONFIRMED", 1), ("intent-2", "PREPARED", 2)],
        )


if __name__ == "__main__":
    unittest.main()
