from __future__ import annotations

from experiments.provider_rotation_recovery.protocol import RecoveryAuthority
from experiments.provider_threshold_rotation.protocol import RotationAuthority
from .asymmetric_custody import (
    PublicRecoveryAuthority,
    accepted_public_signatures,
    sha,
    verify_public_threshold,
)


class CustodyBreakGlassError(RuntimeError):
    pass


def custody_enablement_payload(
    root: RotationAuthority,
    symmetric_recovery,
    public_recovery: PublicRecoveryAuthority,
) -> dict:
    """Canonical immutable cutoff for enabling public-custody break-glass proofs."""
    root.validate()
    symmetric_recovery.validate()
    public_recovery.validate()
    return {
        "kind": "provider-recovery-custody-break-glass-enablement",
        "start_rotation_authority_id": root.authority_id,
        "start_rotation_version": root.version,
        "start_rotation_generation": root.generation,
        "symmetric_authority_id": symmetric_recovery.authority_id,
        "symmetric_version": symmetric_recovery.version,
        "symmetric_generation": symmetric_recovery.generation,
        "public_authority_id": public_recovery.authority_id,
        "public_version": public_recovery.version,
        "public_generation": public_recovery.generation,
    }


def custody_break_glass_payload(
    old_rotation: RotationAuthority,
    new_rotation: RotationAuthority,
    public_recovery: PublicRecoveryAuthority,
    compatibility_recovery: RecoveryAuthority,
    compatibility_intent_digest: str,
) -> dict:
    old_rotation.validate()
    new_rotation.validate()
    public_recovery.validate()
    compatibility_recovery.validate()
    return {
        "kind": "provider-rotation-authority-custody-break-glass-recovery",
        "old_rotation_authority_id": old_rotation.authority_id,
        "old_rotation_version": old_rotation.version,
        "old_rotation_generation": old_rotation.generation,
        "new_rotation_authority": new_rotation.descriptor,
        "public_recovery_authority_id": public_recovery.authority_id,
        "public_recovery_version": public_recovery.version,
        "public_recovery_generation": public_recovery.generation,
        "compatibility_recovery_authority_id": compatibility_recovery.authority_id,
        "compatibility_recovery_generation": compatibility_recovery.generation,
        "compatibility_intent_digest": compatibility_intent_digest,
    }


def accepted_custody_break_glass_signatures(authority, payload, signatures):
    accepted = accepted_public_signatures(authority, payload, signatures)
    verify_public_threshold(authority, payload, accepted)
    return accepted


def custody_break_glass_digest(payload: dict) -> str:
    return sha(payload)
