from __future__ import annotations

import struct
from dataclasses import dataclass
from typing import Callable, Iterable

CONSISTENCY_PROOF_V2 = 0x0105
MAX_VECTOR = (1 << 16) - 1
MIN_LOG_ID = 2
MAX_LOG_ID = 127
MIN_NODE_HASH = 32
MAX_NODE_HASH = 255


class WireError(ValueError): pass
class Truncated(WireError): pass
class TrailingData(WireError): pass
class WrongType(WireError): pass
class MalformedVector(WireError): pass
class BindingError(WireError): pass


@dataclass(frozen=True)
class ConsistencyProofV2:
    log_id: bytes
    tree_size_1: int
    tree_size_2: int
    consistency_path: tuple[bytes, ...]


@dataclass(frozen=True)
class WitnessCheckpoint:
    log_id: bytes
    tree_size: int
    root_hash: bytes


def _validate_log_id(value: bytes) -> None:
    if not isinstance(value, bytes) or not (MIN_LOG_ID <= len(value) <= MAX_LOG_ID):
        raise MalformedVector("LogID length out of range")
    # RFC 9162 LogID is DER OBJECT IDENTIFIER value bytes (tag/length excluded).
    # DER requires minimal base-128 subidentifier encoding: no leading 0x80 group,
    # and every continuation chain must terminate.
    i = 0  # first DER subidentifier combines the first two OID arcs
    while i < len(value):
        if value[i] == 0x80:
            raise MalformedVector("non-minimal DER OID subidentifier")
        while value[i] & 0x80:
            i += 1
            if i >= len(value):
                raise MalformedVector("unterminated DER OID subidentifier")
        i += 1


def _u64(value: int) -> bytes:
    if type(value) is not int or not (0 <= value < 1 << 64):
        raise WireError("uint64 out of range")
    return struct.pack("!Q", value)


def _opaque8(value: bytes, lo: int, hi: int, label: str) -> bytes:
    if not isinstance(value, bytes) or not (lo <= len(value) <= hi):
        raise MalformedVector(f"{label} length out of range")
    return bytes([len(value)]) + value


def encode_consistency_proof(item: ConsistencyProofV2) -> bytes:
    _validate_log_id(item.log_id)
    log = _opaque8(item.log_id, MIN_LOG_ID, MAX_LOG_ID, "LogID")
    path = bytearray()
    for node in item.consistency_path:
        path += _opaque8(node, MIN_NODE_HASH, MAX_NODE_HASH, "NodeHash")
    if len(path) > MAX_VECTOR:
        raise MalformedVector("consistency_path exceeds 2^16-1 bytes")
    return (
        struct.pack("!H", CONSISTENCY_PROOF_V2)
        + log
        + _u64(item.tree_size_1)
        + _u64(item.tree_size_2)
        + struct.pack("!H", len(path))
        + bytes(path)
    )


class _Reader:
    def __init__(self, data: bytes):
        if not isinstance(data, bytes):
            raise WireError("wire input must be bytes")
        self.data = data
        self.pos = 0

    def take(self, n: int) -> bytes:
        end = self.pos + n
        if end > len(self.data):
            raise Truncated("truncated field")
        out = self.data[self.pos:end]
        self.pos = end
        return out

    def u8(self) -> int: return self.take(1)[0]
    def u16(self) -> int: return struct.unpack("!H", self.take(2))[0]
    def u64(self) -> int: return struct.unpack("!Q", self.take(8))[0]


def decode_consistency_proof(data: bytes, *, hash_size: int) -> ConsistencyProofV2:
    if type(hash_size) is not int or not (MIN_NODE_HASH <= hash_size <= MAX_NODE_HASH):
        raise WireError("invalid HASH_SIZE")
    r = _Reader(data)
    if r.u16() != CONSISTENCY_PROOF_V2:
        raise WrongType("not consistency_proof_v2")
    log_len = r.u8()
    if not (MIN_LOG_ID <= log_len <= MAX_LOG_ID):
        raise MalformedVector("LogID length out of range")
    log_id = r.take(log_len)
    _validate_log_id(log_id)
    first, second = r.u64(), r.u64()
    vector_len = r.u16()
    vector_end = r.pos + vector_len
    if vector_end > len(data):
        raise Truncated("truncated consistency_path")
    nodes = []
    while r.pos < vector_end:
        node_len = r.u8()
        if node_len != hash_size:
            raise MalformedVector("NodeHash length does not match HASH_SIZE")
        if r.pos + node_len > vector_end:
            raise Truncated("NodeHash crosses vector boundary")
        nodes.append(r.take(node_len))
    if r.pos != vector_end:
        raise MalformedVector("non-canonical vector boundary")
    if r.pos != len(data):
        raise TrailingData("trailing bytes after TransItem")
    return ConsistencyProofV2(log_id, first, second, tuple(nodes))


def verify_bound_growth(
    wire: bytes,
    old: WitnessCheckpoint,
    new: WitnessCheckpoint,
    *,
    hash_size: int,
    merkle_verifier: Callable[[int, int, bytes, bytes, Iterable[bytes]], bool] | None = None,
) -> bool:
    item = decode_consistency_proof(wire, hash_size=hash_size)
    if old.log_id != new.log_id or item.log_id != old.log_id:
        raise BindingError("LogID does not bind both checkpoints")
    if item.tree_size_1 != old.tree_size or item.tree_size_2 != new.tree_size:
        raise BindingError("proof tree sizes do not bind checkpoints")
    if merkle_verifier is None:
        from experiments.rfc9162_consistency.protocol import verify_consistency
        merkle_verifier = verify_consistency
    return merkle_verifier(
        old.tree_size, new.tree_size, old.root_hash, new.root_hash, item.consistency_path
    )


def unsafe_decode_prefix_only(data: bytes, *, hash_size: int) -> ConsistencyProofV2:
    """Deliberately unsafe: ignores bytes after the declared proof vector."""
    r = _Reader(data)
    if r.u16() != CONSISTENCY_PROOF_V2:
        raise WrongType()
    log_id = r.take(r.u8())
    first, second = r.u64(), r.u64()
    vector_len = r.u16()
    end = r.pos + vector_len
    nodes = []
    while r.pos < end:
        nodes.append(r.take(r.u8()))
    return ConsistencyProofV2(log_id, first, second, tuple(nodes))
