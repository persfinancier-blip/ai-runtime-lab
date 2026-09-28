import sqlite3
import unittest

from experiments.mutable_shared_anchor_writer.cross_table_guards import install_cross_table_guards
from experiments.mutable_shared_anchor_writer.history_binding_guards import install_history_binding_guards
from experiments.mutable_shared_anchor_writer.operation_permit import PermitConnection
from experiments.mutable_shared_anchor_writer.state_machine_udfs import install_state_machine_udfs


class ReceiptCollationExactnessRegressionTests(unittest.TestCase):
    def make(self):
        q = sqlite3.connect(":memory:", isolation_level=None, factory=PermitConnection)
        q.executescript("""
            CREATE TABLE shared_anchor_meta(
              singleton INTEGER PRIMARY KEY,
              reserved_position INTEGER NOT NULL
            );
            INSERT INTO shared_anchor_meta VALUES(1,0);
            CREATE TABLE shared_anchor_intents(
              intent_id TEXT PRIMARY KEY,
              component_id TEXT NOT NULL,
              intent_type TEXT NOT NULL,
              payload_digest TEXT NOT NULL,
              provider_id TEXT COLLATE NOCASE NOT NULL,
              provider_generation INTEGER NOT NULL,
              predecessor_position INTEGER NOT NULL,
              position INTEGER NOT NULL UNIQUE,
              request_id TEXT NOT NULL UNIQUE,
              status TEXT COLLATE NOCASE NOT NULL,
              receipt_binding TEXT
            );
            CREATE TABLE asymmetric_provider_generations(
              generation_id TEXT PRIMARY KEY,
              provider_id TEXT NOT NULL,
              generation INTEGER NOT NULL
            );
            INSERT INTO asymmetric_provider_generations VALUES('g1','Anchor-A',1);
            CREATE TABLE asymmetric_provider_head(
              singleton INTEGER PRIMARY KEY,
              generation_id TEXT NOT NULL,
              generation INTEGER NOT NULL
            );
            INSERT INTO asymmetric_provider_head VALUES(1,'g1',1);
            CREATE TABLE asymmetric_provider_receipts(
              request_id TEXT PRIMARY KEY,
              provider_id TEXT COLLATE NOCASE NOT NULL,
              generation INTEGER NOT NULL,
              position INTEGER NOT NULL,
              kind TEXT COLLATE NOCASE NOT NULL,
              challenge TEXT NOT NULL,
              signature TEXT NOT NULL,
              stable_binding TEXT COLLATE NOCASE NOT NULL
            );
            CREATE TABLE component_anchor_watermarks(
              component_id TEXT PRIMARY KEY,
              position INTEGER NOT NULL
            );
            INSERT INTO shared_anchor_intents VALUES(
              'i','component-A','migration',
              'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
              'Anchor-A',1,0,1,'req','PREPARED',NULL
            );
        """)
        install_state_machine_udfs(q)
        q.execute("BEGIN IMMEDIATE")
        install_cross_table_guards(q)
        install_history_binding_guards(q)
        q.commit()
        return q

    def test_nocase_receipt_kind_does_not_accept_lowercase_reconcile(self):
        q = self.make()
        with self.assertRaises(sqlite3.IntegrityError):
            q.execute(
                "INSERT INTO asymmetric_provider_receipts VALUES(?,?,?,?,?,?,?,?)",
                ("req","Anchor-A",1,1,"reconcile","c","s","abcdef"),
            )

    def test_nocase_provider_does_not_accept_case_variant_provider(self):
        q = self.make()
        with self.assertRaises(sqlite3.IntegrityError):
            q.execute(
                "INSERT INTO asymmetric_provider_receipts VALUES(?,?,?,?,?,?,?,?)",
                ("req","anchor-a",1,1,"RECONCILE","c","s","abcdef"),
            )

    def test_canonical_receipt_still_passes_v3(self):
        q = self.make()
        q.execute(
            "INSERT INTO asymmetric_provider_receipts VALUES(?,?,?,?,?,?,?,?)",
            ("req","Anchor-A",1,1,"RECONCILE","c","s","abcdef"),
        )
        self.assertEqual(q.execute("SELECT kind FROM asymmetric_provider_receipts").fetchone()[0], "RECONCILE")

    def test_v4_binding_is_binary_even_if_receipt_column_is_nocase(self):
        q = self.make()
        q.execute(
            "INSERT INTO asymmetric_provider_receipts VALUES(?,?,?,?,?,?,?,?)",
            ("req","Anchor-A",1,1,"RECONCILE","c","s","abcdef"),
        )
        with self.assertRaises(sqlite3.IntegrityError):
            q.execute(
                "UPDATE shared_anchor_intents SET status='CONFIRMED',receipt_binding='ABCDEF' WHERE intent_id='i'"
            )
        q.execute(
            "UPDATE shared_anchor_intents SET status='CONFIRMED',receipt_binding='abcdef' WHERE intent_id='i'"
        )
        self.assertEqual(
            q.execute("SELECT status,receipt_binding FROM shared_anchor_intents").fetchone(),
            ("CONFIRMED","abcdef"),
        )


if __name__ == "__main__":
    unittest.main()
