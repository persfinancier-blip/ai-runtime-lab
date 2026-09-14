from __future__ import annotations

import hashlib
import json

from .operation_permit import PermitConnection


def expected_request_id(position, intent_id, component_id, intent_type, payload_digest) -> str:
    raw = json.dumps(
        {
            "component_id": component_id,
            "intent_id": intent_id,
            "intent_type": intent_type,
            "payload_digest": payload_digest,
            "position": position,
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    return f"shared-anchor:{position}:{hashlib.sha256(raw).hexdigest()}"


def install_state_machine_udfs(q: PermitConnection) -> None:
    if type(q) is not PermitConnection:
        raise TypeError("exact LAB-091 permit connection required")
    q.create_function("lab091_expected_request_id", 5, expected_request_id)
