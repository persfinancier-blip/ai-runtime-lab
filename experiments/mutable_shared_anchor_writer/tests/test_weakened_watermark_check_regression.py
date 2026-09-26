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


class WeakenedWatermarkCheckRegressionTests(unittest.TestCase):
    def make_db(self):
        q = sqlite3.connect(":memory:", isolation_level=None, factory=PermitConnection)
        install_operation_permit_udf(q)
        q.executescript(
            """
            CREATE TABLE shared_anchor_meta(singleton INTEGER PRIMARY KEY,reserved_position INTEGER NOT NULL);
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
            -- Deliberately legacy/weakened: canonical LAB-080 has CHECK(position>=0).
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

    def test_negative_insert_is_rejected_even_if_legacy_check_is_missing(self):
        q = self.make_db()
        q.execute("BEGIN IMMEDIATE")
        with one_shot_permit(
            q,
            kind="watermark-insert",
            identity="component-a",
            old_value="",
            new_value="-1",
        ):
            with self.assertRaises(sqlite3.IntegrityError):
                q.execute(
                    "INSERT INTO component_anchor_watermarks VALUES(?,?)",
                    ("component-a", -1),
                )
        q.rollback()

    def test_zero_insert_still_uses_normal_exact_permit_path(self):
        q = self.make_db()
        q.execute("BEGIN IMMEDIATE")
        with one_shot_permit(
            q,
            kind="watermark-insert",
            identity="component-a",
            old_value="",
            new_value="0",
        ):
            q.execute(
                "INSERT INTO component_anchor_watermarks VALUES(?,?)",
                ("component-a", 0),
            )
        q.commit()
        self.assertEqual(
            q.execute(
                "SELECT component_id,position FROM component_anchor_watermarks"
            ).fetchall(),
            [("component-a", 0)],
        )


if __name__ == "__main__":
    unittest.main()
