from __future__ import annotations

import hmac
from dataclasses import dataclass

from .protocol import RotationAuthority, Signature, ThresholdNotMet, mac, sha


def _hex64(value):
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(c in "0123456789abcdef" for c in value)
    )


@dataclass(frozen=True)
class ThresholdEnablement:
    start_provider_generation_id: str
    start_provider_generation: int
    authority_id: str
    authority_version: int
    authority_generation: int
    signatures: tuple[Signature, ...]

    def validate(self):
        if not _hex64(self.start_provider_generation_id):
            raise ThresholdNotMet("invalid provider generation identity")
        if type(self.start_provider_generation) is not int or self.start_provider_generation < 1:
            raise ThresholdNotMet("invalid provider generation")
        if not _hex64(self.authority_id):
            raise ThresholdNotMet("invalid authority identity")
        if type(self.authority_version) is not int or self.authority_version < 1:
            raise ThresholdNotMet("invalid authority version")
        if type(self.authority_generation) is not int or self.authority_generation < 1:
            raise ThresholdNotMet("invalid authority generation")
        if type(self.signatures) is not tuple:
            raise ThresholdNotMet("signatures must be a tuple")
        return self

    @property
    def payload(self):
        self.validate()
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
    enablement = ThresholdEnablement(
        start_provider_generation_id,
        start_provider_generation,
        authority.authority_id,
        authority.version,
        authority.generation,
        tuple(signatures),
    )
    return enablement.validate()


def verify_enablement(authority: RotationAuthority, enablement: ThresholdEnablement):
    authority.validate()
    enablement.validate()
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
        if sig.signer_id in revoked:
            continue
        hx = authority.keys.get(sig.signer_id)
        if hx is None:
            continue
        if hmac.compare_digest(mac(bytes.fromhex(hx), enablement.payload), sig.signature):
            seen.add(sig.signer_id)
            valid.append(sig.signer_id)
    if len(valid) < authority.threshold:
        raise ThresholdNotMet(
            f"enablement valid={len(valid)} threshold={authority.threshold}"
        )
    return tuple(sorted(valid))
