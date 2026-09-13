"""Independent byte-exact LAB-099 authority reference vectors.

Test-only. It does not import production provenance code or mutate SQLite. The precursor
bytes and dual HMAC reference keys stay unchanged. PREPARED/CONFIRMED vectors bind the
frozen LAB-099 precursor relation-definition digest selected by the durable V1 contract.
"""

from __future__ import annotations

import hashlib
import hmac
import struct

MAGIC = b"YTIMPRV1"
UTF8 = 0x01
BYTES = 0x02
U64 = 0x03
DIGEST32 = 0x04


def _field(field_id: int, type_code: int, value: bytes) -> bytes:
    return struct.pack(">HBI", field_id, type_code, len(value)) + value


def _u64(value: int) -> bytes:
    if type(value) is not int or not 0 <= value <= 2**64 - 1:
        raise ValueError("reference U64 must be an exact non-negative Python int")
    return struct.pack(">Q", value)


def _utf8(value: str) -> bytes:
    if type(value) is not str:
        raise TypeError("reference UTF8 must be exact str")
    return value.encode("utf-8", errors="strict")


def _record(domain: str, fields: tuple[tuple[int, int, bytes], ...]) -> bytes:
    domain_bytes = domain.encode("ascii")
    ids = tuple(field_id for field_id, _, _ in fields)
    if ids != tuple(sorted(ids)) or len(set(ids)) != len(fields):
        raise ValueError("reference fields must be unique and strictly ordered")
    return (
        MAGIC
        + struct.pack(">H", len(domain_bytes))
        + domain_bytes
        + struct.pack(">H", len(fields))
        + b"".join(_field(field_id, type_code, value) for field_id, type_code, value in fields)
    )


LOGICAL_DATABASE_IDENTITY_DIGEST = bytes(range(0x00, 0x20))
PARENT_CHAIN_LINK_DIGEST = bytes(range(0x20, 0x40))
PREDECESSOR_LAB092_COMPLETION_DIGEST = bytes(range(0x40, 0x60))
PREDECESSOR_PROVENANCE_HEAD_DIGEST = bytes(range(0x60, 0x80))
MIGRATION_NONCE = bytes(range(0x80, 0xA0))
FROZEN_RELATION_DEFINITION_DIGEST = bytes.fromhex(
    "696c54d1afdef52c05c120ce7d09a7a2eeb567daafb3a378b7dc4ca64f80e3bb"
)
RESULTING_PROVENANCE_HEAD_DIGEST = bytes(range(0xC0, 0xE0))
CONFIRMATION_NONCE = bytes(range(0xE0, 0x100))

PRECURSOR_DOMAIN = "ytim.provider-activation-reservation.v1"
PRECURSOR_CANONICAL_BYTES = bytes.fromhex(
    "5954494d5052563100277974696d2e70726f76696465722d61637469766174696f6e2d7265736572766174696f6e2e7631000b00010400000020000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f00020400000020202122232425262728292a2b2c2d2e2f303132333435363738393a3b3c3d3e3f0003030000000800000000000000070004010000000c67656e2d6f6c642d303030370005010000000c67656e2d6e65772d303030380006010000000e70726f76696465722d616c7068610007030000000800000000000000080008010000000e6b65792d616c7068612d30303038000903000000080000000000000029000a010000001b61637469766174652d67656e2d6e65772d303030382d61742d3431000b03000000080000000000000001"
)
PRECURSOR_DIGEST = bytes.fromhex(
    "499482ff043df31ef3f6ba56b5acf3d51bf7359ccf5aa2089435d443dc88c943"
)
PRECURSOR_REFERENCE_VALUES = {
    1: LOGICAL_DATABASE_IDENTITY_DIGEST,
    2: PARENT_CHAIN_LINK_DIGEST,
    3: 7,
    4: "gen-old-0007",
    5: "gen-new-0008",
    6: "provider-alpha",
    7: 8,
    8: "key-alpha-0008",
    9: 41,
    10: "activate-gen-new-0008-at-41",
    11: 1,
}
REFERENCE_PREDECESSOR_KEY = b"lab099-reference-old-key-v1"
REFERENCE_SUCCESSOR_KEY = b"lab099-reference-new-key-v1"
REFERENCE_AUTHENTICATOR_INPUT = PRECURSOR_CANONICAL_BYTES
REFERENCE_PREDECESSOR_HMAC_SHA256 = bytes.fromhex(
    "4017c0b29e154d048180379da7c49b74f16be4f101ffd1da4e835282f04d3a3d"
)
REFERENCE_SUCCESSOR_HMAC_SHA256 = bytes.fromhex(
    "62a99592f44dd9ca3493b61782de8b82206e0619226b23a6ca0913742cd1ec65"
)

