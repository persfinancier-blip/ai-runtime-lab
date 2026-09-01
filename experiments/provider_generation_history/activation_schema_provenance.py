from __future__ import annotations

import sqlite3

from experiments.anchor_attestation.protocol import AttestedCatchup
from experiments.provider_generation_history.protocol import (
    CurrentGenerationRequired,
    HistoricalVerificationError,
)
from experiments.provider_generation_history.supported import (
    CoordinatorOnlyProviderHistory,
    SupportedHistoricalSharedAnchorLedger,
    _ACTIVATION_TABLE_NAME,
    _ACTIVATION_TABLE_SQL,
    _ACTIVATION_TRIGGER_NAME,
    _ACTIVATION_TRIGGER_SQL,
    _normalized_sql,
)
from experiments.shared_anchor_intent_ledger.protocol import (
    Intent,
    IntentConflict,
    PendingIntent,
)


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
        ledger_table = q.execute(
            "SELECT type FROM sqlite_master WHERE name='shared_anchor_intents'"
        ).fetchone()
        if ledger_table is None:
            raise HistoricalVerificationError(
                "activation schema migration requires an existing shared anchor ledger"
            )
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

        if marker in {"PREPARED", "CONFIRMED"}:
            raise HistoricalVerificationError(
                "activation schema provenance exists but activation DDL is missing or mismatched"
            )
        raise HistoricalVerificationError(
            "activation schema is partially installed or definition-mismatched"
        )
    finally:
        q.close()


def _reservation_surface(path, attested, bootstrap):
    """Build inherited reservation primitives without initializing durable history."""
    if type(attested) is not AttestedCatchup:
        raise TypeError("exact LAB-036 AttestedCatchup required")
    bootstrap.validate()
    ledger = object.__new__(SupportedHistoricalSharedAnchorLedger)
    ledger.path = str(path)
    ledger.attested = attested

    history = object.__new__(CoordinatorOnlyProviderHistory)
    history.path = str(path)
    history.bootstrap = bootstrap
    ledger.provider_history = history
    return ledger


def _verify_confirmation_authority(ledger, attested):
    """Read-only full-history/runtime verification before external marker reauthentication."""
    q = ledger._con()
    try:
        q.execute("BEGIN")
        durable = ledger.provider_history._verify_durable_locked(q)
        runtime = ledger._descriptor_from_attested(attested)
        if runtime.generation_id != durable.generation_id:
            raise CurrentGenerationRequired(
                "runtime provider is stale relative to durable history"
            )
        q.commit()
        return durable
    except:
        if q.in_transaction:
            q.rollback()
        raise
    finally:
        q.close()


def _verify_confirmation_activation_integrity(ledger):
    """Reject malformed LAB-090 activation history before provenance can mutate receipts."""
    return ledger._verify_activation_records()


