from __future__ import annotations

import sqlite3

from experiments.provider_generation_history.protocol import HistoricalVerificationError
from experiments.provider_generation_history.supported import (
    SupportedHistoricalSharedAnchorLedger,
    _ACTIVATION_TABLE_NAME,
    _ACTIVATION_TABLE_SQL,
    _ACTIVATION_TRIGGER_NAME,
    _ACTIVATION_TRIGGER_SQL,
    _normalized_sql,
)
from experiments.shared_anchor_intent_ledger.protocol import Intent


_MIGRATION_COMPONENT = "provider-generation-activation-schema"
_MIGRATION_INTENT_ID = "migration:provider-generation-activation-schema:v1"
_MIGRATION_PAYLOAD = {
    "schema": "provider-generation-activation",
    "version": 1,
}


class ActivationSchemaMigrationRequired(HistoricalVerificationError):
    pass


def _completion_intent() -> Intent:
    return Intent(
        _MIGRATION_INTENT_ID,
        _MIGRATION_COMPONENT,
        "migration",
        dict(_MIGRATION_PAYLOAD),
    )


def _schema_object_state(q: sqlite3.Connection):
    table = q.execute(
        "SELECT type,sql FROM sqlite_master WHERE name=?",
        (_ACTIVATION_TABLE_NAME,),
    ).fetchone()
    trigger = q.execute(
        "SELECT type,sql FROM sqlite_master WHERE name=?",
        (_ACTIVATION_TRIGGER_NAME,),
    ).fetchone()

    table_absent = table is None
    trigger_absent = trigger is None
    table_exact = (
        table is not None
        and table[0] == "table"
        and table[1] is not None
        and _normalized_sql(table[1]) == _normalized_sql(_ACTIVATION_TABLE_SQL)
    )
    trigger_exact = (
        trigger is not None
        and trigger[0] == "trigger"
        and trigger[1] is not None
        and _normalized_sql(trigger[1]) == _normalized_sql(_ACTIVATION_TRIGGER_SQL)
    )
    return table_absent, trigger_absent, table_exact, trigger_exact


def _marker_state(q: sqlite3.Connection):
    row = q.execute(
        "SELECT component_id,intent_type,payload_digest,status "
        "FROM shared_anchor_intents WHERE intent_id=?",
        (_MIGRATION_INTENT_ID,),
    ).fetchone()
    if row is None:
        return "ABSENT"
    expected = _completion_intent()
    if (
        row[0] != expected.component_id
        or row[1] != expected.intent_type
        or row[2] != expected.payload_digest
        or row[3] not in {"PREPARED", "CONFIRMED"}
    ):
        raise HistoricalVerificationError("activation schema migration marker mismatch")
    return row[3]


def _classify(path):
    q = sqlite3.connect(str(path), timeout=5, isolation_level=None)
    q.execute("PRAGMA busy_timeout=5000")
    try:
        # Shared-ledger schema must already exist before provenance can be judged.
        ledger_table = q.execute(
            "SELECT type FROM sqlite_master WHERE name='shared_anchor_intents'"
        ).fetchone()
        if ledger_table is None:
            return "LEGACY_ABSENT"
        if ledger_table[0] != "table":
            raise HistoricalVerificationError("shared anchor intent ledger relation mismatch")

        table_absent, trigger_absent, table_exact, trigger_exact = _schema_object_state(q)
        marker = _marker_state(q)

        if table_absent and trigger_absent and marker == "ABSENT":
            return "LEGACY_ABSENT"
        if table_exact and trigger_exact and marker == "ABSENT":
            return "DDL_INSTALLED_UNMARKED"
        if table_exact and trigger_exact and marker == "PREPARED":
            return "DDL_INSTALLED_PREPARED"
        if table_exact and trigger_exact and marker == "CONFIRMED":
            return "COMPLETE"

        # Once a marker exists, missing or changed DDL is post-install corruption/tamper.
        if marker in {"PREPARED", "CONFIRMED"}:
            raise HistoricalVerificationError(
                "activation schema provenance exists but activation DDL is missing or mismatched"
            )
        raise HistoricalVerificationError(
            "activation schema is partially installed or definition-mismatched"
        )
    finally:
        q.close()


class ProvenancedHistoricalSharedAnchorLedger(SupportedHistoricalSharedAnchorLedger):
    """LAB-092 surface: explicit DDL-first migration with authenticated completion provenance."""

    def _init_activation_schema(self):
        state = _classify(self.path)
        if state == "COMPLETE":
            return
        if state in {"LEGACY_ABSENT", "DDL_INSTALLED_UNMARKED", "DDL_INSTALLED_PREPARED"}:
            raise ActivationSchemaMigrationRequired(
                "activation schema requires explicit migrate_activation_schema_v1()"
            )
        raise HistoricalVerificationError("invalid activation schema provenance state")

    def __init__(self, path, attested, bootstrap):
        super().__init__(path, attested, bootstrap)
        # Re-authenticate the CONFIRMED completion intent against the external anchor.
        marker = self.execute(_completion_intent())
        if marker.status != "CONFIRMED":
            raise HistoricalVerificationError("activation schema migration marker is not confirmed")

    @classmethod
    def migrate_activation_schema_v1(cls, path, attested, bootstrap):
        state = _classify(path)
        if state == "COMPLETE":
            return cls(path, attested, bootstrap)
        if state not in {
            "LEGACY_ABSENT",
            "DDL_INSTALLED_UNMARKED",
            "DDL_INSTALLED_PREPARED",
        }:
            raise HistoricalVerificationError("activation schema migration state is not recoverable")

        # DDL-first: inherited LAB-090 installs/verifies table+trigger atomically under
        # BEGIN IMMEDIATE. Only after exact DDL exists do we reserve/confirm the one
        # deterministic authenticated migration completion intent.
        legacy = SupportedHistoricalSharedAnchorLedger(path, attested, bootstrap)
        marker = legacy.execute(_completion_intent())
        if marker.status != "CONFIRMED":
            raise HistoricalVerificationError("activation schema completion marker was not confirmed")
        return cls(path, attested, bootstrap)

    def verify_activation_schema_provenance(self):
        if _classify(self.path) != "COMPLETE":
            raise HistoricalVerificationError("activation schema provenance is incomplete")
        marker = self.execute(_completion_intent())
        if marker.status != "CONFIRMED":
            raise HistoricalVerificationError("activation schema completion marker is not confirmed")
        return True
