"""Test-only persisted LAB-099 CONFIRMED cutover verifier.

Reads the durable PREPARED materialization plus its shared-anchor row, requires the row
to be CONFIRMED, externally reauthenticates the stored receipt binding through the
existing shared-anchor RECONCILE semantics, and returns the exact confirmed-head digest
that a LAB-099 CONFIRMED authority event must bind.

Production code must not import this module.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any

from experiments.provider_generation_history.tests import lab099_cutover_storage_reference as storage
from experiments.provider_generation_history.tests import lab099_prepared_cross_binding_reference as prepared_cross


class ConfirmedFixtureRowVerificationError(ValueError):
    pass


_MATERIALIZATION_FIELDS = (
    "logical_database_identity_digest", "target_schema_set_id", "target_schema_set_version",
    "predecessor_provenance_head_digest", "predecessor_provenance_epoch", "prepared_canonical",
    "prepared_digest", "confirmation_nonce", "anchor_intent_id",
)
_ANCHOR_FIELDS = (
    "intent_id", "component_id", "intent_type", "payload_digest", "provider_id",
    "provider_generation", "predecessor_position", "position", "request_id", "status",
    "receipt_binding",
)
_TAMPER_FIELDS = {"receipt_binding", "position", "predecessor_position", "prepared_digest"}


def _canon(obj: object) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _stable_receipt(obs: Any) -> str:
    return hashlib.sha256(_canon({
        "provider_id": obs.provider_id,
        "generation": obs.generation,
        "position": obs.position,
        "request_id": obs.request_id,
    })).hexdigest()


def _digest32(value: Any, label: str) -> bytes:
    if type(value) is not bytes or len(value) != 32:
        raise ConfirmedFixtureRowVerificationError(f"{label} must be exact 32-byte bytes")
    return value


def _expected_provider(attested: Any) -> tuple[str, int]:
    expected = getattr(getattr(attested, "verifier", None), "expected", None)
    provider_id = getattr(expected, "provider_id", None)
    generation = getattr(expected, "generation", None)
    if type(provider_id) is not str or not provider_id or type(generation) is not int or generation < 1:
        raise ConfirmedFixtureRowVerificationError("attested provider identity is unavailable")
    return provider_id, generation


def _connect(path: Path | str) -> sqlite3.Connection:
    q = sqlite3.connect(str(path), timeout=5, isolation_level=None)
    q.execute("PRAGMA busy_timeout=5000")
    return q


def _one(rows: list[tuple[Any, ...]], label: str) -> tuple[Any, ...]:
    if len(rows) != 1:
        raise ConfirmedFixtureRowVerificationError(f"{label} must resolve to exactly one durable row")
    return rows[0]


def verify_installed_confirmed_cutover(path: Path | str, attested: Any, *, prepared_event_digest: bytes) -> bytes:
    """Fail closed unless persisted CONFIRMED evidence reauthenticates exactly.

    Returns the byte-exact shared-anchor confirmed-head digest for construction/checking
    of the LAB-099 CONFIRMED authority event; it does not invent a provenance head.
    """
    prepared_digest = _digest32(prepared_event_digest, "prepared_event_digest")
    provider_id, generation = _expected_provider(attested)
    q = _connect(path)
    try:
        materialization_row = _one(q.execute(
            "SELECT " + ",".join(_MATERIALIZATION_FIELDS) +
            " FROM provider_activation_reservation_cutovers WHERE prepared_digest=?",
            (prepared_digest,),
        ).fetchall(), "CONFIRMED materialization")
        materialization = dict(zip(_MATERIALIZATION_FIELDS, materialization_row, strict=True))
        anchor_row = _one(q.execute(
            "SELECT " + ",".join(_ANCHOR_FIELDS) + " FROM shared_anchor_intents WHERE intent_id=?",
            (materialization["anchor_intent_id"],),
        ).fetchall(), "shared-anchor CONFIRMED")
        anchor = dict(zip(_ANCHOR_FIELDS, anchor_row, strict=True))
    finally:
        q.close()

    if anchor["status"] != "CONFIRMED":
        raise ConfirmedFixtureRowVerificationError("shared-anchor entry is not CONFIRMED")
    receipt = anchor["receipt_binding"]
    if type(receipt) is not str or len(receipt) != 64 or any(c not in "0123456789abcdef" for c in receipt):
        raise ConfirmedFixtureRowVerificationError("stored receipt binding is malformed")

    # The PREPARED ancestry must remain exact even after status/receipt transition.
    prepared_shape = dict(anchor)
    prepared_shape["status"] = "PREPARED"
    prepared_shape["receipt_binding"] = None
    try:
        prepared_cross.verify_prepared_cross_binding(
            materialization,
            prepared_shape,
            expected_provider_id=provider_id,
            expected_provider_generation=generation,
            expected_predecessor_position=anchor["predecessor_position"],
        )
    except prepared_cross.PreparedCrossBindingError as exc:
        raise ConfirmedFixtureRowVerificationError("CONFIRMED row lost exact PREPARED ancestry") from exc

    challenge = attested.challenge()
    obs = attested.provider.reconcile_increment(challenge=challenge, request_id=anchor["request_id"])
    if obs is None:
        raise ConfirmedFixtureRowVerificationError("provider has no result for confirmed request")
    verified = attested.verifier.verify(obs, expected_challenge=challenge, allowed_kinds={"RECONCILE"})
    if verified.position != anchor["position"] or verified.request_id != anchor["request_id"]:
        raise ConfirmedFixtureRowVerificationError("reauthenticated result does not bind confirmed position/request")
    if _stable_receipt(verified) != receipt:
        raise ConfirmedFixtureRowVerificationError("stored receipt differs from reauthenticated provider result")

    return storage.confirmed_head_digest(anchor)


def tamper_confirmed_fixture_for_test_only(path: Path | str, *, prepared_event_digest: bytes, field: str) -> None:
    digest = _digest32(prepared_event_digest, "prepared_event_digest")
    if field not in _TAMPER_FIELDS:
        raise ConfirmedFixtureRowVerificationError("unsupported CONFIRMED fixture tamper field")
    q = _connect(path)
    try:
        q.execute("BEGIN IMMEDIATE")
        intent_id = storage.anchor_intent_id(digest)
        if field == "receipt_binding":
            changed = q.execute("UPDATE shared_anchor_intents SET receipt_binding=? WHERE intent_id=?",
                                ("00" * 32, intent_id)).rowcount
        elif field in {"position", "predecessor_position"}:
            changed = q.execute(f"UPDATE shared_anchor_intents SET {field}={field}+1 WHERE intent_id=?",
                                (intent_id,)).rowcount
        else:
            replacement = bytes(32) if digest != bytes(32) else bytes([1]) + bytes(31)
            changed = q.execute("UPDATE provider_activation_reservation_cutovers SET prepared_digest=? WHERE prepared_digest=?",
                                (replacement, digest)).rowcount
        if changed != 1:
            raise ConfirmedFixtureRowVerificationError("fixture tamper did not mutate exactly one row")
        q.commit()
    except:
        if q.in_transaction:
            q.rollback()
        raise
    finally:
        q.close()