def _install_and_reserve_prepared(path, attested, bootstrap):
    """Commit exact activation DDL and its deterministic PREPARED marker atomically."""
    intent = _completion_intent()
    intent.validate()
    ledger = _reservation_surface(path, attested, bootstrap)
    q = ledger._con()
    try:
        q.execute("BEGIN IMMEDIATE")

        ledger_table = q.execute(
            "SELECT type FROM sqlite_master WHERE name='shared_anchor_intents'"
        ).fetchone()
        if ledger_table is None or ledger_table[0] != "table":
            raise HistoricalVerificationError("shared anchor intent ledger relation mismatch")

        table_absent, trigger_absent, table_exact, trigger_exact = _schema_object_state(q)
        marker = _marker_state(q)

        durable = ledger.provider_history._verify_durable_locked(q)
        runtime = ledger._descriptor_from_attested(attested)
        if runtime.generation_id != durable.generation_id:
            raise CurrentGenerationRequired(
                "runtime provider is stale relative to durable history"
            )

        if marker == "CONFIRMED":
            if not (table_exact and trigger_exact):
                raise HistoricalVerificationError(
                    "confirmed activation schema provenance has missing or mismatched DDL"
                )
            q.commit()
            return ledger.entry(intent.intent_id)

        if marker == "PREPARED":
            if not (table_exact and trigger_exact):
                raise HistoricalVerificationError(
                    "prepared activation schema provenance has missing or mismatched DDL"
                )
            q.commit()
            return ledger.entry(intent.intent_id)

        if not (
            (table_absent and trigger_absent)
            or (table_exact and trigger_exact)
        ):
            raise HistoricalVerificationError(
                "activation schema is partially installed or definition-mismatched"
            )

        pending = q.execute(
            "SELECT COUNT(*) FROM shared_anchor_intents WHERE status='PREPARED'"
        ).fetchone()[0]
        if pending:
            raise PendingIntent("another anchor intent is unresolved")

        if table_absent and trigger_absent:
            q.execute(_ACTIVATION_TABLE_SQL)
            q.execute(_ACTIVATION_TRIGGER_SQL)

        table_absent, trigger_absent, table_exact, trigger_exact = _schema_object_state(q)
        if table_absent or trigger_absent or not (table_exact and trigger_exact):
            raise HistoricalVerificationError(
                "activation schema did not reach the exact migration definition"
            )

        predecessor = q.execute(
            "SELECT reserved_position FROM shared_anchor_meta WHERE singleton=1"
        ).fetchone()[0]
        position = predecessor + 1
        request_id = ledger._request_id(
            position,
            intent.intent_id,
            intent.component_id,
            intent.intent_type,
            intent.payload_digest,
        )
        q.execute(
            "INSERT INTO shared_anchor_intents VALUES(?,?,?,?,?,?,?,?,?,'PREPARED',NULL)",
            (
                intent.intent_id,
                intent.component_id,
                intent.intent_type,
                intent.payload_digest,
                durable.provider_id,
                durable.generation,
                predecessor,
                position,
                request_id,
            ),
        )
        changed = q.execute(
            "UPDATE shared_anchor_meta SET reserved_position=? WHERE singleton=1 AND reserved_position=?",
            (position, predecessor),
        ).rowcount
        if changed != 1:
            raise IntentConflict("shared anchor tail changed during activation schema migration")

        if _marker_state(q) != "PREPARED":
            raise HistoricalVerificationError("activation schema PREPARED marker was not reserved")
        table_absent, trigger_absent, table_exact, trigger_exact = _schema_object_state(q)
        if table_absent or trigger_absent or not (table_exact and trigger_exact):
            raise HistoricalVerificationError("activation schema changed before migration commit")

        q.commit()
        return ledger.entry(intent.intent_id)
    except:
        if q.in_transaction:
            q.rollback()
        raise
    finally:
        q.close()


class ProvenancedHistoricalSharedAnchorLedger(SupportedHistoricalSharedAnchorLedger):
    """LAB-092 surface: explicit migration with atomic DDL+PREPARED provenance."""

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
        # Ordinary startup is read-only with respect to migration state. In particular,
        # do not call execute() on a legacy/unmarked database because reserve() would
        # create the migration marker. Only an already COMPLETE local state proceeds
        # to full read-only authority and activation-integrity verification, then
        # external re-authentication, before LAB-090 recovery side effects.
        state = _classify(path)
        if state in {"LEGACY_ABSENT", "DDL_INSTALLED_UNMARKED", "DDL_INSTALLED_PREPARED"}:
            raise ActivationSchemaMigrationRequired(
                "activation schema requires explicit migrate_activation_schema_v1()"
            )
        if state != "COMPLETE":
            raise HistoricalVerificationError("invalid activation schema provenance state")

        confirmation = _reservation_surface(path, attested, bootstrap)
        _verify_confirmation_authority(confirmation, attested)
        _verify_confirmation_activation_integrity(confirmation)
        marker = confirmation.execute(_completion_intent())
        if marker.status != "CONFIRMED":
            raise HistoricalVerificationError("activation schema migration marker is not confirmed")

        super().__init__(path, attested, bootstrap)

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

        _install_and_reserve_prepared(path, attested, bootstrap)
        confirmation = _reservation_surface(path, attested, bootstrap)
        _verify_confirmation_authority(confirmation, attested)
        _verify_confirmation_activation_integrity(confirmation)
        marker = confirmation.execute(_completion_intent())
        if marker.status != "CONFIRMED":
            raise HistoricalVerificationError("activation schema completion marker was not confirmed")
        return cls(path, attested, bootstrap)

    def verify_activation_schema_provenance(self):
        if _classify(self.path) != "COMPLETE":
            raise HistoricalVerificationError("activation schema provenance is incomplete")
        _verify_confirmation_authority(self, self.attested)
        _verify_confirmation_activation_integrity(self)
        marker = self.execute(_completion_intent())
        if marker.status != "CONFIRMED":
            raise HistoricalVerificationError("activation schema completion marker is not confirmed")
        return True
