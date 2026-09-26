from __future__ import annotations

import sqlite3

from experiments.mutable_shared_anchor_writer.adoption_validation import _unique_key_sets


def test_binary_unique_identity_can_still_have_nocase_lookup_semantics():
    q = sqlite3.connect(":memory:")
    try:
        q.executescript(
            """
            CREATE TABLE shared_anchor_intents(
              intent_id TEXT COLLATE NOCASE NOT NULL,
              component_id TEXT NOT NULL,
              intent_type TEXT NOT NULL,
              payload_digest TEXT NOT NULL,
              provider_id TEXT NOT NULL,
              provider_generation INTEGER NOT NULL,
              predecessor_position INTEGER NOT NULL,
              position INTEGER NOT NULL,
              request_id TEXT NOT NULL,
              status TEXT NOT NULL,
              receipt_binding TEXT
            );
            CREATE UNIQUE INDEX legacy_intent_id_binary
              ON shared_anchor_intents(intent_id COLLATE BINARY);
            CREATE UNIQUE INDEX legacy_position_binary
              ON shared_anchor_intents(position);
            CREATE UNIQUE INDEX legacy_request_id_binary
              ON shared_anchor_intents(request_id COLLATE BINARY);
            INSERT INTO shared_anchor_intents VALUES(
              'Alpha','component','migration',
              '0000000000000000000000000000000000000000000000000000000000000000',
              'provider',1,0,1,'request','PREPARED',NULL
            );
            """
        )

        # The current adoption identity check accepts the BINARY identity index.
        assert ("intent_id",) in _unique_key_sets(q, "shared_anchor_intents")

        # But supported runtime predicates such as `WHERE intent_id=?` inherit the
        # legacy column's NOCASE collation and therefore alias a distinct identity.
        assert q.execute(
            "SELECT intent_id FROM shared_anchor_intents WHERE intent_id=?",
            ("alpha",),
        ).fetchone() == ("Alpha",)

        # Explicit byte identity does not alias the two values.
        assert q.execute(
            "SELECT intent_id FROM shared_anchor_intents "
            "WHERE intent_id COLLATE BINARY=?",
            ("alpha",),
        ).fetchone() is None
    finally:
        q.close()
