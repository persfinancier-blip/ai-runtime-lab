import sqlite3
import unittest

from experiments.mutable_shared_anchor_writer.adoption_validation import (
    AdoptionValidationError,
    validate_existing_mutable_state_locked,
)


class AdoptionPartialUniqueRegressionTests(unittest.TestCase):
    def make_db(self, partial_target: str):
        q = sqlite3.connect(":memory:", isolation_level=None)
        intent_id_decl = (
            "intent_id TEXT" if partial_target == "intent_id" else "intent_id TEXT PRIMARY KEY"
        )
        watermark_id_decl = (
            "component_id TEXT" if partial_target == "watermark" else "component_id TEXT PRIMARY KEY"
        )
        receipt_id_decl = (
            "request_id TEXT" if partial_target == "receipt" else "request_id TEXT PRIMARY KEY"
        )
        position_where = "WHERE status='CONFIRMED'" if partial_target == "position" else ""
        request_where = "WHERE status='CONFIRMED'" if partial_target == "request_id" else ""
        q.executescript(
            f"""
            CREATE TABLE shared_anchor_meta(
              singleton INTEGER PRIMARY KEY CHECK(singleton=1),
              reserved_position INTEGER NOT NULL CHECK(reserved_position>=0)
            );
            INSERT INTO shared_anchor_meta VALUES(1,0);
            CREATE TABLE shared_anchor_intents(
              {intent_id_decl},
              component_id TEXT NOT NULL,
              intent_type TEXT NOT NULL,
              payload_digest TEXT NOT NULL,
              provider_id TEXT NOT NULL,
              provider_generation INTEGER NOT NULL,
              predecessor_position INTEGER NOT NULL,
              position INTEGER NOT NULL,
              request_id TEXT NOT NULL,
              status TEXT NOT NULL CHECK(status IN ('PREPARED','CONFIRMED')),
              receipt_binding TEXT
            );
            CREATE UNIQUE INDEX intent_position_unique
              ON shared_anchor_intents(position) {position_where};
            CREATE UNIQUE INDEX intent_request_unique
              ON shared_anchor_intents(request_id) {request_where};
            CREATE TABLE component_anchor_watermarks(
              {watermark_id_decl},
              position INTEGER NOT NULL CHECK(position>=0)
            );
            CREATE TABLE asymmetric_provider_receipts(
              {receipt_id_decl},
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
        if partial_target == "intent_id":
            q.execute(
                "CREATE UNIQUE INDEX intent_id_partial ON shared_anchor_intents(intent_id) "
                "WHERE status='CONFIRMED'"
            )
        if partial_target == "watermark":
            q.execute(
                "CREATE UNIQUE INDEX watermark_component_partial "
                "ON component_anchor_watermarks(component_id) WHERE position>0"
            )
        if partial_target == "receipt":
            q.execute(
                "CREATE UNIQUE INDEX receipt_request_partial "
                "ON asymmetric_provider_receipts(request_id) WHERE kind='RECONCILE'"
            )
        return q

    def test_partial_unique_indexes_do_not_satisfy_identity_contract(self):
        for target in (
            "intent_id",
            "position",
            "request_id",
            "watermark",
            "receipt",
        ):
            with self.subTest(target=target):
                q = self.make_db(target)
                q.execute("BEGIN IMMEDIATE")
                with self.assertRaises(AdoptionValidationError):
                    validate_existing_mutable_state_locked(q)
                q.rollback()


if __name__ == "__main__":
    unittest.main()
