"""Explicit LAB-095 logical database identity installation/recovery.

The migration establishes only local custody plus one ordinary shared-anchor
migration intent. External authority remains owned by SharedAnchorLedger.
"""
from __future__ import annotations

import secrets
import sqlite3
from pathlib import Path

from experiments.shared_anchor_intent_ledger.protocol import Intent, SharedAnchorLedger

from .database_identity import (
    DatabaseIdentityError,
    IDENTITY_COMPONENT,
    IDENTITY_INTENT_ID,
    IdentityCustodyState,
    _CUSTODY_TABLE,
    _load_custody,
    confirmed_identity_digest,
    identity_payload,
    identity_payload_digest,
    install_custody_schema,
)


class DatabaseIdentityMigrationError(DatabaseIdentityError):
    pass


def _canonical_path(value: str | Path) -> str:
    return str(Path(value).expanduser().resolve(strict=False))


def _require_same_database(ledger, history) -> str:
    ledger_path = _canonical_path(ledger.path)
    history_path = _canonical_path(history.path)
    if ledger_path != history_path:
        raise DatabaseIdentityMigrationError("ledger/history database paths diverge")
    return ledger_path


def _connect(path: str) -> sqlite3.Connection:
    q = sqlite3.connect(path, timeout=5, isolation_level=None)
    q.execute("PRAGMA busy_timeout=5000")
    return q


def _intent_from_custody(custody) -> Intent:
    return Intent(
        IDENTITY_INTENT_ID,
        IDENTITY_COMPONENT,
        "migration",
        identity_payload(
            nonce_hex=custody.nonce_hex,
            bootstrap_generation_id=custody.bootstrap_generation_id,
        ),
    )


def _classify_locked(q: sqlite3.Connection) -> IdentityCustodyState:
    relation = q.execute(
        "SELECT type FROM sqlite_master WHERE name=?", (_CUSTODY_TABLE,)
    ).fetchone()
    if relation is None:
        return IdentityCustodyState.ABSENT
    if relation != ("table",):
        return IdentityCustodyState.CORRUPT
    rows = q.execute(f"SELECT COUNT(*) FROM {_CUSTODY_TABLE}").fetchone()[0]
    if rows == 0:
        return IdentityCustodyState.ABSENT
    if rows != 1:
        return IdentityCustodyState.CORRUPT
    custody = _load_custody(q)
    if custody is None:
        return IdentityCustodyState.CORRUPT
    intent = q.execute(
        """SELECT component_id,intent_type,payload_digest,provider_id,
                  provider_generation,position,request_id,status,receipt_binding
           FROM shared_anchor_intents WHERE intent_id=?""",
        (IDENTITY_INTENT_ID,),
    ).fetchone()
    if intent is None:
        return IdentityCustodyState.CORRUPT
    component, intent_type, payload_digest, provider_id, generation, position, request_id, status, receipt = intent
    if (
        component != IDENTITY_COMPONENT
        or intent_type != "migration"
        or payload_digest != custody.payload_digest
        or request_id != custody.intent_request_id
    ):
        return IdentityCustodyState.CORRUPT
    if status == "PREPARED":
        if (
            custody.status != "PREPARED"
            or receipt is not None
            or any(
                value is not None
                for value in (
                    custody.provider_id,
                    custody.provider_generation,
                    custody.position,
                    custody.receipt_binding,
                    custody.logical_database_identity_digest,
                )
            )
        ):
            return IdentityCustodyState.CORRUPT
        return IdentityCustodyState.PREPARED
    if status != "CONFIRMED" or receipt is None:
        return IdentityCustodyState.CORRUPT
    if custody.status == "PREPARED":
        return IdentityCustodyState.CONFIRMED_NEEDS_FINALIZE
    if custody.status != "CONFIRMED":
        return IdentityCustodyState.CORRUPT
    expected = confirmed_identity_digest(
        payload_digest=custody.payload_digest,
        provider_id=provider_id,
        provider_generation=generation,
        position=position,
        request_id=request_id,
        receipt_binding=receipt,
    )
    if (
        custody.provider_id != provider_id
        or custody.provider_generation != generation
        or custody.position != position
        or custody.receipt_binding != receipt
        or custody.logical_database_identity_digest != expected
    ):
        return IdentityCustodyState.CORRUPT
    return IdentityCustodyState.COMPLETE


