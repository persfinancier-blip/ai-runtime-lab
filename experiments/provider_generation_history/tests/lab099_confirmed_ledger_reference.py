"""Independent test-only LAB-099 CONFIRMED ledger/provenance bridge.

This freezes one exact CONFIRMED shared-anchor LedgerEntry, its stable RECONCILE
receipt binding, and the direct mapping from the authenticated ledger entry digest
to LAB-099 CONFIRMED provenance field 7. It does not mutate SQLite or import
production LAB-099 code.
"""
from __future__ import annotations

import hashlib
import json
import struct

from experiments.provider_generation_history.tests import lab099_cutover_storage_reference as storage
from experiments.provider_generation_history.tests import lab099_precursor_reference_vectors as authority

REFERENCE_PROVIDER_ID = "provider-alpha"
REFERENCE_PROVIDER_GENERATION = 8
REFERENCE_PREDECESSOR_POSITION = 41
REFERENCE_POSITION = 42
REFERENCE_REQUEST_ID = (
    "shared-anchor:42:9fda50427f6b8a55b305cd4a8833413a1f20b349bc21332bfaf0eb4de7d01bdf"
)
REFERENCE_RECEIPT_BINDING = (
    "ead923c6b9bcd68bc6e4276284fd72211544fcede9f06297b8bc074d898130b4"
)
REFERENCE_CONFIRMED_HEAD_DIGEST = bytes.fromhex(
    "45c53da7909f826f6c8107fef542ba17bed551df8637f8a3185fe66a04410dda"
)
REFERENCE_RESULTING_PROVENANCE_EPOCH = 8

BRIDGED_CONFIRMED_CANONICAL_BYTES = bytes.fromhex(
    "5954494d5052563100417974696d2e6c61623039392e61637469766174696f6e2d7265736572766174696f6e2d707265637572736f722d6375746f7665722d636f6e6669726d65642e7631000900010400000020000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f0002040000002077ffdf5f657510a285d75e866d3418a85d1aeb0ca0f2c830617c850a5277b53e00030400000020404142434445464748494a4b4c4d4e4f505152535455565758595a5b5c5d5e5f0004010000002970726f76696465722d61637469766174696f6e2d7265736572766174696f6e2d707265637572736f7200050300000008000000000000000100060400000020696c54d1afdef52c05c120ce7d09a7a2eeb567daafb3a378b7dc4ca64f80e3bb0007040000002045c53da7909f826f6c8107fef542ba17bed551df8637f8a3185fe66a04410dda00080300000008000000000000000800090200000020e0e1e2e3e4e5e6e7e8e9eaebecedeeeff0f1f2f3f4f5f6f7f8f9fafbfcfdfeff"
)
BRIDGED_CONFIRMED_DIGEST = bytes.fromhex(
    "e7f7083876141f73cc7e8adc88b39c5e6da7f9c10a83433d2a067588c54ae157"
)

_MAGIC = b"YTIMPRV1"
_UTF8 = 0x01
_BYTES = 0x02
_U64 = 0x03
_DIGEST32 = 0x04


def _canon(obj: object) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _field(field_id: int, type_code: int, value: bytes) -> bytes:
    return struct.pack(">HBI", field_id, type_code, len(value)) + value


def _record(domain: str, fields: tuple[tuple[int, int, bytes], ...]) -> bytes:
    domain_bytes = domain.encode("ascii")
    return (
        _MAGIC
        + struct.pack(">H", len(domain_bytes))
        + domain_bytes
        + struct.pack(">H", len(fields))
        + b"".join(_field(field_id, type_code, value) for field_id, type_code, value in fields)
    )


def _u64(value: int) -> bytes:
    return struct.pack(">Q", value)


def reference_confirmed_entry() -> dict:
    return {
        "intent_id": storage.anchor_intent_id(authority.PREPARED_DIGEST),
        "component_id": storage.ANCHOR_COMPONENT_ID,
        "intent_type": storage.ANCHOR_INTENT_TYPE,
        "payload_digest": storage.REFERENCE_ANCHOR_PAYLOAD_DIGEST.hex(),
        "provider_id": REFERENCE_PROVIDER_ID,
        "provider_generation": REFERENCE_PROVIDER_GENERATION,
        "predecessor_position": REFERENCE_PREDECESSOR_POSITION,
        "position": REFERENCE_POSITION,
        "request_id": REFERENCE_REQUEST_ID,
        "status": "CONFIRMED",
        "receipt_binding": REFERENCE_RECEIPT_BINDING,
    }


def stable_receipt_for_reference() -> str:
    return hashlib.sha256(_canon({
        "provider_id": REFERENCE_PROVIDER_ID,
        "generation": REFERENCE_PROVIDER_GENERATION,
        "position": REFERENCE_POSITION,
        "request_id": REFERENCE_REQUEST_ID,
    })).hexdigest()


def bridged_confirmed_canonical() -> bytes:
    v = authority.CONFIRMED_REFERENCE_VALUES
    fields = (
        (1, _DIGEST32, v[1]),
        (2, _DIGEST32, v[2]),
        (3, _DIGEST32, v[3]),
        (4, _UTF8, v[4].encode("utf-8")),
        (5, _U64, _u64(v[5])),
        (6, _DIGEST32, v[6]),
        (7, _DIGEST32, REFERENCE_CONFIRMED_HEAD_DIGEST),
        (8, _U64, _u64(REFERENCE_RESULTING_PROVENANCE_EPOCH)),
        (9, _BYTES, v[9]),
    )
    return _record(authority.CONFIRMED_DOMAIN, fields)


def validate_reference_bridge() -> bool:
    entry = reference_confirmed_entry()
    if storage.anchor_payload_digest(
        authority.PREPARED_DIGEST, authority.CONFIRMATION_NONCE
    ) != storage.REFERENCE_ANCHOR_PAYLOAD_DIGEST:
        raise AssertionError("anchor payload reference drift")
    expected_request = storage.ANCHOR_INTENT_PREFIX + authority.PREPARED_DIGEST.hex()
    if entry["intent_id"] != expected_request:
        raise AssertionError("anchor intent identity drift")
    if stable_receipt_for_reference() != REFERENCE_RECEIPT_BINDING:
        raise AssertionError("stable RECONCILE receipt drift")
    if storage.confirmed_head_digest(entry) != REFERENCE_CONFIRMED_HEAD_DIGEST:
        raise AssertionError("confirmed shared-anchor head digest drift")
    if authority.PREPARED_REFERENCE_VALUES[4] + 1 != REFERENCE_RESULTING_PROVENANCE_EPOCH:
        raise AssertionError("provenance epoch is not predecessor+1")
    if authority.CONFIRMED_REFERENCE_VALUES[8] != REFERENCE_RESULTING_PROVENANCE_EPOCH:
        raise AssertionError("historical CONFIRMED epoch vector drift")
    if authority.CONFIRMED_REFERENCE_VALUES[7] == REFERENCE_CONFIRMED_HEAD_DIGEST:
        raise AssertionError("historical synthetic head unexpectedly equals bridged head")
    confirmed = bridged_confirmed_canonical()
    if confirmed != BRIDGED_CONFIRMED_CANONICAL_BYTES:
        raise AssertionError("bridged CONFIRMED canonical bytes drift")
    if hashlib.sha256(confirmed).digest() != BRIDGED_CONFIRMED_DIGEST:
        raise AssertionError("bridged CONFIRMED digest drift")
    return True


if __name__ == "__main__":
    assert validate_reference_bridge()
