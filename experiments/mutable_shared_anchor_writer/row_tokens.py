from __future__ import annotations

import hashlib
import json

from .operation_permit import PermitConnection


def _token(kind: str, values) -> str:
    raw = json.dumps(
        {"kind": kind, "values": list(values)},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode()
    return hashlib.sha256(raw).hexdigest()


def intent_row_token(
    intent_id,
    component_id,
    intent_type,
    payload_digest,
    provider_id,
    provider_generation,
    predecessor_position,
    position,
    request_id,
    status,
    receipt_binding,
) -> str:
    return _token(
        "shared-anchor-intent-row-v1",
        (
            intent_id,
            component_id,
            intent_type,
            payload_digest,
            provider_id,
            provider_generation,
            predecessor_position,
            position,
            request_id,
            status,
            receipt_binding,
        ),
    )


def receipt_row_token(
    request_id,
    provider_id,
    generation,
    position,
    kind,
    challenge,
    signature,
    stable_binding,
) -> str:
    return _token(
        "asymmetric-provider-receipt-row-v1",
        (
            request_id,
            provider_id,
            generation,
            position,
            kind,
            challenge,
            signature,
            stable_binding,
        ),
    )


def install_row_token_udfs(q: PermitConnection) -> None:
    if type(q) is not PermitConnection:
        raise TypeError("exact LAB-091 permit connection required")
    q.create_function("lab091_intent_row_token", 11, intent_row_token)
    q.create_function("lab091_receipt_row_token", 8, receipt_row_token)
