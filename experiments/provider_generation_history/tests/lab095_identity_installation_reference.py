"""Test-only LAB-095 identity installation/recovery state-machine reference.

This module freezes recovery semantics only. It is not production authority and
production code MUST NOT import it.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class IdentityInstallState(str, Enum):
    LEGACY_ABSENT = "LEGACY_ABSENT"
    PREPARED = "PREPARED"
    CONFIRMED_NEEDS_FINALIZE = "CONFIRMED_NEEDS_FINALIZE"
    COMPLETE = "COMPLETE"
    CORRUPT = "CORRUPT"


@dataclass(frozen=True)
class Snapshot:
    custody_present: bool
    custody_status: str | None
    custody_payload_digest: str | None
    intent_status: str | None
    intent_payload_digest: str | None
    receipt_binding_present: bool
    confirmed_identity_digest_present: bool


def classify(snapshot: Snapshot) -> IdentityInstallState:
    """Classify only persisted facts; never invent missing authority."""
    c = snapshot

    if not c.custody_present:
        if (
            c.custody_status is None
            and c.custody_payload_digest is None
            and c.intent_status is None
            and c.intent_payload_digest is None
            and not c.receipt_binding_present
            and not c.confirmed_identity_digest_present
        ):
            return IdentityInstallState.LEGACY_ABSENT
        return IdentityInstallState.CORRUPT

    if c.custody_status not in {"PREPARED", "CONFIRMED"}:
        return IdentityInstallState.CORRUPT
    if not c.custody_payload_digest:
        return IdentityInstallState.CORRUPT
    if c.intent_status not in {"PREPARED", "CONFIRMED"}:
        return IdentityInstallState.CORRUPT
    if c.intent_payload_digest != c.custody_payload_digest:
        return IdentityInstallState.CORRUPT

    if c.intent_status == "PREPARED":
        if c.custody_status != "PREPARED":
            return IdentityInstallState.CORRUPT
        if c.receipt_binding_present or c.confirmed_identity_digest_present:
            return IdentityInstallState.CORRUPT
        return IdentityInstallState.PREPARED

    if not c.receipt_binding_present:
        return IdentityInstallState.CORRUPT

    if c.custody_status == "PREPARED":
        if c.confirmed_identity_digest_present:
            return IdentityInstallState.CORRUPT
        return IdentityInstallState.CONFIRMED_NEEDS_FINALIZE

    if not c.confirmed_identity_digest_present:
        return IdentityInstallState.CORRUPT
    return IdentityInstallState.COMPLETE


def retry_action(state: IdentityInstallState) -> str:
    """Freeze which side effects are permitted from each persisted state."""
    return {
        IdentityInstallState.LEGACY_ABSENT: "BEGIN_INSTALL",
        IdentityInstallState.PREPARED: "RECONCILE_SAME_REQUEST",
        IdentityInstallState.CONFIRMED_NEEDS_FINALIZE: "FINALIZE_LOCALLY",
        IdentityInstallState.COMPLETE: "VERIFY_ONLY",
        IdentityInstallState.CORRUPT: "FAIL_CLOSED",
    }[state]


CONTRACT = {
    "nonce_custody": (
        "Generate 32 random bytes inside BEGIN IMMEDIATE only after observing "
        "LEGACY_ABSENT; caller-supplied nonce is forbidden."
    ),
    "atomic_prepare": (
        "Persist nonce/bootstrap/payload custody and the deterministic shared-anchor "
        "PREPARED identity intent in the same SQLite transaction."
    ),
    "prepared_crash": (
        "A crash before COMMIT leaves LEGACY_ABSENT; a crash after COMMIT leaves "
        "PREPARED and retry reuses the exact persisted nonce/payload/request."
    ),
    "unknown_provider": (
        "Provider timeout/UNKNOWN never creates a new nonce or request; retry uses "
        "RECONCILE for the same deterministic request identity."
    ),
    "confirmed_restart": (
        "If external confirmation is durable but the local identity digest was not "
        "finalized, reauthenticate the CONFIRMED row/receipt and derive the digest "
        "locally without another provider increment."
    ),
    "partial_states": (
        "Custody without matching intent, intent without custody, mismatched payload, "
        "local CONFIRMED before external CONFIRMED, or missing confirmed receipt fail closed."
    ),
    "concurrent_writer": (
        "BEGIN IMMEDIATE serializes first installation. A loser re-reads state and "
        "resumes the winner's PREPARED request; it never generates a second nonce."
    ),
    "legacy_migration": (
        "Existing valid history is migrated by reserving exactly the next shared-anchor "
        "position under the current verified provider generation."
    ),
}
