from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass, replace
from enum import IntEnum
from typing import Iterable

class Sensitivity(IntEnum):
    PUBLIC = 0
    INTERNAL = 1
    CONFIDENTIAL = 2
    SECRET = 3

@dataclass(frozen=True)
class LabeledValue:
    value: str
    sensitivity: Sensitivity
    provenance: tuple[str, ...]
    declassified_by: str | None = None

    @property
    def content_digest(self) -> str:
        return hashlib.sha256(self.value.encode()).hexdigest()

@dataclass(frozen=True)
class Destination:
    name: str
    trust: str
    allowed_max: Sensitivity

@dataclass(frozen=True)
class Authorization:
    destination: str
    purpose: str
    max_sensitivity: Sensitivity
    generation: int
    issuer: str
    value_digest: str

@dataclass(frozen=True)
class DeclassificationGrant:
    source_digest: str
    target: Sensitivity
    rule_id: str
    generation: int
    issuer: str

@dataclass(frozen=True)
class EgressRequest:
    value: LabeledValue
    destination: Destination
    purpose: str
    authorization: Authorization | None
    current_auth_generation: int

@dataclass(frozen=True)
class Decision:
    allowed: bool
    reason: str
    evidence_record: dict[str, str | int]


def source(value: str, sensitivity: Sensitivity, source_id: str) -> LabeledValue:
    return LabeledValue(value, sensitivity, (f"source:{source_id}",))


def transform(values: Iterable[LabeledValue], output: str, transform_id: str) -> LabeledValue:
    vals = tuple(values)
    if not vals:
        raise ValueError("transform needs at least one input")
    sensitivity = max(v.sensitivity for v in vals)
    provenance = tuple(p for v in vals for p in v.provenance) + (f"transform:{transform_id}",)
    return LabeledValue(output, sensitivity, provenance)


def declassify(
    value: LabeledValue,
    output: str,
    target: Sensitivity,
    grant: DeclassificationGrant,
    *,
    current_generation: int,
) -> LabeledValue:
    if grant.issuer != "trusted-control":
        raise PermissionError("declassification grant is not trusted control-plane authority")
    if grant.generation != current_generation:
        raise PermissionError("declassification grant is stale")
    if grant.source_digest != value.content_digest:
        raise PermissionError("declassification grant source mismatch")
    if grant.target != target:
        raise PermissionError("declassification target mismatch")
    if target >= value.sensitivity:
        raise ValueError("declassification must lower sensitivity")
    return LabeledValue(output, target, value.provenance + (f"declassify:{grant.rule_id}",), grant.rule_id)


def propagate_fallback(value: LabeledValue, fallback_id: str) -> LabeledValue:
    return replace(value, provenance=value.provenance + (f"fallback:{fallback_id}",))


def evidence_ref(value: LabeledValue, *, audit_key: bytes = b"lab021-test-audit-key") -> dict[str, str | int]:
    opaque_digest = hmac.new(audit_key, value.value.encode(), hashlib.sha256).hexdigest()
    return {
        "opaque_digest": opaque_digest,
        "sensitivity": int(value.sensitivity),
        "provenance_digest": hashlib.sha256("|".join(value.provenance).encode()).hexdigest(),
    }


def authorize(req: EgressRequest) -> Decision:
    ev = evidence_ref(req.value)
    if req.value.sensitivity > req.destination.allowed_max:
        return Decision(False, "sink sensitivity ceiling exceeded", ev)
    if req.destination.trust == "untrusted" and req.value.sensitivity >= Sensitivity.CONFIDENTIAL:
        return Decision(False, "protected data cannot flow to untrusted destination", ev)

    if req.value.sensitivity >= Sensitivity.CONFIDENTIAL:
        auth = req.authorization
        if auth is None:
            return Decision(False, "sensitive egress requires authorization", ev)
        if auth.issuer != "trusted-control":
            return Decision(False, "authorization is not trusted control-plane authority", ev)
        if auth.generation != req.current_auth_generation:
            return Decision(False, "authorization is stale", ev)
        if auth.destination != req.destination.name:
            return Decision(False, "authorization destination mismatch", ev)
        if auth.value_digest != req.value.content_digest:
            return Decision(False, "authorization payload mismatch", ev)
        if auth.purpose != req.purpose:
            return Decision(False, "authorization purpose mismatch", ev)
        if req.value.sensitivity > auth.max_sensitivity:
            return Decision(False, "authorization sensitivity ceiling exceeded", ev)

    return Decision(True, "egress allowed", ev)


def unsafe_transform_drop_taint(secret: LabeledValue, output: str) -> LabeledValue:
    return LabeledValue(output, Sensitivity.PUBLIC, ("unsafe:taint_dropped",))