def prepare_database_identity(ledger, history) -> IdentityCustodyState:
    """Atomically create custody and the one PREPARED identity reservation.

    Nonce generation occurs only while holding BEGIN IMMEDIATE after re-reading
    the persisted state. Existing PREPARED/confirmed work is never replaced.
    """
    path = _require_same_database(ledger, history)
    history.verify_durable()
    current = history.current()
    provider_id, generation = ledger._provider()
    if (current.provider_id, current.generation) != (provider_id, generation):
        raise DatabaseIdentityMigrationError("ledger/history provider generation mismatch")

    q = _connect(path)
    try:
        q.execute("BEGIN IMMEDIATE")
        install_custody_schema(q)
        head = q.execute(
            "SELECT generation_id,generation FROM provider_generation_head WHERE singleton=1"
        ).fetchone()
        bootstrap = q.execute(
            "SELECT generation_id FROM provider_generations ORDER BY generation LIMIT 1"
        ).fetchone()
        if head is None or bootstrap is None:
            raise DatabaseIdentityMigrationError("provider history metadata missing")
        if bootstrap[0] != history.bootstrap.generation_id:
            raise DatabaseIdentityMigrationError("provider history bootstrap changed")
        if head[1] != generation:
            raise DatabaseIdentityMigrationError("provider history generation changed")
        head_provider = q.execute(
            "SELECT provider_id FROM provider_generations WHERE generation_id=?",
            (head[0],),
        ).fetchone()
        if head_provider != (provider_id,):
            raise DatabaseIdentityMigrationError("provider history head changed")
        state = _classify_locked(q)
        if state is not IdentityCustodyState.ABSENT:
            if state is IdentityCustodyState.CORRUPT:
                raise DatabaseIdentityMigrationError("identity custody is corrupt")
            q.commit()
            return state

        pending = q.execute(
            "SELECT COUNT(*) FROM shared_anchor_intents WHERE status='PREPARED'"
        ).fetchone()[0]
        if pending:
            raise DatabaseIdentityMigrationError(
                "another shared-anchor intent is unresolved"
            )

        nonce_hex = secrets.token_bytes(32).hex()
        bootstrap_generation_id = history.bootstrap.generation_id
        payload_digest = identity_payload_digest(
            nonce_hex=nonce_hex,
            bootstrap_generation_id=bootstrap_generation_id,
        )
        predecessor_row = q.execute(
            "SELECT reserved_position FROM shared_anchor_meta WHERE singleton=1"
        ).fetchone()
        if predecessor_row is None:
            raise DatabaseIdentityMigrationError("shared anchor metadata missing")
        predecessor = predecessor_row[0]
        position = predecessor + 1
        request_id = SharedAnchorLedger._request_id(
            position,
            IDENTITY_INTENT_ID,
            IDENTITY_COMPONENT,
            "migration",
            payload_digest,
        )
        q.execute(
            """INSERT INTO shared_anchor_intents
               VALUES(?,?,?,?,?,?,?,?,?,'PREPARED',NULL)""",
            (
                IDENTITY_INTENT_ID,
                IDENTITY_COMPONENT,
                "migration",
                payload_digest,
                provider_id,
                generation,
                predecessor,
                position,
                request_id,
            ),
        )
        updated = q.execute(
            """UPDATE shared_anchor_meta SET reserved_position=?
               WHERE singleton=1 AND reserved_position=?""",
            (position, predecessor),
        ).rowcount
        if updated != 1:
            raise DatabaseIdentityMigrationError("shared anchor tail changed")
        q.execute(
            f"""INSERT INTO {_CUSTODY_TABLE}
                VALUES(1,'PREPARED',?,?,?,?,NULL,NULL,NULL,NULL,NULL)""",
            (
                nonce_hex,
                bootstrap_generation_id,
                payload_digest,
                request_id,
            ),
        )
        q.commit()
        return IdentityCustodyState.PREPARED
    except Exception:
        if q.in_transaction:
            q.rollback()
        raise
    finally:
        q.close()


def _finalize_confirmed(path: str) -> str:
    q = _connect(path)
    try:
        q.execute("BEGIN IMMEDIATE")
        install_custody_schema(q)
        state = _classify_locked(q)
        if state is IdentityCustodyState.COMPLETE:
            custody = _load_custody(q)
            q.commit()
            return custody.logical_database_identity_digest
        if state is not IdentityCustodyState.CONFIRMED_NEEDS_FINALIZE:
            raise DatabaseIdentityMigrationError(
                f"cannot finalize identity from state {state.value}"
            )
        custody = _load_custody(q)
        row = q.execute(
            """SELECT provider_id,provider_generation,position,request_id,receipt_binding
               FROM shared_anchor_intents WHERE intent_id=? AND status='CONFIRMED'""",
            (IDENTITY_INTENT_ID,),
        ).fetchone()
        if row is None:
            raise DatabaseIdentityMigrationError("confirmed identity intent missing")
        provider_id, generation, position, request_id, receipt = row
        digest = confirmed_identity_digest(
            payload_digest=custody.payload_digest,
            provider_id=provider_id,
            provider_generation=generation,
            position=position,
            request_id=request_id,
            receipt_binding=receipt,
        )
        updated = q.execute(
            f"""UPDATE {_CUSTODY_TABLE}
                SET status='CONFIRMED',provider_id=?,provider_generation=?,
                    position=?,receipt_binding=?,logical_database_identity_digest=?
                WHERE singleton=1 AND status='PREPARED'
                  AND provider_id IS NULL AND provider_generation IS NULL
                  AND position IS NULL AND receipt_binding IS NULL
                  AND logical_database_identity_digest IS NULL""",
            (provider_id, generation, position, receipt, digest),
        ).rowcount
        if updated != 1:
            raise DatabaseIdentityMigrationError("identity custody changed before finalize")
        q.commit()
        return digest
    except Exception:
        if q.in_transaction:
            q.rollback()
        raise
    finally:
        q.close()


def migrate_database_identity(ledger, history, *, timeout_after_commit: bool = False) -> str:
    """Prepare, reconcile/execute the same request, then locally finalize.

    A retry after UNKNOWN or process crash reconstructs the Intent from persisted
    custody. SharedAnchorLedger.execute() therefore reconciles the same durable
    request and reauthenticates already-CONFIRMED evidence before finalization.
    """
    path = _require_same_database(ledger, history)
    state = prepare_database_identity(ledger, history)
    if state is IdentityCustodyState.COMPLETE:
        q = _connect(path)
        try:
            custody = _load_custody(q)
            return custody.logical_database_identity_digest
        finally:
            q.close()

    q = _connect(path)
    try:
        custody = _load_custody(q)
        if custody is None:
            raise DatabaseIdentityMigrationError("identity custody disappeared")
        intent = _intent_from_custody(custody)
    finally:
        q.close()

    ledger.execute(intent, timeout_after_commit=timeout_after_commit)
    return _finalize_confirmed(path)
