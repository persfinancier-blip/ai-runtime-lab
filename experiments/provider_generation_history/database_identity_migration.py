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
        orphan_intent = q.execute(
            "SELECT 1 FROM shared_anchor_intents WHERE intent_id=?",
            (IDENTITY_INTENT_ID,),
        ).fetchone()
        return (
            IdentityCustodyState.CORRUPT
            if orphan_intent is not None
            else IdentityCustodyState.ABSENT
        )
    if rows != 1:
        return IdentityCustodyState.CORRUPT
    custody = _load_custody(q)
    if custody is None:
        return IdentityCustodyState.CORRUPT
    try:
        expected_payload_digest = identity_payload_digest(
            nonce_hex=custody.nonce_hex,
            bootstrap_generation_id=custody.bootstrap_generation_id,
        )
    except DatabaseIdentityError:
        return IdentityCustodyState.CORRUPT
    if custody.payload_digest != expected_payload_digest:
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
    try:
        expected = confirmed_identity_digest(
            payload_digest=custody.payload_digest,
            provider_id=provider_id,
            provider_generation=generation,
            position=position,
            request_id=request_id,
            receipt_binding=receipt,
        )
    except DatabaseIdentityError:
        return IdentityCustodyState.CORRUPT
    if (
        custody.provider_id != provider_id
        or custody.provider_generation != generation
        or custody.position != position
        or custody.receipt_binding != receipt
        or custody.logical_database_identity_digest != expected
    ):
        return IdentityCustodyState.CORRUPT
    return IdentityCustodyState.COMPLETE


def _authority_tuple(value):
    return (value.provider_id, value.generation)


def prepare_database_identity(ledger, history) -> IdentityCustodyState:
    """Atomically create custody and the one PREPARED identity reservation.

    The full provider-history verifier runs on the same SQLite connection while
    BEGIN IMMEDIATE is held, before custody schema creation, nonce generation, or
    shared-anchor mutation. Existing PREPARED/confirmed work is never replaced.
    """
    path = _require_same_database(ledger, history)
    history.verify_durable()
    current = history.current()
    runtime_authority = ledger._provider()
    if _authority_tuple(current) != runtime_authority:
        raise DatabaseIdentityMigrationError("ledger/history provider generation mismatch")

    q = _connect(path)
    try:
        q.execute("BEGIN IMMEDIATE")

        # Security boundary: re-run the complete durable-history verifier while
        # holding the same writer lock used for migration. Do this before any
        # custody DDL/DML so corrupt history leaves zero migration mutation.
        locked_current = history._verify_durable_locked(q)
        if _authority_tuple(locked_current) != _authority_tuple(current):
            raise DatabaseIdentityMigrationError("provider history changed under migration lock")
        if _authority_tuple(locked_current) != runtime_authority:
            raise DatabaseIdentityMigrationError("runtime provider changed under migration lock")

        install_custody_schema(q)
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
                locked_current.provider_id,
                locked_current.generation,
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


def _authenticated_entry_tuple(entry):
    try:
        return (
            entry.intent_id,
            entry.component_id,
            entry.intent_type,
            entry.payload_digest,
            entry.provider_id,
            entry.provider_generation,
            entry.predecessor_position,
            entry.position,
            entry.request_id,
            entry.status,
            entry.receipt_binding,
        )
    except AttributeError as exc:
        raise DatabaseIdentityMigrationError(
            "ledger execute did not return an authenticated confirmed entry"
        ) from exc


def _finalize_confirmed(path: str, authenticated_entry) -> str:
    authenticated = _authenticated_entry_tuple(authenticated_entry)
    if authenticated[9] != "CONFIRMED":
        raise DatabaseIdentityMigrationError(
            "ledger execute did not return an authenticated confirmed entry"
        )

    q = _connect(path)
    try:
        q.execute("BEGIN IMMEDIATE")
        install_custody_schema(q)
        state = _classify_locked(q)
        if state not in {
            IdentityCustodyState.CONFIRMED_NEEDS_FINALIZE,
            IdentityCustodyState.COMPLETE,
        }:
            raise DatabaseIdentityMigrationError(
                f"cannot finalize identity from state {state.value}"
            )
        custody = _load_custody(q)
        row = q.execute(
            """SELECT intent_id,component_id,intent_type,payload_digest,provider_id,
                      provider_generation,predecessor_position,position,request_id,
                      status,receipt_binding
               FROM shared_anchor_intents WHERE intent_id=?""",
            (IDENTITY_INTENT_ID,),
        ).fetchone()
        if row is None:
            raise DatabaseIdentityMigrationError("confirmed identity intent missing")
        if row != authenticated:
            raise DatabaseIdentityMigrationError(
                "confirmed identity intent changed after authentication"
            )
        (
            intent_id,
            component_id,
            intent_type,
            payload_digest,
            provider_id,
            generation,
            predecessor_position,
            position,
            request_id,
            status,
            receipt,
        ) = row
        if (
            intent_id != IDENTITY_INTENT_ID
            or component_id != IDENTITY_COMPONENT
            or intent_type != "migration"
            or payload_digest != custody.payload_digest
            or request_id != custody.intent_request_id
            or status != "CONFIRMED"
        ):
            raise DatabaseIdentityMigrationError(
                "confirmed identity intent changed after authentication"
            )
        if state is IdentityCustodyState.COMPLETE:
            q.commit()
            return custody.logical_database_identity_digest
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
    COMPLETE local custody is also reauthenticated; it is not external authority
    by itself. The exact CONFIRMED entry returned by that authenticated operation
    must remain byte-for-byte authoritative through the final local writer
    transaction.
    """
    path = _require_same_database(ledger, history)
    prepare_database_identity(ledger, history)

    q = _connect(path)
    try:
        custody = _load_custody(q)
        if custody is None:
            raise DatabaseIdentityMigrationError("identity custody disappeared")
        intent = _intent_from_custody(custody)
    finally:
        q.close()

    authenticated_entry = ledger.execute(
        intent, timeout_after_commit=timeout_after_commit
    )
    return _finalize_confirmed(path, authenticated_entry)
