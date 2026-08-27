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
)


class IntentAlternateUniqueReplaceRegressionTests(unittest.TestCase):
    def make_db(self):
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

        original = (
            "intent-original",
            "component-A",
            "migration",
            "a" * 64,
            "anchor-A",
            1,
            0,
            1,
            "request-original",
            "PREPARED",
            None,
        )
        q.execute("BEGIN IMMEDIATE")
        with one_shot_permit(
            q,
            kind="intent-insert",
            identity=original[0],
            old_value="",
            new_value=intent_row_token(*original),
        ):
            q.execute(
                "INSERT INTO shared_anchor_intents VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                original,
            )
        q.commit()
        return q, original

    def assert_original_unchanged(self, q, original):
        row = q.execute(
            "SELECT intent_id,component_id,intent_type,payload_digest,"
            "provider_id,provider_generation,predecessor_position,position,"
            "request_id,status,receipt_binding "
            "FROM shared_anchor_intents"
        ).fetchall()
        self.assertEqual(row, [original])

    def test_fresh_primary_key_cannot_replace_existing_request_id(self):
        q, original = self.make_db()
        candidate = (
            "intent-attacker-request",
            "component-B",
            "migration",
            "b" * 64,
            "anchor-A",
            1,
            1,
            2,
            original[8],
            "PREPARED",
            None,
        )
        q.execute("BEGIN IMMEDIATE")
        with self.assertRaises(sqlite3.IntegrityError):
            with one_shot_permit(
                q,
                kind="intent-insert",
                identity=candidate[0],
                old_value="",
                new_value=intent_row_token(*candidate),
            ):
                q.execute(
                    "INSERT OR REPLACE INTO shared_anchor_intents "
                    "VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                    candidate,
                )
        q.rollback()
        self.assert_original_unchanged(q, original)

    def test_fresh_primary_key_cannot_replace_existing_position(self):
        q, original = self.make_db()
        candidate = (
            "intent-attacker-position",
            "component-B",
            "migration",
            "c" * 64,
            "anchor-A",
            1,
            0,
            original[7],
            "request-attacker-position",
            "PREPARED",
            None,
        )
        q.execute("BEGIN IMMEDIATE")
        with self.assertRaises(sqlite3.IntegrityError):
            with one_shot_permit(
                q,
                kind="intent-insert",
                identity=candidate[0],
                old_value="",
                new_value=intent_row_token(*candidate),
            ):
                q.execute(
                    "INSERT OR REPLACE INTO shared_anchor_intents "
                    "VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                    candidate,
                )
        q.rollback()
        self.assert_original_unchanged(q, original)


if __name__ == "__main__":
    unittest.main()
