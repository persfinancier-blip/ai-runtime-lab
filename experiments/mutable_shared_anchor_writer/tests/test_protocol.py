import sqlite3
import tempfile
import unittest
from pathlib import Path

from experiments.mutable_shared_anchor_writer.protocol import (
    InvalidLedgerMutation,
    MutableLedgerWriter,
)


def intent_row(i="i1", pos=1):
    return (i, "component-A", "migration", "a"*64, "anchor-A", 1, pos-1, pos, f"req-{i}")


class Tests(unittest.TestCase):
    def make(self, td):
        return MutableLedgerWriter(Path(td)/"db")

    def test_supported_reserve_confirm_watermark_receipt(self):
        with tempfile.TemporaryDirectory() as td:
            w=self.make(td)
            w.reserve(intent_row())
            w.confirm("i1", "b"*64)
            w.advance_watermark("component-A",0,1)
            w.record_receipt(("req-i1","anchor-A",1,1,"RECONCILE","c"*64))
            q=w.connection
            self.assertEqual(q.execute("SELECT reserved_position FROM shared_anchor_meta").fetchone()[0],1)
            self.assertEqual(q.execute("SELECT status FROM shared_anchor_intents").fetchone()[0],"CONFIRMED")
            self.assertEqual(q.execute("SELECT position FROM component_anchor_watermarks").fetchone()[0],1)
            self.assertEqual(q.execute("SELECT COUNT(*) FROM asymmetric_provider_receipts").fetchone()[0],1)
            w.close()

    def test_raw_dml_on_broker_handle_is_denied(self):
        with tempfile.TemporaryDirectory() as td:
            w=self.make(td); q=w.connection
            attacks=[
                "UPDATE shared_anchor_meta SET reserved_position=99",
                "INSERT INTO shared_anchor_intents VALUES('x','c','migration','"+"a"*64+"','anchor-A',1,0,1,'r','PREPARED',NULL)",
                "INSERT INTO component_anchor_watermarks VALUES('evil',9)",
                "INSERT INTO asymmetric_provider_receipts VALUES('r','anchor-A',1,1,'RECONCILE','"+"c"*64+"')",
            ]
            for sql in attacks:
                with self.assertRaises(sqlite3.DatabaseError): q.execute(sql)
            w.close()

    def test_other_writable_connection_fails_closed_without_function(self):
        with tempfile.TemporaryDirectory() as td:
            w=self.make(td)
            q=sqlite3.connect(w.path)
            with self.assertRaises(sqlite3.DatabaseError): q.execute("UPDATE shared_anchor_meta SET reserved_position=9")
            q.close(); w.close()

    def test_intent_cannot_be_rewritten_after_confirm(self):
        with tempfile.TemporaryDirectory() as td:
            w=self.make(td); w.reserve(intent_row()); w.confirm("i1","b"*64)
            with self.assertRaises(sqlite3.DatabaseError):
                with w._write_txn() as q:
                    q.execute("UPDATE shared_anchor_intents SET receipt_binding='"+"d"*64+"' WHERE intent_id='i1'")
            w.close()

    def test_intent_identity_cannot_change_during_confirm(self):
        with tempfile.TemporaryDirectory() as td:
            w=self.make(td); w.reserve(intent_row())
            with self.assertRaises(sqlite3.DatabaseError):
                with w._write_txn() as q:
                    q.execute("UPDATE shared_anchor_intents SET status='CONFIRMED',receipt_binding=?,component_id='evil' WHERE intent_id='i1'",("b"*64,))
            w.close()

    def test_watermark_rollback_blocked_even_authorized(self):
        with tempfile.TemporaryDirectory() as td:
            w=self.make(td); w.advance_watermark("c",0,5)
            with self.assertRaises(InvalidLedgerMutation): w.advance_watermark("c",5,4)
            w.close()

    def test_receipt_is_append_only(self):
        with tempfile.TemporaryDirectory() as td:
            w=self.make(td); w.record_receipt(("r","anchor-A",1,1,"RECONCILE","c"*64))
            for sql in ("UPDATE asymmetric_provider_receipts SET position=2 WHERE request_id='r'", "DELETE FROM asymmetric_provider_receipts WHERE request_id='r'", "INSERT OR REPLACE INTO asymmetric_provider_receipts VALUES('r','anchor-A',1,2,'RECONCILE','"+"d"*64+"')"):
                with self.assertRaises(sqlite3.DatabaseError):
                    with w._write_txn() as q: q.execute(sql)
            w.close()

    def test_replace_existing_intent_and_watermark_denied_even_authorized(self):
        with tempfile.TemporaryDirectory() as td:
            w=self.make(td); w.reserve(intent_row()); w.advance_watermark("component-A",0,1)
            with self.assertRaises(sqlite3.DatabaseError):
                with w._write_txn() as q:
                    q.execute("INSERT OR REPLACE INTO shared_anchor_intents VALUES('i1','component-A','migration','"+"a"*64+"','anchor-A',1,0,1,'req-i1','PREPARED',NULL)")
            with self.assertRaises(sqlite3.DatabaseError):
                with w._write_txn() as q:
                    q.execute("INSERT OR REPLACE INTO component_anchor_watermarks VALUES('component-A',99)")
            w.close()

    def test_negative_control_writable_connection_can_spoof_udf_if_lab087_boundary_is_absent(self):
        with tempfile.TemporaryDirectory() as td:
            w=self.make(td)
            q=sqlite3.connect(w.path)
            q.create_function("lab091_writer_authorized",0,lambda:1)
            q.execute("UPDATE shared_anchor_meta SET reserved_position=9")
            q.commit()
            self.assertEqual(q.execute("SELECT reserved_position FROM shared_anchor_meta").fetchone()[0],9)
            q.close(); w.close()

    def test_failure_rolls_back_authorization_and_data(self):
        with tempfile.TemporaryDirectory() as td:
            w=self.make(td)
            with self.assertRaises(RuntimeError):
                with w._write_txn() as q:
                    q.execute("UPDATE shared_anchor_meta SET reserved_position=1")
                    raise RuntimeError("crash")
            self.assertEqual(w.connection.execute("SELECT reserved_position FROM shared_anchor_meta").fetchone()[0],0)
            with self.assertRaises(sqlite3.DatabaseError): w.connection.execute("UPDATE shared_anchor_meta SET reserved_position=2")
            w.close()

    def test_nested_authorization_denied(self):
        with tempfile.TemporaryDirectory() as td:
            w=self.make(td)
            with self.assertRaises(Exception):
                with w._write_txn():
                    with w._write_txn(): pass
            w.close()

if __name__=="__main__": unittest.main()
