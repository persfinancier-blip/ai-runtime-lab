from __future__ import annotations

import hashlib
import sqlite3
from pathlib import Path

from experiments.provider_generation_history.activation_schema_provenance import (
    ProvenancedHistoricalSharedAnchorLedger,
)
from experiments.provider_generation_history.protocol import HistoricalVerificationError


_PRECURSOR_RELATION_NAME = "provider_activation_reservation_precursors"
_PRECURSOR_RELATION_DDL_V1 = """CREATE TABLE provider_activation_reservation_precursors(
  activation_id TEXT PRIMARY KEY,
  logical_database_identity_digest TEXT NOT NULL,
  parent_chain_link_digest TEXT NOT NULL,
  parent_epoch INTEGER NOT NULL,
  old_generation_id TEXT NOT NULL,
  new_generation_id TEXT NOT NULL,
  successor_provider_id TEXT NOT NULL,
  successor_generation INTEGER NOT NULL,
  successor_key_id TEXT NOT NULL,
  expected_position INTEGER NOT NULL,
  protocol_version INTEGER NOT NULL CHECK(protocol_version=1),
  predecessor_mac TEXT NOT NULL,
  successor_mac TEXT NOT NULL,
  UNIQUE(logical_database_identity_digest,parent_chain_link_digest,parent_epoch)
)"""
_PRECURSOR_RELATION_DEFINITION_DIGEST = bytes.fromhex(
    "696c54d1afdef52c05c120ce7d09a7a2eeb567daafb3a378b7dc4ca64f80e3bb"
)
_CUTOVER_RELATION_NAME = "provider_activation_reservation_cutovers"
_CUTOVER_COMPONENT = "provider-activation-reservation-precursor"
_CUTOVER_INTENT_TYPE = "migration"
_CUTOVER_INTENT_PREFIX = "migration:provider-activation-reservation-precursor-cutover:v1:"


class PrecursorCutoverMigrationRequired(HistoricalVerificationError):
    """The LAB-099 authenticated precursor cutover has not completed."""


class PrecursorCutoverVerificationError(HistoricalVerificationError):
    """Durable LAB-099 precursor-cutover state is inconsistent or unauthenticated."""


def _normalized_sql(sql: str) -> str:
    return " ".join(sql.split())


def _connect(path: Path | str) -> sqlite3.Connection:
    q = sqlite3.connect(str(path), timeout=5, isolation_level=None)
    q.execute("PRAGMA busy_timeout=5000")
    return q


def _relation_state(q: sqlite3.Connection) -> str:
    row = q.execute(
        "SELECT type,sql FROM sqlite_master WHERE name=?",
        (_PRECURSOR_RELATION_NAME,),
    ).fetchone()
    if row is None:
        return "ABSENT"
    if row[0] != "table" or row[1] is None:
        return "MISMATCH"
    normalized = _normalized_sql(row[1])
    digest = hashlib.sha256(normalized.encode("utf-8", errors="strict")).digest()
    if digest != _PRECURSOR_RELATION_DEFINITION_DIGEST:
        return "MISMATCH"
    if normalized != _normalized_sql(_PRECURSOR_RELATION_DDL_V1):
        return "MISMATCH"
    return "EXACT"


def _cutover_row(q: sqlite3.Connection):
    object_row = q.execute(
        "SELECT type FROM sqlite_master WHERE name=?",
        (_CUTOVER_RELATION_NAME,),
    ).fetchone()
    if object_row is None:
        return None
    if object_row[0] != "table":
        raise PrecursorCutoverVerificationError("LAB-099 cutover relation is not a table")
    columns = {
        row[1]
        for row in q.execute(f'PRAGMA table_info("{_CUTOVER_RELATION_NAME}")').fetchall()
    }
    required = {
        "prepared_digest",
        "anchor_intent_id",
        "prepared_canonical",
        "confirmation_nonce",
    }
    if not required.issubset(columns):
        raise PrecursorCutoverVerificationError("LAB-099 cutover relation shape mismatch")
    rows = q.execute(
        "SELECT prepared_digest,anchor_intent_id FROM provider_activation_reservation_cutovers"
    ).fetchall()
    if len(rows) != 1:
        raise PrecursorCutoverVerificationError("LAB-099 cutover must contain exactly one evidence row")
    prepared_digest, intent_id = rows[0]
    if type(prepared_digest) is not bytes or len(prepared_digest) != 32:
        raise PrecursorCutoverVerificationError("LAB-099 prepared digest is malformed")
    expected_intent_id = _CUTOVER_INTENT_PREFIX + prepared_digest.hex()
    if intent_id != expected_intent_id:
        raise PrecursorCutoverVerificationError("LAB-099 cutover intent cross-binding mismatch")
    return prepared_digest, intent_id


