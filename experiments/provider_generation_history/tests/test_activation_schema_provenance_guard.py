import sqlite3

import pytest

from experiments.provider_generation_history.activation_schema import (
    ACTIVATION_TABLE_SQL,
    ACTIVATION_TRIGGER_SQL,
)
from experiments.provider_generation_history.activation_schema_provenance import (
    ActivationSchemaProvenanceReceiptGuardMixin,
    MIGRATION_INTENT_ID,
    classify_activation_schema_provenance_locked,
    completion_intent,
)
from experiments.provider_generation_history.protocol import HistoricalVerificationError


LEDGER_DDL = """CREATE TABLE shared_anchor_intents(
  intent_id TEXT PRIMARY KEY,
  component_id TEXT NOT NULL,
  intent_type TEXT NOT NULL,
  payload_digest TEXT NOT NULL,
  status TEXT NOT NULL
)"""


def _connection():
    q = sqlite3.connect(":memory:", isolation_level=None)
    q.execute(LEDGER_DDL)
    return q


def _install_exact_activation_schema(q):
    q.execute(ACTIVATION_TABLE_SQL)
    q.execute(ACTIVATION_TRIGGER_SQL)


def _install_marker(q, status="CONFIRMED", *, payload_digest=None):
    expected = completion_intent()
    q.execute(
        "INSERT INTO shared_anchor_intents VALUES(?,?,?,?,?)",
        (
            MIGRATION_INTENT_ID,
            expected.component_id,
            expected.intent_type,
            payload_digest or expected.payload_digest,
            status,
        ),
    )


def test_complete_classification_uses_supplied_transaction_without_committing_it():
    q = _connection()
    try:
        _install_exact_activation_schema(q)
        _install_marker(q)
        q.execute("BEGIN IMMEDIATE")

        assert classify_activation_schema_provenance_locked(q) == "COMPLETE"
        assert q.in_transaction is True

        q.rollback()
    finally:
        q.close()


def test_confirmed_marker_with_missing_activation_schema_fails_closed():
    q = _connection()
    try:
        _install_marker(q)
        q.execute("BEGIN IMMEDIATE")
        with pytest.raises(
            HistoricalVerificationError,
            match="provenance exists but activation DDL is missing or mismatched",
        ):
            classify_activation_schema_provenance_locked(q)
        assert q.in_transaction is True
        q.rollback()
    finally:
        q.close()


def test_confirmed_marker_with_mismatched_activation_schema_fails_closed():
    q = _connection()
    try:
        q.execute(
            "CREATE TABLE provider_generation_activations(activation_id TEXT PRIMARY KEY)"
        )
        _install_marker(q)
        q.execute("BEGIN IMMEDIATE")
        with pytest.raises(
            HistoricalVerificationError,
            match="provenance exists but activation DDL is missing or mismatched",
        ):
            classify_activation_schema_provenance_locked(q)
        assert q.in_transaction is True
        q.rollback()
    finally:
        q.close()


def test_marker_substitution_fails_closed():
    q = _connection()
    try:
        _install_exact_activation_schema(q)
        _install_marker(q, payload_digest="0" * 64)
        q.execute("BEGIN IMMEDIATE")
        with pytest.raises(
            HistoricalVerificationError,
            match="activation schema migration marker mismatch",
        ):
            classify_activation_schema_provenance_locked(q)
        assert q.in_transaction is True
        q.rollback()
    finally:
        q.close()


def test_receipt_guard_refuses_unmarked_schema_before_downstream_guard():
    q = _connection()
    try:
        _install_exact_activation_schema(q)
        calls = []

        class Downstream:
            def _guard_receipt_persistence_locked(self, supplied_q):
                calls.append(supplied_q)

        class Guarded(ActivationSchemaProvenanceReceiptGuardMixin, Downstream):
            pass

        q.execute("BEGIN IMMEDIATE")
        with pytest.raises(
            HistoricalVerificationError,
            match="activation schema provenance is incomplete",
        ):
            Guarded()._guard_receipt_persistence_locked(q)
        assert calls == []
        assert q.in_transaction is True
        q.rollback()
    finally:
        q.close()


def test_receipt_guard_delegates_with_same_connection_only_after_complete():
    q = _connection()
    try:
        _install_exact_activation_schema(q)
        _install_marker(q)
        calls = []

        class Downstream:
            def _guard_receipt_persistence_locked(self, supplied_q):
                calls.append(supplied_q)
                return "ok"

        class Guarded(ActivationSchemaProvenanceReceiptGuardMixin, Downstream):
            pass

        q.execute("BEGIN IMMEDIATE")
        assert Guarded()._guard_receipt_persistence_locked(q) == "ok"
        assert calls == [q]
        assert q.in_transaction is True
        q.rollback()
    finally:
        q.close()
