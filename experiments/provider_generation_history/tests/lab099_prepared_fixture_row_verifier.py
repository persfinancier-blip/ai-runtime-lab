"""Test-only LAB-099 persisted PREPARED fixture-row verifier.

This module reads the exact durable rows produced by ``install_atomic_prepared_cutover``
and delegates semantic authority checks to the side-effect-free cross-binding oracle.
It also exposes deliberately narrow test-only tamper helpers for RED-intent corruption
cases. Production code must not import this module or gain equivalent mutation hooks.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from experiments.provider_generation_history.tests import (
    lab099_cutover_storage_reference as storage,
)
from experiments.provider_generation_history.tests import (
    lab099_prepared_cross_binding_reference as cross_binding,
)


class PreparedFixtureRowVerificationError(ValueError):
    pass


_MATERIALIZATION_FIELDS = (
    "logical_database_identity_digest",
    "target_schema_set_id",
    "target_schema_set_version",
    "predecessor_provenance_head_digest",
    "predecessor_provenance_epoch",
    "prepared_canonical",
    "prepared_digest",
    "confirmation_nonce",
    "anchor_intent_id",
)
_ANCHOR_FIELDS = (
    "intent_id",
    "component_id",
    "intent_type",
    "payload_digest",
    "provider_id",
    "provider_generation",
    "predecessor_position",
    "position",
    "request_id",
    "status",
    "receipt_binding",
)
_TAMPER_FIELDS = {
    "confirmation_nonce",
    "prepared_digest",
    "provider_generation",
    "predecessor_position",
    "position",
    "request_id",
}


def _digest32(value: Any, label: str) -> bytes:
    if type(value) is not bytes or len(value) != 32:
        raise PreparedFixtureRowVerificationError(
            f"{label} must be exact 32-byte bytes"
        )
    return value


def _expected_provider(attested: Any) -> tuple[str, int]:
    verifier = getattr(attested, "verifier", None)
    expected = getattr(verifier, "expected", None)
    provider_id = getattr(expected, "provider_id", None)
    generation = getattr(expected, "generation", None)
    if type(provider_id) is not str or not provider_id:
        raise PreparedFixtureRowVerificationError(
            "attested verifier expected provider_id is unavailable"
        )
    if type(generation) is not int or generation < 1:
        raise PreparedFixtureRowVerificationError(
            "attested verifier expected generation is unavailable"
        )
    return provider_id, generation


def _connect(path: Path | str) -> sqlite3.Connection:
    q = sqlite3.connect(str(path), timeout=5, isolation_level=None)
    q.execute("PRAGMA busy_timeout=5000")
    return q


def _exact_one(rows: list[tuple[Any, ...]], label: str) -> tuple[Any, ...]:
    if len(rows) != 1:
        raise PreparedFixtureRowVerificationError(
            f"{label} must resolve to exactly one durable row"
        )
    return rows[0]


def verify_installed_prepared_cutover(
    path: Path | str,
    attested: Any,
    *,
    prepared_event_digest: bytes,
) -> bool:
    """Read back and fail closed unless the persisted PREPARED pair cross-binds exactly."""

    prepared_digest = _digest32(prepared_event_digest, "prepared_event_digest")
    provider_id, generation = _expected_provider(attested)

    q = _connect(path)
    try:
        materialization_row = _exact_one(
            q.execute(
                "SELECT " + ",".join(_MATERIALIZATION_FIELDS) + " "
                "FROM provider_activation_reservation_cutovers WHERE prepared_digest=?",
                (prepared_digest,),
            ).fetchall(),
            "PREPARED materialization",
        )
        materialization = dict(
            zip(_MATERIALIZATION_FIELDS, materialization_row, strict=True)
        )

        anchor_row = _exact_one(
            q.execute(
                "SELECT " + ",".join(_ANCHOR_FIELDS) + " "
                "FROM shared_anchor_intents WHERE intent_id=?",
                (materialization["anchor_intent_id"],),
            ).fetchall(),
            "shared-anchor PREPARED",
        )
        anchor = dict(zip(_ANCHOR_FIELDS, anchor_row, strict=True))

        meta = q.execute(
            "SELECT reserved_position FROM shared_anchor_meta WHERE singleton=1"
        ).fetchone()
        if meta is None or type(meta[0]) is not int or meta[0] < 1:
            raise PreparedFixtureRowVerificationError(
                "shared-anchor reserved_position is unavailable"
            )
        if anchor["position"] != meta[0]:
            raise PreparedFixtureRowVerificationError(
                "shared-anchor PREPARED position differs from durable reserved tail"
            )
        predecessor = meta[0] - 1
    finally:
        q.close()

    try:
        return cross_binding.verify_prepared_cross_binding(
            materialization,
            anchor,
            expected_provider_id=provider_id,
            expected_provider_generation=generation,
            expected_predecessor_position=predecessor,
        )
    except cross_binding.PreparedCrossBindingError as exc:
        raise PreparedFixtureRowVerificationError(
            "persisted PREPARED rows fail exact cross-binding"
        ) from exc


def tamper_prepared_fixture_for_test_only(
    path: Path | str,
    *,
    prepared_event_digest: bytes,
    field: str,
) -> None:
    """Mutate exactly one frozen binding field for fixture-level fail-closed checks."""

    digest = _digest32(prepared_event_digest, "prepared_event_digest")
    if field not in _TAMPER_FIELDS:
        raise PreparedFixtureRowVerificationError(
            "unsupported PREPARED fixture tamper field"
        )

    q = _connect(path)
    try:
        q.execute("BEGIN IMMEDIATE")
        intent_id = storage.anchor_intent_id(digest)
        if field == "confirmation_nonce":
            current = q.execute(
                "SELECT confirmation_nonce FROM provider_activation_reservation_cutovers "
                "WHERE prepared_digest=?",
                (digest,),
            ).fetchone()
            if current is None or type(current[0]) is not bytes or len(current[0]) != 32:
                raise PreparedFixtureRowVerificationError(
                    "confirmation nonce fixture row is unavailable"
                )
            changed = q.execute(
                "UPDATE provider_activation_reservation_cutovers "
                "SET confirmation_nonce=? WHERE prepared_digest=?",
                (bytes(reversed(current[0])), digest),
            ).rowcount
        elif field == "prepared_digest":
            replacement = bytes(32)
            if replacement == digest:
                replacement = bytes([1]) + bytes(31)
            changed = q.execute(
                "UPDATE provider_activation_reservation_cutovers "
                "SET prepared_digest=? WHERE prepared_digest=?",
                (replacement, digest),
            ).rowcount
        elif field in {"provider_generation", "predecessor_position", "position"}:
            changed = q.execute(
                f"UPDATE shared_anchor_intents SET {field}={field}+1 WHERE intent_id=?",
                (intent_id,),
            ).rowcount
        else:
            changed = q.execute(
                "UPDATE shared_anchor_intents SET request_id=request_id || ':tampered' "
                "WHERE intent_id=?",
                (intent_id,),
            ).rowcount
        if changed != 1:
            raise PreparedFixtureRowVerificationError(
                "fixture tamper did not mutate exactly one durable row"
            )
        q.commit()
    except:
        if q.in_transaction:
            q.rollback()
        raise
    finally:
        q.close()
