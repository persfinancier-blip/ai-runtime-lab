from __future__ import annotations

import sqlite3

from experiments.provider_generation_history.activation_schema import (
    ACTIVATION_TABLE_NAME,
    ACTIVATION_TABLE_SQL,
    ACTIVATION_TRIGGER_NAME,
    ACTIVATION_TRIGGER_SQL,
    normalized_sql,
)
from experiments.provider_generation_history.protocol import HistoricalVerificationError
from experiments.shared_anchor_intent_ledger.protocol import Intent


MIGRATION_COMPONENT = "provider-generation-activation-schema"
MIGRATION_INTENT_ID = "migration:provider-generation-activation-schema:v1"
MIGRATION_PAYLOAD = {
    "schema": "provider-generation-activation",
    "version": 1,
}


class ActivationSchemaMigrationRequired(HistoricalVerificationError):
    pass


def completion_intent() -> Intent:
    return Intent(
        MIGRATION_INTENT_ID,
        MIGRATION_COMPONENT,
        "migration",
        dict(MIGRATION_PAYLOAD),
    )


def _schema_object_state_locked(q: sqlite3.Connection):
    table = q.execute(
        "SELECT type,sql FROM sqlite_master WHERE name=?",
        (ACTIVATION_TABLE_NAME,),
    ).fetchone()
    trigger = q.execute(
        "SELECT type,sql FROM sqlite_master WHERE name=?",
        (ACTIVATION_TRIGGER_NAME,),
    ).fetchone()

    table_absent = table is None
    trigger_absent = trigger is None
    table_exact = (
        table is not None
        and table[0] == "table"
        and table[1] is not None
        and normalized_sql(table[1]) == normalized_sql(ACTIVATION_TABLE_SQL)
    )
    trigger_exact = (
        trigger is not None
        and trigger[0] == "trigger"
        and trigger[1] is not None
        and normalized_sql(trigger[1]) == normalized_sql(ACTIVATION_TRIGGER_SQL)
    )
    return table_absent, trigger_absent, table_exact, trigger_exact


def _marker_state_locked(q: sqlite3.Connection) -> str:
    row = q.execute(
        "SELECT component_id,intent_type,payload_digest,status "
        "FROM shared_anchor_intents WHERE intent_id=?",
        (MIGRATION_INTENT_ID,),
    ).fetchone()
    if row is None:
        return "ABSENT"

    expected = completion_intent()
    if (
        row[0] != expected.component_id
        or row[1] != expected.intent_type
        or row[2] != expected.payload_digest
        or row[3] not in {"PREPARED", "CONFIRMED"}
    ):
        raise HistoricalVerificationError(
            "activation schema migration marker mismatch"
        )
    return row[3]


def classify_activation_schema_provenance_locked(q: sqlite3.Connection) -> str:
    """Classify activation schema provenance through the caller's locked connection.

    This function deliberately never opens, commits, rolls back, or closes a SQLite
    connection. The caller owns transaction scope so classification can be composed
    atomically with receipt verification/persistence.
    """
    ledger_table = q.execute(
        "SELECT type FROM sqlite_master WHERE name='shared_anchor_intents'"
    ).fetchone()
    if ledger_table is None:
        raise HistoricalVerificationError(
            "activation schema migration requires an existing shared anchor ledger"
        )
    if ledger_table[0] != "table":
        raise HistoricalVerificationError(
            "shared anchor intent ledger relation mismatch"
        )

    table_absent, trigger_absent, table_exact, trigger_exact = (
        _schema_object_state_locked(q)
    )
    marker = _marker_state_locked(q)

    if table_absent and trigger_absent and marker == "ABSENT":
        return "LEGACY_ABSENT"
    if table_exact and trigger_exact and marker == "ABSENT":
        return "DDL_INSTALLED_UNMARKED"
    if table_exact and trigger_exact and marker == "PREPARED":
        return "DDL_INSTALLED_PREPARED"
    if table_exact and trigger_exact and marker == "CONFIRMED":
        return "COMPLETE"

    if marker in {"PREPARED", "CONFIRMED"}:
        raise HistoricalVerificationError(
            "activation schema provenance exists but activation DDL is missing or mismatched"
        )
    raise HistoricalVerificationError(
        "activation schema is partially installed or definition-mismatched"
    )


def require_complete_activation_schema_provenance_locked(
    q: sqlite3.Connection,
) -> None:
    if classify_activation_schema_provenance_locked(q) != "COMPLETE":
        raise HistoricalVerificationError(
            "activation schema provenance is incomplete"
        )


class ActivationSchemaProvenanceReceiptGuardMixin:
    """LAB-092 receipt guard with no provider-history strategy authority.

    Compose this mixin before SupportedHistoricalSharedAnchorLedger. The exact
    connection supplied by the ledger-owned BEGIN IMMEDIATE receipt transaction is
    used for provenance classification; no second connection and no history strategy
    replacement is permitted here.
    """

    def _guard_receipt_persistence_locked(self, q):
        require_complete_activation_schema_provenance_locked(q)
        return super()._guard_receipt_persistence_locked(q)
