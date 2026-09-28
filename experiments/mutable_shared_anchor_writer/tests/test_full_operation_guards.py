import sqlite3
import unittest

from experiments.mutable_shared_anchor_writer.full_operation_guards import (
    install_full_operation_guards,
)
from experiments.mutable_shared_anchor_writer.operation_permit import (
    PermitConnection,
    install_operation_permit_udf,
    one_shot_permit,
)
from experiments.mutable_shared_anchor_writer.row_tokens import (
    install_row_token_udfs,
    intent_row_token,
    receipt_row_token,
)


class FullOperationGuardTests(unittest.TestCase):
    def make(self):
        q = sqlite3.connect(":memory:", isolation_level=None, factory=PermitConnection)
        install_operation_permit_udf(q)
        install_row_token_udfs(q)
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
        install_full_operation_guards(q)
        q.commit()
        return q

    @staticmethod
    def intent_row(receipt=None, status="PREPARED"):
        return (
            "intent-1","component-A","migration","a" * 64,
            "anchor-A",1,0,1,"request-1",status,receipt,
        )

    @staticmethod
    def receipt_row():
        return (
            "request-1","anchor-A",1,1,"RECONCILE","challenge-1",
            "ab" * 64,"cd" * 32,
        )

    def insert_intent(self, q):
        row = self.intent_row()
        token = intent_row_token(*row)
        with one_shot_permit(
            q, kind="intent-insert", identity=row[0], old_value="", new_value=token
        ):
            q.execute("INSERT INTO shared_anchor_intents VALUES(?,?,?,?,?,?,?,?,?,?,?)", row)

    def test_unpermitted_intent_insert_is_blocked(self):
        q = self.make(); q.execute("BEGIN IMMEDIATE")
        with self.assertRaises(sqlite3.IntegrityError):
            q.execute("INSERT INTO shared_anchor_intents VALUES(?,?,?,?,?,?,?,?,?,?,?)", self.intent_row())
        q.rollback()

    def test_exact_intent_insert_and_meta_cas(self):
        q = self.make(); q.execute("BEGIN IMMEDIATE")
        self.insert_intent(q)
        with one_shot_permit(q, kind="meta-update", identity="1", old_value="0", new_value="1"):
            q.execute("UPDATE shared_anchor_meta SET reserved_position=1 WHERE singleton=1 AND reserved_position=0")
        q.commit()
        self.assertEqual(q.execute("SELECT status FROM shared_anchor_intents").fetchone()[0], "PREPARED")

    def test_intent_permit_binds_all_row_fields(self):
        q = self.make(); q.execute("BEGIN IMMEDIATE")
        intended = self.intent_row()
        tampered = list(intended); tampered[2] = "attacker-type"
        with self.assertRaises(sqlite3.IntegrityError):
            with one_shot_permit(
                q, kind="intent-insert", identity=intended[0], old_value="",
                new_value=intent_row_token(*intended),
            ):
                q.execute("INSERT INTO shared_anchor_intents VALUES(?,?,?,?,?,?,?,?,?,?,?)", tuple(tampered))
        q.rollback()

    def test_exact_confirmation_binds_receipt_and_row(self):
        q = self.make(); q.execute("BEGIN IMMEDIATE"); self.insert_intent(q)
        old = self.intent_row(); new = self.intent_row(receipt="binding-1", status="CONFIRMED")
        with one_shot_permit(
            q, kind="intent-confirm", identity="intent-1",
            old_value=intent_row_token(*old), new_value=intent_row_token(*new),
        ):
            q.execute("UPDATE shared_anchor_intents SET status='CONFIRMED',receipt_binding='binding-1' WHERE intent_id='intent-1'")
        q.commit()
        self.assertEqual(q.execute("SELECT status,receipt_binding FROM shared_anchor_intents").fetchone(), ("CONFIRMED","binding-1"))

    def test_confirmation_permit_rejects_different_receipt(self):
        q = self.make(); q.execute("BEGIN IMMEDIATE"); self.insert_intent(q)
        old = self.intent_row(); expected = self.intent_row(receipt="binding-1", status="CONFIRMED")
        with self.assertRaises(sqlite3.IntegrityError):
            with one_shot_permit(
                q, kind="intent-confirm", identity="intent-1",
                old_value=intent_row_token(*old), new_value=intent_row_token(*expected),
            ):
                q.execute("UPDATE shared_anchor_intents SET status='CONFIRMED',receipt_binding='evil' WHERE intent_id='intent-1'")
        q.rollback()

    def test_exact_receipt_insert_binds_full_receipt(self):
        q = self.make(); q.execute("BEGIN IMMEDIATE"); row = self.receipt_row()
        with one_shot_permit(
            q, kind="receipt-insert", identity=row[0], old_value="",
            new_value=receipt_row_token(*row),
        ):
            q.execute("INSERT INTO asymmetric_provider_receipts VALUES(?,?,?,?,?,?,?,?)", row)
        q.commit()
        self.assertEqual(q.execute("SELECT COUNT(*) FROM asymmetric_provider_receipts").fetchone()[0], 1)

    def test_receipt_permit_rejects_field_substitution(self):
        q = self.make(); q.execute("BEGIN IMMEDIATE"); row = self.receipt_row(); bad = list(row); bad[3] = 999
        with self.assertRaises(sqlite3.IntegrityError):
            with one_shot_permit(
                q, kind="receipt-insert", identity=row[0], old_value="",
                new_value=receipt_row_token(*row),
            ):
                q.execute("INSERT INTO asymmetric_provider_receipts VALUES(?,?,?,?,?,?,?,?)", tuple(bad))
        q.rollback()

    def test_receipt_identity_cannot_be_replaced(self):
        q = self.make(); q.execute("BEGIN IMMEDIATE"); row = self.receipt_row()
        with one_shot_permit(q, kind="receipt-insert", identity=row[0], old_value="", new_value=receipt_row_token(*row)):
            q.execute("INSERT INTO asymmetric_provider_receipts VALUES(?,?,?,?,?,?,?,?)", row)
        q.commit(); q.execute("BEGIN IMMEDIATE")
        with self.assertRaises(sqlite3.IntegrityError):
            with one_shot_permit(q, kind="receipt-insert", identity=row[0], old_value="", new_value=receipt_row_token(*row)):
                q.execute("INSERT OR REPLACE INTO asymmetric_provider_receipts VALUES(?,?,?,?,?,?,?,?)", row)
        q.rollback()

    def test_exact_watermark_paths_and_no_second_statement(self):
        q = self.make(); q.execute("BEGIN IMMEDIATE")
        with one_shot_permit(q, kind="watermark-insert", identity="component-A", old_value="", new_value="1"):
            q.execute("INSERT INTO component_anchor_watermarks VALUES('component-A',1)")
        with one_shot_permit(q, kind="watermark-update", identity="component-A", old_value="1", new_value="7"):
            q.execute("UPDATE component_anchor_watermarks SET position=7 WHERE component_id='component-A' AND position=1")
            with self.assertRaises(sqlite3.IntegrityError):
                q.execute("UPDATE component_anchor_watermarks SET position=999 WHERE component_id='component-A'")
        q.commit()

    def test_meta_jump_is_blocked_even_with_matching_jump_permit(self):
        q = self.make(); q.execute("BEGIN IMMEDIATE")
        with self.assertRaises(sqlite3.IntegrityError):
            with one_shot_permit(q, kind="meta-update", identity="1", old_value="0", new_value="999"):
                q.execute("UPDATE shared_anchor_meta SET reserved_position=999 WHERE singleton=1")
        q.rollback()


if __name__ == "__main__":
    unittest.main()
