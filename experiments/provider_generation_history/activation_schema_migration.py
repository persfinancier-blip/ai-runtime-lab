from __future__ import annotations

"""Explicit LAB-092 activation-schema migration writer.

This module is intentionally opt-in. It installs only the immutable LAB-090 DDL
and reserves the deterministic LAB-092 PREPARED marker in one BEGIN IMMEDIATE.
It does not perform activation recovery/fencing and never replaces the ledger's
construction-bound private provider-history strategy.
"""

from experiments.anchor_attestation.protocol import AttestedCatchup
from experiments.provider_generation_history.activation_schema import (
    ACTIVATION_TABLE_SQL,
    ACTIVATION_TRIGGER_SQL,
)
from experiments.provider_generation_history.activation_schema_provenance import (
    MIGRATION_INTENT_ID,
    _marker_state_locked,
    _schema_object_state_locked,
    completion_intent,
)
from experiments.provider_generation_history.protocol import (
    CurrentGenerationRequired,
    GenerationDescriptor,
    HistoricalVerificationError,
)
from experiments.provider_generation_history.supported import (
    CoordinatorOnlyProviderHistory,
    SupportedHistoricalSharedAnchorLedger,
)
from experiments.shared_anchor_intent_ledger.protocol import IntentConflict, PendingIntent


def _migration_reservation_surface(path, attested, bootstrap: GenerationDescriptor):
    """Construct only the authority needed for the locked migration reservation."""
    if type(attested) is not AttestedCatchup:
        raise TypeError("exact LAB-036 AttestedCatchup required")
    bootstrap.validate()

    history = object.__new__(CoordinatorOnlyProviderHistory)
    history.path = path
    history.bootstrap = bootstrap

    ledger = object.__new__(SupportedHistoricalSharedAnchorLedger)
    ledger.path = path
    ledger.attested = attested
    ledger.provider_history = history
    return ledger


def _reject_unrelated_prepared_locked(q):
    unrelated = q.execute(
        "SELECT COUNT(*) FROM shared_anchor_intents "
        "WHERE status='PREPARED' AND intent_id<>?",
        (MIGRATION_INTENT_ID,),
    ).fetchone()[0]
    if unrelated:
        raise PendingIntent("another anchor intent is unresolved")


def install_and_reserve_activation_schema_v1(
    path, attested: AttestedCatchup, bootstrap: GenerationDescriptor
):
    """Atomically install exact activation DDL and reserve its PREPARED marker.

    Recoverable inputs are exact legacy absence, exact DDL with no marker, and exact
    DDL with the deterministic PREPARED marker. Partial/mismatched DDL, a corrupt
    marker, another PREPARED intent, or a stale runtime generation fail closed.
    """
    intent = completion_intent()
    intent.validate()
    ledger = _migration_reservation_surface(path, attested, bootstrap)
    q = ledger._con()
    try:
        q.execute("BEGIN IMMEDIATE")

        ledger_table = q.execute(
            "SELECT type FROM sqlite_master WHERE name='shared_anchor_intents'"
        ).fetchone()
        if ledger_table is None or ledger_table[0] != "table":
            raise HistoricalVerificationError(
                "activation schema migration requires an existing shared anchor ledger"
            )
        meta = q.execute(
            "SELECT reserved_position FROM shared_anchor_meta WHERE singleton=1"
        ).fetchone()
        if meta is None:
            raise HistoricalVerificationError("shared anchor metadata singleton missing")

        table_absent, trigger_absent, table_exact, trigger_exact = (
            _schema_object_state_locked(q)
        )
        marker = _marker_state_locked(q)

        durable = ledger._history()._verify_durable_locked(q)
        runtime = ledger._descriptor_from_attested(attested)
        if runtime.generation_id != durable.generation_id:
            raise CurrentGenerationRequired(
                "runtime provider is stale relative to durable history"
            )

        _reject_unrelated_prepared_locked(q)

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

        if table_absent and trigger_absent:
            q.execute(ACTIVATION_TABLE_SQL)
            q.execute(ACTIVATION_TRIGGER_SQL)

        table_absent, trigger_absent, table_exact, trigger_exact = (
            _schema_object_state_locked(q)
        )
        if table_absent or trigger_absent or not (table_exact and trigger_exact):
            raise HistoricalVerificationError(
                "activation schema did not reach the exact migration definition"
            )

        predecessor = meta[0]
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
            "UPDATE shared_anchor_meta SET reserved_position=? "
            "WHERE singleton=1 AND reserved_position=?",
            (position, predecessor),
        ).rowcount
        if changed != 1:
            raise IntentConflict(
                "shared anchor tail changed during activation schema migration"
            )

        if _marker_state_locked(q) != "PREPARED":
            raise HistoricalVerificationError(
                "activation schema PREPARED marker was not reserved"
            )
        table_absent, trigger_absent, table_exact, trigger_exact = (
            _schema_object_state_locked(q)
        )
        if table_absent or trigger_absent or not (table_exact and trigger_exact):
            raise HistoricalVerificationError(
                "activation schema changed before migration commit"
            )

        q.commit()
        return ledger.entry(intent.intent_id)
    except:
        if q.in_transaction:
            q.rollback()
        raise
    finally:
        q.close()
