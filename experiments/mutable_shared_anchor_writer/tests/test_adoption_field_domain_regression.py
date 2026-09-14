import sqlite3
import unittest

from experiments.mutable_shared_anchor_writer.adoption_validation import (
    AdoptionValidationError,
    validate_existing_mutable_state_locked,
)
from experiments.mutable_shared_anchor_writer.state_machine_udfs import expected_request_id


class AdoptionFieldDomainRegressionTests(unittest.TestCase):
    def make_db(self):
        q = sqlite3.connect(":memory:", isolation_level=None)
        q.executescript(
            """
            CREATE TABLE shared_anchor_meta(
              singleton INTEGER PRIMARY KEY CHECK(singleton=1),
              reserved_position INTEGER NOT NULL CHECK(reserved_position>=0)
            );
            INSERT INTO shared_anchor_meta VALUES(1,1);
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
              status TEXT NOT NULL CHECK(status IN ('PREPARED','CONFIRMED')),
              receipt_binding TEXT
            );
            CREATE TABLE component_anchor_watermarks(
              component_id TEXT PRIMARY KEY,
              position INTEGER NOT NULL CHECK(position>=0)
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

    def assert_rejected(self, **overrides):
        values = {
            "intent_id": "intent-1",
            "component_id": "component-A",
            "intent_type": "migration",
            "payload_digest": "a" * 64,
            "provider_id": "anchor-A",
            "provider_generation": 1,
        }
        values.update(overrides)
        q = self.make_db()
        request_id = expected_request_id(
            1,
            values["intent_id"],
            values["component_id"],
            values["intent_type"],
            values["payload_digest"],
        )
        q.execute(
            "INSERT INTO shared_anchor_intents VALUES(?,?,?,?,?,?,?,?,?,'PREPARED',NULL)",
            (
                values["intent_id"],
                values["component_id"],
                values["intent_type"],
                values["payload_digest"],
                values["provider_id"],
                values["provider_generation"],
                0,
                1,
                request_id,
            ),
        )
        q.execute("BEGIN IMMEDIATE")
        with self.assertRaises(AdoptionValidationError):
            validate_existing_mutable_state_locked(q)
        q.rollback()

    def test_unknown_intent_type_is_rejected(self):
        self.assert_rejected(intent_type="attacker_type")

    def test_empty_intent_identity_is_rejected(self):
        self.assert_rejected(intent_id="")

    def test_empty_component_identity_is_rejected(self):
        self.assert_rejected(component_id="")

    def test_noncanonical_payload_digest_is_rejected(self):
        self.assert_rejected(payload_digest="not-a-digest")

    def test_uppercase_payload_digest_is_rejected(self):
        self.assert_rejected(payload_digest="A" * 64)

    def test_empty_provider_identity_is_rejected(self):
        self.assert_rejected(provider_id="")

    def test_nonpositive_provider_generation_is_rejected(self):
        self.assert_rejected(provider_generation=0)

    def test_valid_supported_prepared_row_is_still_adoptable(self):
        q = self.make_db()
        payload_digest = "a" * 64
        request_id = expected_request_id(
            1, "intent-1", "component-A", "migration", payload_digest
        )
        q.execute(
            "INSERT INTO shared_anchor_intents VALUES(?,?,?,?,?,?,?,?,?,'PREPARED',NULL)",
            (
                "intent-1", "component-A", "migration", payload_digest,
                "anchor-A", 1, 0, 1, request_id,
            ),
        )
        q.execute("BEGIN IMMEDIATE")
        self.assertTrue(validate_existing_mutable_state_locked(q))
        q.rollback()


if __name__ == "__main__":
    unittest.main()
