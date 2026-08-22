from __future__ import annotations

import hmac
from dataclasses import dataclass

from .protocol import (
    RotationAuthority,
    Signature,
    ThresholdNotMet,
    mac,
    sha,
)


@dataclass(frozen=True)
class ThresholdEnablement:
    start_provider_generation_id: str
    start_provider_generation: int
    authority_id: str
    authority_version: int
    authority_generation: int
    signatures: tuple[Signature, ...]

    @property
    def payload(self):
        return {
            "kind": "threshold-provider-rotation-enablement",
            "start_provider_generation_id": self.start_provider_generation_id,
            "start_provider_generation": self.start_provider_generation,
            "authority_id": self.authority_id,
            "authority_version": self.authority_version,
            "authority_generation": self.authority_generation,
        }

    @property
    def enablement_digest(self):
        return sha(self.payload)


def make_enablement(
    *,
    start_provider_generation_id: str,
    start_provider_generation: int,
    authority: RotationAuthority,
    signatures: tuple[Signature, ...],
):
    return ThresholdEnablement(
        start_provider_generation_id,
        start_provider_generation,
        authority.authority_id,
        authority.version,
        authority.generation,
        tuple(signatures),
    )


def verify_enablement(authority: RotationAuthority, enablement: ThresholdEnablement):
    authority.validate()
    if (
        enablement.authority_id != authority.authority_id
        or enablement.authority_version != authority.version
        or enablement.authority_generation != authority.generation
    ):
        raise ThresholdNotMet("enablement authority mismatch")
    seen = set()
    valid = []
    revoked = set(authority.revoked)
    for sig in enablement.signatures:
        if sig.signer_id in seen:
            continue
        seen.add(sig.signer_id)
        if sig.signer_id in revoked:
            continue
        hx = authority.keys.get(sig.signer_id)
        if hx is None:
            continue
        if hmac.compare_digest(
            mac(bytes.fromhex(hx), enablement.payload), sig.signature
        ):
            valid.append(sig.signer_id)
    if len(valid) < authority.threshold:
        raise ThresholdNotMet(
            f"enablement valid={len(valid)} threshold={authority.threshold}"
        )
    return tuple(sorted(valid))
