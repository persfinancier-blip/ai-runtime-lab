"""Test-only canonical reference for LAB-095 logical database/history identity.

This file is test authority only. Production code must independently derive and
authenticate the same identities; it must not import this module.
"""
from __future__ import annotations

import hashlib
import json

IDENTITY_COMPONENT = "provider-history-logical-database"
IDENTITY_INTENT_ID = "migration:logical-database-identity:v1"
IDENTITY_SCHEMA = "provider-history-logical-database"
IDENTITY_VERSION = 1


def _canon(obj: object) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _sha(obj: object) -> str:
    return hashlib.sha256(_canon(obj)).hexdigest()


def identity_payload(*, nonce_hex: str, bootstrap_generation_id: str) -> dict[str, object]:
    if (
        not isinstance(nonce_hex, str)
        or len(nonce_hex) != 64
        or any(c not in "0123456789abcdef" for c in nonce_hex)
    ):
        raise ValueError("nonce_hex must be 32 lowercase hex bytes")
    if (
        not isinstance(bootstrap_generation_id, str)
        or len(bootstrap_generation_id) != 64
        or any(c not in "0123456789abcdef" for c in bootstrap_generation_id)
    ):
        raise ValueError("bootstrap_generation_id must be a lowercase sha256 digest")
    return {
        "schema": IDENTITY_SCHEMA,
        "version": IDENTITY_VERSION,
        "nonce_hex": nonce_hex,
        "bootstrap_generation_id": bootstrap_generation_id,
    }


def confirmed_identity_digest(
    *,
    payload_digest: str,
    provider_id: str,
    provider_generation: int,
    position: int,
    request_id: str,
    receipt_binding: str,
) -> str:
    """Bind the logical DB identity to externally confirmed shared-anchor evidence."""
    return _sha(
        {
            "domain": "lab095-logical-database-identity-v1",
            "intent_id": IDENTITY_INTENT_ID,
            "component_id": IDENTITY_COMPONENT,
            "intent_type": "migration",
            "payload_digest": payload_digest,
            "provider_id": provider_id,
            "provider_generation": provider_generation,
            "position": position,
            "request_id": request_id,
            "receipt_binding": receipt_binding,
        }
    )


def genesis_parent_chain_link(
    *, logical_database_identity_digest: str, bootstrap_generation_id: str
) -> str:
    return _sha(
        {
            "domain": "lab095-provider-history-parent-link-v1",
            "logical_database_identity_digest": logical_database_identity_digest,
            "bootstrap_generation_id": bootstrap_generation_id,
        }
    )


def transition_parent_chain_link(
    *,
    logical_database_identity_digest: str,
    parent_chain_link_digest: str,
    provider_id: str,
    old_generation_id: str,
    new_generation_id: str,
    old_mac: str,
    new_mac: str,
) -> str:
    return _sha(
        {
            "domain": "lab095-provider-history-parent-link-v1",
            "logical_database_identity_digest": logical_database_identity_digest,
            "parent_chain_link_digest": parent_chain_link_digest,
            "transition": {
                "provider_id": provider_id,
                "old_generation_id": old_generation_id,
                "new_generation_id": new_generation_id,
                "old_mac": old_mac,
                "new_mac": new_mac,
            },
        }
    )
