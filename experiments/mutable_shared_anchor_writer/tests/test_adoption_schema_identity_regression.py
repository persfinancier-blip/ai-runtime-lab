import sqlite3
import unittest

from experiments.mutable_shared_anchor_writer.adoption_validation import (
    AdoptionValidationError,
    validate_existing_mutable_state_locked,
)
from experiments.mutable_shared_anchor_writer.state_machine_udfs import expected_request_id


class AdoptionSchemaIdentityRegressionTests(unittest.TestCase):
    def make_weakened_db(self, reserved_position=0):
        q = sqlite3.connect(":memory:", isolation_level=None)
        q.executescript(
            """
            CREATE TABLE shared_anchor_meta(singleton INTEGER,reserved_position INTEGER);
            CREATE TABLE shared_anchor_intents(
              intent_id TEXT,component_id TEXT,intent_type TEXT,payload_digest TEXT,
              provider_id TEXT,provider_generation INTEGER,predecessor_position INTEGER,
              position INTEGER,request_id TEXT,status TEXT,receipt_binding TEXT
            );
            CREATE TABLE component_anchor_watermarks(component_id TEXT,position INTEGER);
            CREATE TABLE asymmetric_provider_receipts(
              request_id TEXT,provider_id TEXT,generation INTEGER,position INTEGER,
              kind TEXT,challenge TEXT,signature TEXT,stable_binding TEXT
            );
            """
        )
        q.execute("INSERT INTO shared_anchor_meta VALUES(1,?)", (reserved_position,))
        return q

    def insert_confirmed(self, q, *, position, intent_id):
        digest = "a" * 64
        request_id = expected_request_id(
            position, intent_id, "component-A", "migration", digest
        )
        q.execute(
            "INSERT INTO shared_anchor_intents VALUES(?,?,?,?,?,?,?,?,?,'CONFIRMED',?)",
            (
                intent_id,
                "component-A",
                "migration",
                digest,
                "anchor-A",
                1,
                position - 1,
                position,
                request_id,
                "b" * 64,
            ),
        )
        q.execute(
            "INSERT INTO asymmetric_provider_receipts VALUES(?,?,?,?,?,?,?,?)",
            (
                request_id,
                "anchor-A",
                1,
                position,
                "RECONCILE",
                "challenge",
                "signature",
                "b" * 64,
            ),
        )
        return request_id

    def assert_adoption_rejected(self, q):
        q.execute("BEGIN IMMEDIATE")
        with self.assertRaises(AdoptionValidationError):
            validate_existing_mutable_state_locked(q)
        q.rollback()

    def test_duplicate_intent_identity_from_weakened_legacy_schema_is_rejected(self):
        q = self.make_weakened_db(reserved_position=2)
        self.insert_confirmed(q, position=1, intent_id="same-intent")
        self.insert_confirmed(q, position=2, intent_id="same-intent")
        self.assert_adoption_rejected(q)

    def test_duplicate_meta_singleton_from_weakened_legacy_schema_is_rejected(self):
        q = self.make_weakened_db()
        q.execute("INSERT INTO shared_anchor_meta VALUES(1,0)")
        self.assert_adoption_rejected(q)

    def test_duplicate_watermark_identity_from_weakened_legacy_schema_is_rejected(self):
        q = self.make_weakened_db()
        q.execute("INSERT INTO component_anchor_watermarks VALUES('component-A',0)")
        q.execute("INSERT INTO component_anchor_watermarks VALUES('component-A',0)")
        self.assert_adoption_rejected(q)

    def test_duplicate_receipt_identity_from_weakened_legacy_schema_is_rejected(self):
        q = self.make_weakened_db(reserved_position=1)
        request_id = self.insert_confirmed(q, position=1, intent_id="intent-1")
        q.execute(
            "INSERT INTO asymmetric_provider_receipts VALUES(?,?,?,?,?,?,?,?)",
            (
                request_id,
                "anchor-A",
                1,
                1,
                "RECONCILE",
                "challenge-2",
                "signature-2",
                "b" * 64,
            ),
        )
        self.assert_adoption_rejected(q)


if __name__ == "__main__":
    unittest.main()