def _marker_state(q: sqlite3.Connection, intent_id: str) -> str:
    row = q.execute(
        "SELECT component_id,intent_type,status,receipt_binding "
        "FROM shared_anchor_intents WHERE intent_id=?",
        (intent_id,),
    ).fetchone()
    if row is None:
        return "MISSING"
    component_id, intent_type, status, receipt_binding = row
    if component_id != _CUTOVER_COMPONENT or intent_type != _CUTOVER_INTENT_TYPE:
        raise PrecursorCutoverVerificationError("LAB-099 shared-anchor marker identity mismatch")
    if status == "PREPARED":
        if receipt_binding is not None:
            raise PrecursorCutoverVerificationError("LAB-099 PREPARED marker already has receipt")
        return "PREPARED"
    if status == "CONFIRMED":
        if type(receipt_binding) is not str or len(receipt_binding) != 64:
            raise PrecursorCutoverVerificationError("LAB-099 CONFIRMED marker receipt is malformed")
        return "CONFIRMED"
    raise PrecursorCutoverVerificationError("LAB-099 shared-anchor marker status mismatch")


def classify_precursor_cutover_v1(path: Path | str) -> str:
    """Classify durable V1 cutover state without mutating the database."""

    q = _connect(path)
    try:
        ledger = q.execute(
            "SELECT type FROM sqlite_master WHERE name='shared_anchor_intents'"
        ).fetchone()
        if ledger is None or ledger[0] != "table":
            raise PrecursorCutoverVerificationError(
                "LAB-099 requires an existing shared-anchor intent ledger"
            )

        relation = _relation_state(q)
        try:
            cutover = _cutover_row(q)
        except sqlite3.DatabaseError as exc:
            raise PrecursorCutoverVerificationError(
                "LAB-099 cutover evidence cannot be read"
            ) from exc

        if relation == "ABSENT" and cutover is None:
            return "ABSENT"
        if relation == "MISMATCH":
            return "CORRUPT_RELATION"
        if relation == "EXACT" and cutover is None:
            return "ORPHAN_UNAUTHENTICATED_SCHEMA"
        if relation == "ABSENT" and cutover is not None:
            return "CONFIRMED_RELATION_MISSING"

        assert relation == "EXACT" and cutover is not None
        _, intent_id = cutover
        marker = _marker_state(q, intent_id)
        if marker == "MISSING":
            return "ORPHAN_UNAUTHENTICATED_SCHEMA"
        if marker == "PREPARED":
            return "PREPARED_INCOMPLETE"
        if marker == "CONFIRMED":
            return "CONFIRMED"
        raise AssertionError("unreachable LAB-099 marker state")
    finally:
        q.close()


class PrecursorGovernedHistoricalSharedAnchorLedger(ProvenancedHistoricalSharedAnchorLedger):
    """LAB-099 startup surface gated on an authenticated precursor cutover."""

    def __init__(self, path, attested, bootstrap):
        state = classify_precursor_cutover_v1(path)
        if state == "ABSENT":
            raise PrecursorCutoverMigrationRequired(
                "LAB-099 precursor cutover requires explicit migration"
            )
        if state != "CONFIRMED":
            raise PrecursorCutoverVerificationError(
                f"LAB-099 precursor cutover is not validly confirmed: {state}"
            )
        super().__init__(path, attested, bootstrap)


def migrate_precursor_cutover_v1(path, attested, bootstrap):
    """Explicit LAB-099 migration entry point.

    The first production slice intentionally does not invent PREPARED/CONFIRMED
    authority. Migration remains closed until the next RED-driven slice binds the
    inherited LAB-092 completion/provenance head and existing shared-anchor execution.
    """

    state = classify_precursor_cutover_v1(path)
    if state == "CONFIRMED":
        return PrecursorGovernedHistoricalSharedAnchorLedger(path, attested, bootstrap)
    if state != "ABSENT":
        raise PrecursorCutoverVerificationError(
            f"LAB-099 cutover state is not safely migratable: {state}"
        )
    raise PrecursorCutoverMigrationRequired(
        "LAB-099 authenticated PREPARED migration authority is not implemented yet"
    )


def resume_precursor_cutover_v1(
    path,
    attested,
    bootstrap,
    *,
    expected_prepared_digest: bytes,
):
    """Resume only an already authenticated PREPARED cutover; fail closed for now."""

    if type(expected_prepared_digest) is not bytes or len(expected_prepared_digest) != 32:
        raise TypeError("expected_prepared_digest must be exact 32-byte bytes")
    state = classify_precursor_cutover_v1(path)
    if state != "PREPARED_INCOMPLETE":
        raise PrecursorCutoverVerificationError(
            f"LAB-099 resume requires exact PREPARED_INCOMPLETE state, got {state}"
        )
    q = _connect(path)
    try:
        row = q.execute(
            "SELECT prepared_digest FROM provider_activation_reservation_cutovers"
        ).fetchone()
        if row is None or row[0] != expected_prepared_digest:
            raise PrecursorCutoverVerificationError(
                "LAB-099 resume expected PREPARED digest mismatch"
            )
    finally:
        q.close()
    raise PrecursorCutoverMigrationRequired(
        "LAB-099 authenticated CONFIRMED transition is not implemented yet"
    )
