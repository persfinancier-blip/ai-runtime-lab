import sqlite3
import unittest

from experiments.mutable_shared_anchor_writer.cross_table_guards import install_cross_table_guards
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


class CrossTableStateMachineGuardTests(unittest.TestCase):
    def make(self):
        q=sqlite3.connect(":memory:",isolation_level=None,factory=PermitConnection)
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
              intent_id TEXT PRIMARY KEY,component_id TEXT NOT NULL,intent_type TEXT NOT NULL,
              payload_digest TEXT NOT NULL,provider_id TEXT NOT NULL,provider_generation INTEGER NOT NULL,
              predecessor_position INTEGER NOT NULL,position INTEGER NOT NULL UNIQUE,
              request_id TEXT NOT NULL UNIQUE,status TEXT NOT NULL,receipt_binding TEXT
            );
            CREATE TABLE asymmetric_provider_generations(
              generation_id TEXT PRIMARY KEY,provider_id TEXT NOT NULL,generation INTEGER NOT NULL,
              public_key_hex TEXT NOT NULL
            );
            INSERT INTO asymmetric_provider_generations VALUES('g1','anchor-A',1,'pk');
            CREATE TABLE asymmetric_provider_head(
              singleton INTEGER PRIMARY KEY CHECK(singleton=1),
              generation_id TEXT NOT NULL,generation INTEGER NOT NULL
            );
            INSERT INTO asymmetric_provider_head VALUES(1,'g1',1);
            CREATE TABLE asymmetric_provider_receipts(
              request_id TEXT PRIMARY KEY,provider_id TEXT NOT NULL,generation INTEGER NOT NULL,
              position INTEGER NOT NULL,kind TEXT NOT NULL,challenge TEXT NOT NULL,
              signature TEXT NOT NULL,stable_binding TEXT NOT NULL
            );
            """
        )
        q.execute("BEGIN IMMEDIATE")
        install_cross_table_guards(q)
        q.commit()
        return q

    @staticmethod
    def intent(provider="anchor-A", generation=1, predecessor=0, position=1, request="request-1"):
        return (
            "intent-1","component-A","migration","a"*64,provider,generation,
            predecessor,position,request,"PREPARED",None,
        )

    def insert_intent(self,q,row=None):
        row=self.intent() if row is None else row
        with one_shot_permit(
            q,kind="intent-insert",identity=row[0],old_value="",new_value=intent_row_token(*row)
        ):
            q.execute("INSERT INTO shared_anchor_intents VALUES(?,?,?,?,?,?,?,?,?,?,?)",row)

    @staticmethod
    def receipt(request="request-1", provider="anchor-A", generation=1, position=1, kind="RECONCILE"):
        return (request,provider,generation,position,kind,"challenge","ab"*64,"cd"*32)

    def test_wrong_provider_intent_is_rejected_even_with_exact_permit(self):
        q=self.make(); q.execute("BEGIN IMMEDIATE")
        with self.assertRaises(sqlite3.IntegrityError):
            self.insert_intent(q,self.intent(provider="attacker",generation=999))
        q.rollback()

    def test_wrong_tail_intent_is_rejected_even_with_exact_permit(self):
        q=self.make(); q.execute("BEGIN IMMEDIATE")
        with self.assertRaises(sqlite3.IntegrityError):
            self.insert_intent(q,self.intent(predecessor=7,position=8))
        q.rollback()

    def test_position_jump_is_rejected_even_with_exact_permit(self):
        q=self.make(); q.execute("BEGIN IMMEDIATE")
        with self.assertRaises(sqlite3.IntegrityError):
            self.insert_intent(q,self.intent(predecessor=0,position=999,request="request-999"))
        q.rollback()

    def test_meta_cannot_jump_even_if_gap_intent_is_present_out_of_band(self):
        q=self.make()
        q.execute("DROP TRIGGER lab091_v3_intent_requires_current_tail_and_provider")
        q.execute(
            "INSERT INTO shared_anchor_intents VALUES(?,?,?,?,?,?,?,?,?,?,?)",
            self.intent(predecessor=0,position=999,request="request-999"),
        )
        q.execute("BEGIN IMMEDIATE")
        with self.assertRaises(sqlite3.IntegrityError):
            q.execute("UPDATE shared_anchor_meta SET reserved_position=999 WHERE singleton=1")
        q.rollback()

    def test_meta_advance_requires_the_prepared_intent_row(self):
        q=self.make(); q.execute("BEGIN IMMEDIATE")
        with self.assertRaises(sqlite3.IntegrityError):
            q.execute("UPDATE shared_anchor_meta SET reserved_position=1 WHERE singleton=1")
        self.insert_intent(q)
        q.execute("UPDATE shared_anchor_meta SET reserved_position=1 WHERE singleton=1")
        self.assertEqual(q.execute("SELECT reserved_position FROM shared_anchor_meta").fetchone()[0],1)
        q.rollback()

    def test_orphan_receipt_is_rejected_even_with_exact_permit(self):
        q=self.make(); q.execute("BEGIN IMMEDIATE")
        row=self.receipt(request="orphan")
        with self.assertRaises(sqlite3.IntegrityError):
            with one_shot_permit(
                q,kind="receipt-insert",identity=row[0],old_value="",new_value=receipt_row_token(*row)
            ):
                q.execute("INSERT INTO asymmetric_provider_receipts VALUES(?,?,?,?,?,?,?,?)",row)
        q.rollback()

    def test_receipt_must_be_reconcile_for_matching_prepared_intent(self):
        q=self.make(); q.execute("BEGIN IMMEDIATE"); self.insert_intent(q)
        bad=self.receipt(kind="READ")
        with self.assertRaises(sqlite3.IntegrityError):
            with one_shot_permit(
                q,kind="receipt-insert",identity=bad[0],old_value="",new_value=receipt_row_token(*bad)
            ):
                q.execute("INSERT INTO asymmetric_provider_receipts VALUES(?,?,?,?,?,?,?,?)",bad)
        good=self.receipt()
        with one_shot_permit(
            q,kind="receipt-insert",identity=good[0],old_value="",new_value=receipt_row_token(*good)
        ):
            q.execute("INSERT INTO asymmetric_provider_receipts VALUES(?,?,?,?,?,?,?,?)",good)
        self.assertEqual(q.execute("SELECT request_id FROM asymmetric_provider_receipts").fetchone()[0],"request-1")
        q.rollback()

    def test_provider_rotation_changes_accepted_intent_generation(self):
        q=self.make()
        q.execute("UPDATE asymmetric_provider_head SET generation_id='g2',generation=2 WHERE singleton=1")
        q.execute("INSERT INTO asymmetric_provider_generations VALUES('g2','anchor-A',2,'pk2')")
        q.execute("BEGIN IMMEDIATE")
        with self.assertRaises(sqlite3.IntegrityError):
            self.insert_intent(q,self.intent(provider="anchor-A",generation=1))
        self.insert_intent(q,self.intent(provider="anchor-A",generation=2))
        q.rollback()


if __name__=="__main__": unittest.main()