PREPARED_DOMAIN = "ytim.lab099.activation-reservation-precursor-cutover-prepared.v1"
PREPARED_CANONICAL_BYTES = bytes.fromhex(
    "5954494d5052563100407974696d2e6c61623039392e61637469766174696f6e2d7265736572766174696f6e2d707265637572736f722d6375746f7665722d70726570617265642e7631000a00010400000020000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f00020400000020404142434445464748494a4b4c4d4e4f505152535455565758595a5b5c5d5e5f00030400000020606162636465666768696a6b6c6d6e6f707172737475767778797a7b7c7d7e7f0004030000000800000000000000070005010000002970726f76696465722d61637469766174696f6e2d7265736572766174696f6e2d707265637572736f7200060300000008000000000000000100070400000020696c54d1afdef52c05c120ce7d09a7a2eeb567daafb3a378b7dc4ca64f80e3bb000803000000080000000000000001000903000000080000000000000002000a0200000020808182838485868788898a8b8c8d8e8f909192939495969798999a9b9c9d9e9f"
)
PREPARED_DIGEST = bytes.fromhex("77ffdf5f657510a285d75e866d3418a85d1aeb0ca0f2c830617c850a5277b53e")
PREPARED_REFERENCE_VALUES = {
    1: LOGICAL_DATABASE_IDENTITY_DIGEST,
    2: PREDECESSOR_LAB092_COMPLETION_DIGEST,
    3: PREDECESSOR_PROVENANCE_HEAD_DIGEST,
    4: 7,
    5: "provider-activation-reservation-precursor",
    6: 1,
    7: FROZEN_RELATION_DEFINITION_DIGEST,
    8: 1,
    9: 2,
    10: MIGRATION_NONCE,
}

CONFIRMED_DOMAIN = "ytim.lab099.activation-reservation-precursor-cutover-confirmed.v1"
CONFIRMED_CANONICAL_BYTES = bytes.fromhex(
    "5954494d5052563100417974696d2e6c61623039392e61637469766174696f6e2d7265736572766174696f6e2d707265637572736f722d6375746f7665722d636f6e6669726d65642e7631000900010400000020000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f0002040000002077ffdf5f657510a285d75e866d3418a85d1aeb0ca0f2c830617c850a5277b53e00030400000020404142434445464748494a4b4c4d4e4f505152535455565758595a5b5c5d5e5f0004010000002970726f76696465722d61637469766174696f6e2d7265736572766174696f6e2d707265637572736f7200050300000008000000000000000100060400000020696c54d1afdef52c05c120ce7d09a7a2eeb567daafb3a378b7dc4ca64f80e3bb00070400000020c0c1c2c3c4c5c6c7c8c9cacbcccdcecfd0d1d2d3d4d5d6d7d8d9dadbdcdddedf00080300000008000000000000000800090200000020e0e1e2e3e4e5e6e7e8e9eaebecedeeeff0f1f2f3f4f5f6f7f8f9fafbfcfdfeff"
)
CONFIRMED_DIGEST = bytes.fromhex("caeb7b1cac2ff7b990ca54377fa2bd83b639a0af6e86478760de3ee27d5e6406")
CONFIRMED_REFERENCE_VALUES = {
    1: LOGICAL_DATABASE_IDENTITY_DIGEST,
    2: PREPARED_DIGEST,
    3: PREDECESSOR_LAB092_COMPLETION_DIGEST,
    4: "provider-activation-reservation-precursor",
    5: 1,
    6: FROZEN_RELATION_DEFINITION_DIGEST,
    7: RESULTING_PROVENANCE_HEAD_DIGEST,
    8: 8,
    9: CONFIRMATION_NONCE,
}


