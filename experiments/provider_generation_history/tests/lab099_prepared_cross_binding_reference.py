"""Test-only LAB-099 PREPARED materialization/shared-anchor cross-binding oracle.

Side-effect free. This module verifies that one durable cutover materialization row and
one shared-anchor PREPARED row describe the exact same frozen PREPARED authority. It
imports only independent test-owned LAB-099 reference vectors/oracles and does not touch
production provenance code or SQLite.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from experiments.provider_generation_history.tests import (
    lab099_cutover_storage_reference as storage,
)
from experiments.provider_generation_history.tests import (
    lab099_precursor_reference_vectors as authority,
)


class PreparedCrossBindingError(ValueError):
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


def _canon(obj: object) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _exact_dict(value: Any, fields: tuple[str, ...], label: str) -> dict[str, Any]:
    if type(value) is not dict or set(value) != set(fields):
        raise PreparedCrossBindingError(f"{label} shape mismatch")
    return value


def _digest32(value: Any, label: str) -> bytes:
    if type(value) is not bytes or len(value) != 32:
        raise PreparedCrossBindingError(f"{label} must be exact 32-byte bytes")
    return value


def _positive_int(value: Any, label: str) -> int:
    if type(value) is not int or value < 1:
        raise PreparedCrossBindingError(f"{label} must be an exact positive int")
    return value


def _nonnegative_int(value: Any, label: str) -> int:
    if type(value) is not int or value < 0:
        raise PreparedCrossBindingError(f"{label} must be an exact non-negative int")
    return value


def _request_id(
    position: int,
    intent_id: str,
    component_id: str,
    intent_type: str,
    payload_digest: str,
) -> str:
    binding = hashlib.sha256(
        _canon(
            {
                "position": position,
                "intent_id": intent_id,
                "component_id": component_id,
                "intent_type": intent_type,
                "payload_digest": payload_digest,
            }
        )
    ).hexdigest()
    return f"shared-anchor:{position}:{binding}"


def verify_prepared_cross_binding(
    materialization: dict[str, Any],
    anchor_prepared: dict[str, Any],
    *,
    expected_provider_id: str,
    expected_provider_generation: int,
    expected_predecessor_position: int,
) -> bool:
    """Fail closed unless both rows bind one exact frozen PREPARED authority."""

    materialization = _exact_dict(
        materialization, _MATERIALIZATION_FIELDS, "materialization"
    )
    anchor_prepared = _exact_dict(anchor_prepared, _ANCHOR_FIELDS, "anchor PREPARED")

    if type(expected_provider_id) is not str or not expected_provider_id:
        raise PreparedCrossBindingError("expected_provider_id must be exact non-empty text")
    _positive_int(expected_provider_generation, "expected_provider_generation")
    _nonnegative_int(expected_predecessor_position, "expected_predecessor_position")

    prepared_canonical = materialization["prepared_canonical"]
    if type(prepared_canonical) is not bytes:
        raise PreparedCrossBindingError("prepared_canonical must be exact bytes")
    prepared_digest = _digest32(materialization["prepared_digest"], "prepared_digest")
    if hashlib.sha256(prepared_canonical).digest() != prepared_digest:
        raise PreparedCrossBindingError("prepared canonical/digest mismatch")
    if prepared_canonical != authority.PREPARED_CANONICAL_BYTES:
        raise PreparedCrossBindingError("prepared canonical differs from frozen PREPARED")
    if prepared_digest != authority.PREPARED_DIGEST:
        raise PreparedCrossBindingError("prepared digest differs from frozen PREPARED")

    values = authority.PREPARED_REFERENCE_VALUES
    expected_materialization = (
        values[1],
        values[5],
        values[6],
        values[3],
        values[4],
    )
    actual_materialization = tuple(
        materialization[field] for field in _MATERIALIZATION_FIELDS[:5]
    )
    if actual_materialization != expected_materialization:
        raise PreparedCrossBindingError("materialization PREPARED semantics mismatch")

    confirmation_nonce = _digest32(
        materialization["confirmation_nonce"], "confirmation_nonce"
    )
    if confirmation_nonce != authority.CONFIRMATION_NONCE:
        raise PreparedCrossBindingError("confirmation nonce differs from frozen PREPARED")

    intent_id = storage.anchor_intent_id(prepared_digest)
    if materialization["anchor_intent_id"] != intent_id:
        raise PreparedCrossBindingError("materialization anchor intent identity mismatch")

    payload_digest = storage.anchor_payload_digest(
        prepared_digest, confirmation_nonce
    ).hex()
    position = expected_predecessor_position + 1
    request_id = _request_id(
        position,
        intent_id,
        storage.ANCHOR_COMPONENT_ID,
        storage.ANCHOR_INTENT_TYPE,
        payload_digest,
    )
    expected_anchor = {
        "intent_id": intent_id,
        "component_id": storage.ANCHOR_COMPONENT_ID,
        "intent_type": storage.ANCHOR_INTENT_TYPE,
        "payload_digest": payload_digest,
        "provider_id": expected_provider_id,
        "provider_generation": expected_provider_generation,
        "predecessor_position": expected_predecessor_position,
        "position": position,
        "request_id": request_id,
        "status": "PREPARED",
        "receipt_binding": None,
    }
    if anchor_prepared != expected_anchor:
        raise PreparedCrossBindingError("shared-anchor PREPARED cross-binding mismatch")
    return True


def reference_rows() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Return deterministic exact rows plus runtime authority expected by the verifier."""

    values = authority.PREPARED_REFERENCE_VALUES
    materialization = dict(
        zip(
            _MATERIALIZATION_FIELDS,
            (
                values[1],
                values[5],
                values[6],
                values[3],
                values[4],
                authority.PREPARED_CANONICAL_BYTES,
                authority.PREPARED_DIGEST,
                authority.CONFIRMATION_NONCE,
                storage.anchor_intent_id(authority.PREPARED_DIGEST),
            ),
            strict=True,
        )
    )
    provider_id = "provider-alpha"
    provider_generation = 8
    predecessor_position = 41
    intent_id = materialization["anchor_intent_id"]
    payload_digest = storage.anchor_payload_digest(
        authority.PREPARED_DIGEST, authority.CONFIRMATION_NONCE
    ).hex()
    position = predecessor_position + 1
    anchor = {
        "intent_id": intent_id,
        "component_id": storage.ANCHOR_COMPONENT_ID,
        "intent_type": storage.ANCHOR_INTENT_TYPE,
        "payload_digest": payload_digest,
        "provider_id": provider_id,
        "provider_generation": provider_generation,
        "predecessor_position": predecessor_position,
        "position": position,
        "request_id": _request_id(
            position,
            intent_id,
            storage.ANCHOR_COMPONENT_ID,
            storage.ANCHOR_INTENT_TYPE,
            payload_digest,
        ),
        "status": "PREPARED",
        "receipt_binding": None,
    }
    expected = {
        "expected_provider_id": provider_id,
        "expected_provider_generation": provider_generation,
        "expected_predecessor_position": predecessor_position,
    }
    return materialization, anchor, expected


def validate_reference() -> bool:
    materialization, anchor, expected = reference_rows()
    if verify_prepared_cross_binding(materialization, anchor, **expected) is not True:
        raise AssertionError("reference PREPARED cross-binding failed")

    negative_cases = []

    changed_nonce = dict(materialization)
    changed_nonce["confirmation_nonce"] = bytes(reversed(authority.CONFIRMATION_NONCE))
    negative_cases.append((changed_nonce, anchor, expected))

    changed_digest = dict(materialization)
    changed_digest["prepared_digest"] = bytes(32)
    negative_cases.append((changed_digest, anchor, expected))

    stale_provider = dict(expected)
    stale_provider["expected_provider_generation"] += 1
    negative_cases.append((materialization, anchor, stale_provider))

    stale_tail = dict(expected)
    stale_tail["expected_predecessor_position"] += 1
    negative_cases.append((materialization, anchor, stale_tail))

    for bad_materialization, bad_anchor, bad_expected in negative_cases:
        try:
            verify_prepared_cross_binding(
                bad_materialization, bad_anchor, **bad_expected
            )
        except PreparedCrossBindingError:
            continue
        raise AssertionError("negative PREPARED cross-binding case was accepted")
    return True


if __name__ == "__main__":
    assert validate_reference()
