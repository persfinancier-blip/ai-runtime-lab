import sqlite3
import unittest

from experiments.mutable_shared_anchor_writer.adoption_validation import (
    AdoptionValidationError,
    validate_existing_mutable_state_locked,
)
from experiments.mutable_shared_anchor_writer.state_machine_udfs import expected_request_id


class AdoptionCollationRegressionTests(unittest.TestCase):
    def make_db(self, target=None):
        q = sqlite3.connect(":memory:", isolation_level=None)
        intent_id = (
            "intent_id TEXT PRIMARY KEY COLLATE NOCASE"
            if target == "intent_id"
            else "intent_id TEXT PRIMARY KEY"
        )
        request_id = (
            "request_id TEXT NOT NULL UNIQUE COLLATE NOCASE"
            if target == "intent_request_id"
            else "request_id TEXT NOT NULL UNIQUE"
        )
        watermark_component = (
            "component_id TEXT PRIMARY KEY COLLATE NOCASE"
            if target == "watermark_component"
            else "component_id TEXT PRIMARY KEY"
        )
        receipt_request = (
            "request_id TEXT PRIMARY KEY COLLATE NOCASE"
            if target == "receipt_request_id"
            else "request_id TEXT PRIMARY KEY"
        )
        q.executescript(
            f"""
            CREATE TABLE shared_anchor_meta(
              singleton INTEGER PRIMARY KEY CHECK(singleton=1),
              reserved_position INTEGER NOT NULL CHECK(reserved_position>=0)
            );
            INSERT INTO shared_anchor_meta VALUES(1,0);
            CREATE TABLE shared_anchor_intents(
              {intent_id},
              component_id TEXT NOT NULL,
              intent_type TEXT NOT NULL,
              payload_digest TEXT NOT NULL,
              provider_id TEXT NOT NULL,
              provider_generation INTEGER NOT NULL,
              predecessor_position INTEGER NOT NULL,
              position INTEGER NOT NULL UNIQUE,
              {request_id},
              status TEXT NOT NULL CHECK(status IN ('PREPARED','CONFIRMED')),
              receipt_binding TEXT
            );
            CREATE TABLE component_anchor_watermarks(
              {watermark_component},
              position INTEGER NOT NULL CHECK(position>=0)
            );
            CREATE TABLE asymmetric_provider_receipts(
              {receipt_request},
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

    def validate(self, q):
        q.execute("BEGIN IMMEDIATE")
        try:
            return validate_existing_mutable_state_locked(q)
        finally:
            q.rollback()

    def test_binary_canonical_identity_constraints_are_accepted(self):
        self.assertTrue(self.validate(self.make_db()))

    def test_nonbinary_text_identity_constraints_fail_closed(self):
        for target in (
            "intent_id",
            "intent_request_id",
            "watermark_component",
            "receipt_request_id",
        ):
            with self.subTest(target=target):
                with self.assertRaises(AdoptionValidationError):
                    self.validate(self.make_db(target))

    def test_nocase_unique_is_behaviorally_incompatible_with_exact_identity(self):
        q = sqlite3.connect(":memory:")
        q.execute("CREATE TABLE t(id TEXT UNIQUE COLLATE NOCASE)")
        q.execute("INSERT INTO t VALUES('Intent-A')")
        with self.assertRaises(sqlite3.IntegrityError):
            q.execute("INSERT INTO t VALUES('intent-a')")
        q.close()

    def test_orphan_check_uses_binary_identity_even_with_binary_unique_overlay(self):
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
              request_id TEXT COLLATE NOCASE NOT NULL,
              status TEXT NOT NULL CHECK(status IN ('PREPARED','CONFIRMED')),
              receipt_binding TEXT
            );
            CREATE UNIQUE INDEX lab091_test_intent_request_binary
              ON shared_anchor_intents(request_id COLLATE BINARY);
            CREATE TABLE component_anchor_watermarks(
              component_id TEXT PRIMARY KEY,
              position INTEGER NOT NULL CHECK(position>=0)
            );
            CREATE TABLE asymmetric_provider_receipts(
              request_id TEXT COLLATE NOCASE NOT NULL,
              provider_id TEXT NOT NULL,
              generation INTEGER NOT NULL,
              position INTEGER NOT NULL,
              kind TEXT NOT NULL,
              challenge TEXT NOT NULL,
              signature TEXT NOT NULL,
              stable_binding TEXT NOT NULL
            );
            CREATE UNIQUE INDEX lab091_test_receipt_request_binary
              ON asymmetric_provider_receipts(request_id COLLATE BINARY);
            """
        )
        digest = "0" * 64
        request_id = expected_request_id(1, "intent-a", "component-a", "migration", digest)
        q.execute(
            "INSERT INTO shared_anchor_intents VALUES(?,?,?,?,?,?,?,?,?,'CONFIRMED',?)",
            (
                "intent-a",
                "component-a",
                "migration",
                digest,
                "provider-a",
                1,
                0,
                1,
                request_id,
                "binding",
            ),
        )
        q.execute(
            "INSERT INTO asymmetric_provider_receipts VALUES(?,?,?,?,?,?,?,?)",
            (
                request_id.upper(),
                "provider-a",
                1,
                1,
                "RECONCILE",
                "challenge",
                "signature",
                "binding",
            ),
        )
        with self.assertRaises(AdoptionValidationError):
            self.validate(q)
        q.close()


if __name__ == "__main__":
    unittest.main()