def _precursor_from_values() -> bytes:
    v = PRECURSOR_REFERENCE_VALUES
    return _record(PRECURSOR_DOMAIN, (
        (1, DIGEST32, v[1]), (2, DIGEST32, v[2]), (3, U64, _u64(v[3])),
        (4, UTF8, _utf8(v[4])), (5, UTF8, _utf8(v[5])), (6, UTF8, _utf8(v[6])),
        (7, U64, _u64(v[7])), (8, UTF8, _utf8(v[8])), (9, U64, _u64(v[9])),
        (10, UTF8, _utf8(v[10])), (11, U64, _u64(v[11])),
    ))


def _prepared_from_values() -> bytes:
    v = PREPARED_REFERENCE_VALUES
    return _record(PREPARED_DOMAIN, (
        (1, DIGEST32, v[1]), (2, DIGEST32, v[2]), (3, DIGEST32, v[3]),
        (4, U64, _u64(v[4])), (5, UTF8, _utf8(v[5])), (6, U64, _u64(v[6])),
        (7, DIGEST32, v[7]), (8, U64, _u64(v[8])), (9, U64, _u64(v[9])),
        (10, BYTES, v[10]),
    ))


def _confirmed_from_values() -> bytes:
    v = CONFIRMED_REFERENCE_VALUES
    return _record(CONFIRMED_DOMAIN, (
        (1, DIGEST32, v[1]), (2, DIGEST32, v[2]), (3, DIGEST32, v[3]),
        (4, UTF8, _utf8(v[4])), (5, U64, _u64(v[5])), (6, DIGEST32, v[6]),
        (7, DIGEST32, v[7]), (8, U64, _u64(v[8])), (9, BYTES, v[9]),
    ))


def validate_reference_vectors() -> bool:
    precursor = _precursor_from_values()
    if precursor != PRECURSOR_CANONICAL_BYTES:
        raise AssertionError("precursor canonical bytes drift")
    if hashlib.sha256(precursor).digest() != PRECURSOR_DIGEST:
        raise AssertionError("precursor digest drift")
    if hmac.new(REFERENCE_PREDECESSOR_KEY, precursor, hashlib.sha256).digest() != REFERENCE_PREDECESSOR_HMAC_SHA256:
        raise AssertionError("predecessor authenticator vector drift")
    if hmac.new(REFERENCE_SUCCESSOR_KEY, precursor, hashlib.sha256).digest() != REFERENCE_SUCCESSOR_HMAC_SHA256:
        raise AssertionError("successor authenticator vector drift")

    prepared_bytes = _prepared_from_values()
    if prepared_bytes != PREPARED_CANONICAL_BYTES:
        raise AssertionError("PREPARED canonical bytes drift")
    if hashlib.sha256(prepared_bytes).digest() != PREPARED_DIGEST:
        raise AssertionError("PREPARED digest drift")

    confirmed_bytes = _confirmed_from_values()
    if confirmed_bytes != CONFIRMED_CANONICAL_BYTES:
        raise AssertionError("CONFIRMED canonical bytes drift")
    if CONFIRMED_REFERENCE_VALUES[2] != PREPARED_DIGEST:
        raise AssertionError("CONFIRMED no longer binds exact PREPARED digest")
    if hashlib.sha256(confirmed_bytes).digest() != CONFIRMED_DIGEST:
        raise AssertionError("CONFIRMED digest drift")
    return True


if __name__ == "__main__":
    assert validate_reference_vectors()
