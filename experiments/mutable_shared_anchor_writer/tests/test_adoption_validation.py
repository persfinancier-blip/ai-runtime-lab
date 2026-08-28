import sqlite3
import unittest

from experiments.mutable_shared_anchor_writer.adoption_validation import (
    AdoptionValidationError,
    validate_existing_mutable_state_locked,
)
from experiments.mutable_shared_anchor_writer.state_machine_udfs import expected_request_id


class AdoptionValidationTests(unittest.TestCase):
    def make_db(self):
        q = sqlite3.connect(":memory:", isolation_level=None)
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
        return q

    def insert_intent(self, q, *, request_id=None):
        intent_id = "intent-1"
        component_id = "component-A"
        intent_type = "migration"
        payload_digest = "a" * 64
        position = 1
        if request_id is None:
            request_id = expected_request_id(
                position, intent_id, component_id, intent_type, payload_digest
            )
        q.execute(
            "INSERT INTO shared_anchor_intents VALUES(?,?,?,?,?,?,?,?,?,'PREPARED',NULL)",
            (
                intent_id,
                component_id,
                intent_type,
                payload_digest,
                "anchor-A",
                1,
                0,
                position,
                request_id,
            ),
        )
        return request_id

    def test_valid_existing_prepared_state_is_adoptable(self):
        q = self.make_db()
        self.insert_intent(q)
        q.execute("BEGIN IMMEDIATE")
        self.assertTrue(validate_existing_mutable_state_locked(q))
        q.rollback()

    def test_non_deterministic_existing_request_id_is_rejected(self):
        q = self.make_db()
        self.insert_intent(q, request_id="attacker-chosen-request")
        q.execute("BEGIN IMMEDIATE")
        with self.assertRaises(AdoptionValidationError):
            validate_existing_mutable_state_locked(q)
        q.rollback()

    def test_orphan_existing_receipt_is_rejected(self):
        q = self.make_db()
        self.insert_intent(q)
        q.execute(
            "INSERT INTO asymmetric_provider_receipts VALUES(?,?,?,?,?,?,?,?)",
            (
                "orphan-request",
                "anchor-A",
                1,
                1,
                "RECONCILE",
                "challenge",
                "signature",
                "b" * 64,
            ),
        )
        q.execute("BEGIN IMMEDIATE")
        with self.assertRaises(AdoptionValidationError):
            validate_existing_mutable_state_locked(q)
        q.rollback()

    def test_existing_receipt_owned_by_prepared_intent_is_allowed(self):
        q = self.make_db()
        request_id = self.insert_intent(q)
        q.execute(
            "INSERT INTO asymmetric_provider_receipts VALUES(?,?,?,?,?,?,?,?)",
            (
                request_id,
                "anchor-A",
                1,
                1,
                "RECONCILE",
                "challenge",
                "signature",
                "b" * 64,
            ),
        )
        q.execute("BEGIN IMMEDIATE")
        self.assertTrue(validate_existing_mutable_state_locked(q))
        q.rollback()

    def test_requires_write_transaction(self):
        q = self.make_db()
        with self.assertRaises(AdoptionValidationError):
            validate_existing_mutable_state_locked(q)


if __name__ == "__main__":
    unittest.main()
