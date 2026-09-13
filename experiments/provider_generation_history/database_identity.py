"""LAB-095 logical database/history identity primitives.

This module owns production canonical derivation and the local custody-state
classifier. It intentionally does not create external shared-anchor authority:
installation/reconciliation is a separate explicit migration step.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

IDENTITY_COMPONENT = "provider-history-logical-database"
IDENTITY_INTENT_ID = "migration:logical-database-identity:v1"
IDENTITY_SCHEMA = "provider-history-logical-database"
IDENTITY_VERSION = 1

_CUSTODY_TABLE = "provider_history_database_identity"
_CUSTODY_DDL = """CREATE TABLE IF NOT EXISTS provider_history_database_identity(
  singleton INTEGER PRIMARY KEY CHECK(singleton=1),
  status TEXT NOT NULL CHECK(status IN ('PREPARED','CONFIRMED')),
  nonce_hex TEXT NOT NULL,
  bootstrap_generation_id TEXT NOT NULL,
  payload_digest TEXT NOT NULL,
  intent_request_id TEXT NOT NULL,
  provider_id TEXT,
  provider_generation INTEGER,
  position INTEGER,
  receipt_binding TEXT,
  logical_database_identity_digest TEXT
)"""
_CUSTODY_STORED_DDL = _CUSTODY_DDL.replace(" IF NOT EXISTS", "")


class DatabaseIdentityError(RuntimeError):
    pass


class IdentityCustodyState(str, Enum):
    ABSENT = "ABSENT"
    PREPARED = "PREPARED"
    CONFIRMED_NEEDS_FINALIZE = "CONFIRMED_NEEDS_FINALIZE"
    COMPLETE = "COMPLETE"
    CORRUPT = "CORRUPT"


@dataclass(frozen=True)
class IdentityCustody:
    status: str
    nonce_hex: str
    bootstrap_generation_id: str
    payload_digest: str
    intent_request_id: str
    provider_id: str | None
    provider_generation: int | None
    position: int | None
    receipt_binding: str | None
    logical_database_identity_digest: str | None


def _canon(obj: object) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _sha(obj: object) -> str:
    return hashlib.sha256(_canon(obj)).hexdigest()


def _require_digest(value: str, label: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(c not in "0123456789abcdef" for c in value)
    ):
        raise DatabaseIdentityError(f"{label} must be a lowercase sha256 digest")
    return value


def _require_nonempty(value: str, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise DatabaseIdentityError(f"invalid {label}")
    return value


def identity_payload(*, nonce_hex: str, bootstrap_generation_id: str) -> dict[str, object]:
    _require_digest(nonce_hex, "nonce_hex")
    _require_digest(bootstrap_generation_id, "bootstrap_generation_id")
    return {
        "schema": IDENTITY_SCHEMA,
        "version": IDENTITY_VERSION,
        "nonce_hex": nonce_hex,
        "bootstrap_generation_id": bootstrap_generation_id,
    }


def identity_payload_digest(*, nonce_hex: str, bootstrap_generation_id: str) -> str:
    # SharedAnchorLedger.Intent.payload_digest hashes component/type/payload.
    return _sha(
        {
            "component_id": IDENTITY_COMPONENT,
            "intent_type": "migration",
            "payload": identity_payload(
                nonce_hex=nonce_hex,
                bootstrap_generation_id=bootstrap_generation_id,
            ),
        }
    )


def confirmed_identity_digest(
    *,
    payload_digest: str,
    provider_id: str,
    provider_generation: int,
    position: int,
    request_id: str,
    receipt_binding: str,
) -> str:
    _require_digest(payload_digest, "payload_digest")
    _require_nonempty(provider_id, "provider_id")
    if type(provider_generation) is not int or provider_generation < 1:
        raise DatabaseIdentityError("invalid provider_generation")
    if type(position) is not int or position < 1:
        raise DatabaseIdentityError("invalid position")
    _require_nonempty(request_id, "request_id")
    _require_digest(receipt_binding, "receipt_binding")
    return _sha(
        {
            "domain": "lab095-logical-database-identity-v1",
            "intent_id": IDENTITY_INTENT_ID,
            "component_id": IDENTITY_COMPONENT,
            "intent_type": "migration",
            "payload_digest": payload_digest,
            "provider_id": provider_id,
            "provider_generation": provider_generation,
            "position": position,
            "request_id": request_id,
            "receipt_binding": receipt_binding,
        }
    )


def genesis_parent_chain_link(
    *, logical_database_identity_digest: str, bootstrap_generation_id: str
) -> str:
    _require_digest(
        logical_database_identity_digest, "logical_database_identity_digest"
    )
    _require_digest(bootstrap_generation_id, "bootstrap_generation_id")
    return _sha(
        {
            "domain": "lab095-provider-history-parent-link-v1",
            "logical_database_identity_digest": logical_database_identity_digest,
            "bootstrap_generation_id": bootstrap_generation_id,
        }
    )


def transition_parent_chain_link(
    *,
    logical_database_identity_digest: str,
    parent_chain_link_digest: str,
    provider_id: str,
    old_generation_id: str,
    new_generation_id: str,
    old_mac: str,
    new_mac: str,
) -> str:
    _require_digest(
        logical_database_identity_digest, "logical_database_identity_digest"
    )
    _require_digest(parent_chain_link_digest, "parent_chain_link_digest")
    _require_nonempty(provider_id, "provider_id")
    for value, label in (
        (old_generation_id, "old_generation_id"),
        (new_generation_id, "new_generation_id"),
        (old_mac, "old_mac"),
        (new_mac, "new_mac"),
    ):
        _require_digest(value, label)
    return _sha(
        {
            "domain": "lab095-provider-history-parent-link-v1",
            "logical_database_identity_digest": logical_database_identity_digest,
            "parent_chain_link_digest": parent_chain_link_digest,
            "transition": {
                "provider_id": provider_id,
                "old_generation_id": old_generation_id,
                "new_generation_id": new_generation_id,
                "old_mac": old_mac,
                "new_mac": new_mac,
            },
        }
    )


def install_custody_schema(q: sqlite3.Connection) -> None:
    """Create the local custody relation only.

    This does not assert installation or external authority. Callers performing
    migration must do so under their own BEGIN IMMEDIATE transaction.
    """
    q.execute(_CUSTODY_DDL)
    row = q.execute(
        "SELECT type,sql FROM sqlite_master WHERE name=?", (_CUSTODY_TABLE,)
    ).fetchone()
    if row != ("table", _CUSTODY_STORED_DDL):
        raise DatabaseIdentityError("identity custody schema mismatch")


def _connect(path: str | Path) -> sqlite3.Connection:
    q = sqlite3.connect(str(path), timeout=5, isolation_level=None)
    q.execute("PRAGMA busy_timeout=5000")
    return q


def _load_custody(q: sqlite3.Connection) -> IdentityCustody | None:
    row = q.execute(
        f"""
        SELECT status,nonce_hex,bootstrap_generation_id,payload_digest,
               intent_request_id,provider_id,provider_generation,position,
               receipt_binding,logical_database_identity_digest
        FROM {_CUSTODY_TABLE} WHERE singleton=1
        """
    ).fetchone()
    if row is None:
        return None
    return IdentityCustody(*row)


def _identity_intent_present(q: sqlite3.Connection) -> bool:
    return (
        q.execute(
            "SELECT 1 FROM shared_anchor_intents WHERE intent_id=? LIMIT 1",
            (IDENTITY_INTENT_ID,),
        ).fetchone()
        is not None
    )


def classify_identity_custody(path: str | Path) -> IdentityCustodyState:
    """Read-only fail-closed classifier for already-created custody schema."""
    path = Path(path)
    if not path.exists():
        return IdentityCustodyState.ABSENT
    if not path.is_file():
        return IdentityCustodyState.CORRUPT
    q = _connect(path)
    try:
        relation = q.execute(
            "SELECT type,sql FROM sqlite_master WHERE name=?",
            (_CUSTODY_TABLE,),
        ).fetchone()
        anchor_relation = q.execute(
            "SELECT type FROM sqlite_master WHERE name='shared_anchor_intents'"
        ).fetchone()
        if relation is None:
            if anchor_relation == ("table",) and _identity_intent_present(q):
                return IdentityCustodyState.CORRUPT
            return IdentityCustodyState.ABSENT
        if relation != ("table", _CUSTODY_STORED_DDL):
            return IdentityCustodyState.CORRUPT
        if anchor_relation != ("table",):
            return IdentityCustodyState.CORRUPT

        rows = q.execute(f"SELECT COUNT(*) FROM {_CUSTODY_TABLE}").fetchone()[0]
        if rows == 0:
            if _identity_intent_present(q):
                return IdentityCustodyState.CORRUPT
            return IdentityCustodyState.ABSENT
        if rows != 1:
            return IdentityCustodyState.CORRUPT

        c = _load_custody(q)
        if c is None:
            return IdentityCustodyState.CORRUPT
        try:
            _require_digest(c.nonce_hex, "nonce_hex")
            _require_digest(c.bootstrap_generation_id, "bootstrap_generation_id")
            _require_digest(c.payload_digest, "payload_digest")
            _require_nonempty(c.intent_request_id, "intent_request_id")
            if c.payload_digest != identity_payload_digest(
                nonce_hex=c.nonce_hex,
                bootstrap_generation_id=c.bootstrap_generation_id,
            ):
                return IdentityCustodyState.CORRUPT
        except DatabaseIdentityError:
            return IdentityCustodyState.CORRUPT

        intent = q.execute(
            """
            SELECT component_id,intent_type,payload_digest,provider_id,
                   provider_generation,position,request_id,status,receipt_binding
            FROM shared_anchor_intents WHERE intent_id=?
            """,
            (IDENTITY_INTENT_ID,),
        ).fetchone()
        if intent is None:
            return IdentityCustodyState.CORRUPT
        (
            component_id, intent_type, intent_payload_digest, provider_id,
            provider_generation, position, request_id, intent_status,
            receipt_binding,
        ) = intent
        if (
            component_id != IDENTITY_COMPONENT
            or intent_type != "migration"
            or intent_payload_digest != c.payload_digest
            or request_id != c.intent_request_id
        ):
            return IdentityCustodyState.CORRUPT

        if intent_status == "PREPARED":
            if (
                c.status != "PREPARED"
                or receipt_binding is not None
                or c.provider_id is not None
                or c.provider_generation is not None
                or c.position is not None
                or c.receipt_binding is not None
                or c.logical_database_identity_digest is not None
            ):
                return IdentityCustodyState.CORRUPT
            return IdentityCustodyState.PREPARED

        if intent_status != "CONFIRMED":
            return IdentityCustodyState.CORRUPT
        try:
            _require_nonempty(provider_id, "provider_id")
            if type(provider_generation) is not int or provider_generation < 1:
                return IdentityCustodyState.CORRUPT
            if type(position) is not int or position < 1:
                return IdentityCustodyState.CORRUPT
            _require_digest(receipt_binding, "receipt_binding")
        except DatabaseIdentityError:
            return IdentityCustodyState.CORRUPT

        expected = confirmed_identity_digest(
            payload_digest=c.payload_digest,
            provider_id=provider_id,
            provider_generation=provider_generation,
            position=position,
            request_id=request_id,
            receipt_binding=receipt_binding,
        )

        if c.status == "PREPARED":
            if any(
                value is not None
                for value in (
                    c.provider_id,
                    c.provider_generation,
                    c.position,
                    c.receipt_binding,
                    c.logical_database_identity_digest,
                )
            ):
                return IdentityCustodyState.CORRUPT
            return IdentityCustodyState.CONFIRMED_NEEDS_FINALIZE

        if c.status != "CONFIRMED":
            return IdentityCustodyState.CORRUPT
        if (
            c.provider_id != provider_id
            or c.provider_generation != provider_generation
            or c.position != position
            or c.receipt_binding != receipt_binding
            or c.logical_database_identity_digest != expected
        ):
            return IdentityCustodyState.CORRUPT
        return IdentityCustodyState.COMPLETE
    except sqlite3.Error:
        return IdentityCustodyState.CORRUPT
    finally:
        q.close()
