"""Test-only LAB-099 durable cutover storage oracle.

This module freezes the SQLite materialization relation plus the deterministic
shared-anchor cross-binding selected by LAB099_DURABLE_CUTOVER_EVIDENCE_STORAGE_V1_FROZEN.
It is side-effect free and imports no production LAB-099 code.
"""

from __future__ import annotations

import hashlib
import json


CUTOVER_RELATION_NAME = "provider_activation_reservation_cutovers"
CUTOVER_RELATION_SQL = """CREATE TABLE provider_activation_reservation_cutovers(
  logical_database_identity_digest BLOB NOT NULL CHECK(typeof(logical_database_identity_digest)='blob' AND length(logical_database_identity_digest)=32),
  target_schema_set_id TEXT NOT NULL,
  target_schema_set_version INTEGER NOT NULL CHECK(target_schema_set_version=1),
  predecessor_provenance_head_digest BLOB NOT NULL CHECK(typeof(predecessor_provenance_head_digest)='blob' AND length(predecessor_provenance_head_digest)=32),
  predecessor_provenance_epoch INTEGER NOT NULL CHECK(predecessor_provenance_epoch>=0),
  prepared_canonical BLOB NOT NULL,
  prepared_digest BLOB NOT NULL UNIQUE CHECK(typeof(prepared_digest)='blob' AND length(prepared_digest)=32),
  confirmation_nonce BLOB NOT NULL CHECK(typeof(confirmation_nonce)='blob' AND length(confirmation_nonce)=32),
  anchor_intent_id TEXT NOT NULL UNIQUE,
  PRIMARY KEY(logical_database_identity_digest,target_schema_set_id,target_schema_set_version),
  UNIQUE(logical_database_identity_digest,predecessor_provenance_head_digest,predecessor_provenance_epoch)
)"""
CUTOVER_RELATION_DEFINITION_DIGEST = bytes.fromhex(
    "0db2587bae8861d0233d939b4283a58b438b947c5336f7af9d0f1687856c860e"
)

ANCHOR_COMPONENT_ID = "provider-activation-reservation-precursor"
ANCHOR_INTENT_TYPE = "migration"
ANCHOR_CONTRACT = "provider-activation-reservation-precursor-cutover"
ANCHOR_VERSION = 1
ANCHOR_INTENT_PREFIX = (
    "migration:provider-activation-reservation-precursor-cutover:v1:"
)
CONFIRMED_HEAD_DOMAIN = "ytim.lab099.shared-anchor-confirmed-head.v1"

REFERENCE_PREPARED_DIGEST = bytes.fromhex(
    "77ffdf5f657510a285d75e866d3418a85d1aeb0ca0f2c830617c850a5277b53e"
)
REFERENCE_CONFIRMATION_NONCE = bytes(range(0xE0, 0x100))
REFERENCE_ANCHOR_PAYLOAD_DIGEST = bytes.fromhex(
    "8aee140ac30142fac83fe03f95f36e56be94583b4ef100060610bb9ec59089e9"
)


def _canon(obj: object) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _normalized_sql(sql: str) -> str:
    return " ".join(sql.split())


def _digest32(value: bytes, label: str) -> bytes:
    if type(value) is not bytes or len(value) != 32:
        raise ValueError(f"{label} must be exact 32-byte bytes")
    return value


def anchor_intent_id(prepared_digest: bytes) -> str:
    return ANCHOR_INTENT_PREFIX + _digest32(prepared_digest, "prepared_digest").hex()


def anchor_payload(prepared_digest: bytes, confirmation_nonce: bytes) -> dict:
    return {
        "contract": ANCHOR_CONTRACT,
        "version": ANCHOR_VERSION,
        "prepared_digest": _digest32(prepared_digest, "prepared_digest").hex(),
        "confirmation_nonce": _digest32(
            confirmation_nonce, "confirmation_nonce"
        ).hex(),
    }


def anchor_payload_digest(prepared_digest: bytes, confirmation_nonce: bytes) -> bytes:
    payload = anchor_payload(prepared_digest, confirmation_nonce)
    intent_digest_input = {
        "component_id": ANCHOR_COMPONENT_ID,
        "intent_type": ANCHOR_INTENT_TYPE,
        "payload": payload,
    }
    return hashlib.sha256(_canon(intent_digest_input)).digest()


def confirmed_head_digest(entry: dict) -> bytes:
    required = {
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
    }
    if type(entry) is not dict or set(entry) != required:
        raise ValueError("confirmed shared-anchor entry shape mismatch")
    if entry["component_id"] != ANCHOR_COMPONENT_ID:
        raise ValueError("confirmed entry component mismatch")
    if entry["intent_type"] != ANCHOR_INTENT_TYPE:
        raise ValueError("confirmed entry type mismatch")
    if entry["status"] != "CONFIRMED":
        raise ValueError("confirmed head requires CONFIRMED entry")
    if not isinstance(entry["receipt_binding"], str) or len(entry["receipt_binding"]) != 64:
        raise ValueError("confirmed receipt binding mismatch")
    body = {"domain": CONFIRMED_HEAD_DOMAIN, **entry}
    return hashlib.sha256(_canon(body)).digest()


def validate_reference() -> bool:
    relation_digest = hashlib.sha256(
        _normalized_sql(CUTOVER_RELATION_SQL).encode("utf-8")
    ).digest()
    if relation_digest != CUTOVER_RELATION_DEFINITION_DIGEST:
        raise AssertionError("cutover relation definition digest drift")
    if anchor_intent_id(REFERENCE_PREPARED_DIGEST) != (
        ANCHOR_INTENT_PREFIX + REFERENCE_PREPARED_DIGEST.hex()
    ):
        raise AssertionError("anchor intent identity drift")
    if anchor_payload_digest(
        REFERENCE_PREPARED_DIGEST, REFERENCE_CONFIRMATION_NONCE
    ) != REFERENCE_ANCHOR_PAYLOAD_DIGEST:
        raise AssertionError("anchor payload digest drift")
    return True


if __name__ == "__main__":
    assert validate_reference()
