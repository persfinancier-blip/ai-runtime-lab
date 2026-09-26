import sqlite3
import unittest

from experiments.mutable_shared_anchor_writer.operation_permit import (
    PermitConnection, install_operation_permit_udf, one_shot_permit
)
from experiments.mutable_shared_anchor_writer.row_tokens import install_row_token_udfs
from experiments.mutable_shared_anchor_writer.full_operation_guards import install_full_operation_guards


class LegacySurfacePersistenceTests(unittest.TestCase):
    def make(self):
        q=sqlite3.connect(":memory:", isolation_level=None, factory=PermitConnection)
        install_operation_permit_udf(q); install_row_token_udfs(q)
        q.executescript("""
          CREATE TABLE shared_anchor_meta(singleton INTEGER PRIMARY KEY,reserved_position INTEGER NOT NULL);
          INSERT INTO shared_anchor_meta VALUES(1,0);
          CREATE TABLE shared_anchor_intents(
            intent_id TEXT PRIMARY KEY,component_id TEXT,intent_type TEXT,payload_digest TEXT,
            provider_id TEXT,provider_generation INTEGER,predecessor_position INTEGER,position INTEGER,
            request_id TEXT UNIQUE,status TEXT,receipt_binding TEXT
          );
          CREATE TABLE component_anchor_watermarks(component_id TEXT PRIMARY KEY,position INTEGER);
          CREATE TABLE asymmetric_provider_receipts(
            request_id TEXT PRIMARY KEY,provider_id TEXT,generation INTEGER,position INTEGER,
            kind TEXT,challenge TEXT,signature TEXT,stable_binding TEXT
          );
        """)
        q.execute("BEGIN IMMEDIATE"); install_full_operation_guards(q); q.commit()
        return q

    @staticmethod
    def legacy_reinstall(q):
        # Exact meta-relevant behavior of the pre-fix LAB-091 legacy installer:
        # it knows only the old trigger names.
        for name in (
            "lab091_meta_no_insert","lab091_meta_authorized_update","lab091_meta_no_delete",
            "lab091_meta_exact_update",
        ):
            q.execute(f"DROP TRIGGER IF EXISTS {name}")
        q.execute("""CREATE TRIGGER lab091_meta_authorized_update
          BEFORE UPDATE ON shared_anchor_meta
          WHEN lab091_writer_authorized()!=1
          BEGIN SELECT RAISE(ABORT,'legacy writer required'); END""")

    def test_legacy_reinstall_cannot_remove_v2_guard(self):
        q=self.make()
        self.legacy_reinstall(q)
        q.create_function("lab091_writer_authorized",0,lambda:1)
        q.execute("BEGIN IMMEDIATE")
        with self.assertRaises(sqlite3.Error):
            # Legacy connection lacks lab091_consume_permit in production. This
            # focused connection still has it, so exact v2 guard returns 0 and
            # raises IntegrityError instead; accept either fail-closed path.
            q.execute("UPDATE shared_anchor_meta SET reserved_position=999 WHERE singleton=1")
        q.rollback()

    def test_operation_scoped_writer_still_works_after_legacy_reinstall(self):
        q=self.make()
        self.legacy_reinstall(q)
        q.create_function("lab091_writer_authorized",0,lambda:1)
        q.execute("BEGIN IMMEDIATE")
        with one_shot_permit(q,kind="meta-update",identity="1",old_value="0",new_value="1"):
            q.execute("UPDATE shared_anchor_meta SET reserved_position=1 WHERE singleton=1")
        q.commit()
        self.assertEqual(q.execute("SELECT reserved_position FROM shared_anchor_meta").fetchone()[0],1)


if __name__=="__main__": unittest.main()
