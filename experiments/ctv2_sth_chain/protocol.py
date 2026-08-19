from __future__ import annotations

import struct
from dataclasses import dataclass
from typing import Iterable

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

SIGNED_TREE_HEAD_V2 = 0x0104
ED25519 = 0x0807
MAX_U16 = (1 << 16) - 1
MIN_LOG_ID = 2
MAX_LOG_ID = 127


class STHError(ValueError): pass
class Truncated(STHError): pass
class TrailingData(STHError): pass
class WrongType(STHError): pass
class Malformed(STHError): pass
class ProfileError(STHError): pass
class SignatureError(STHError): pass
class BindingError(STHError): pass


@dataclass(frozen=True)
class Extension:
    extension_type: int
    extension_data: bytes


@dataclass(frozen=True)
class TreeHeadDataV2:
    timestamp: int
    tree_size: int
    root_hash: bytes
    sth_extensions: tuple[Extension, ...] = ()


@dataclass(frozen=True)
class SignedTreeHeadV2:
    log_id: bytes
    tree_head: TreeHeadDataV2
    signature: bytes


@dataclass(frozen=True)
class LogProfile:
    log_id: bytes
    hash_size: int
    signature_scheme: int
    public_key: bytes


@dataclass(frozen=True)
class AuthenticatedSTH:
    profile: LogProfile
    sth: SignedTreeHeadV2
    tree_head_bytes: bytes


class _Reader:
    def __init__(self, data: bytes):
        if not isinstance(data, bytes):
            raise Malformed("wire input must be bytes")
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


def _strict_u64(value: int, label: str) -> None:
    if type(value) is not int or not (0 <= value < 1 << 64):
        raise Malformed(f"{label} must be uint64")


def _strict_u16(value: int, label: str) -> None:
    if type(value) is not int or not (0 <= value <= MAX_U16):
        raise Malformed(f"{label} must be uint16")


def _validate_log_id(value: bytes) -> None:
    if not isinstance(value, bytes) or not (MIN_LOG_ID <= len(value) <= MAX_LOG_ID):
        raise Malformed("LogID length out of range")
    i = 0
    while i < len(value):
        if value[i] == 0x80:
            raise Malformed("non-minimal DER OID subidentifier")
        while value[i] & 0x80:
            i += 1
            if i >= len(value):
                raise Malformed("unterminated DER OID subidentifier")
        i += 1


def _encode_extensions(items: tuple[Extension, ...]) -> bytes:
    previous = -1
    body = bytearray()
    for item in items:
        _strict_u16(item.extension_type, "extension_type")
        if item.extension_type <= previous:
            raise Malformed("STH extensions must be strictly ordered and unique")
        previous = item.extension_type
        if not isinstance(item.extension_data, bytes) or len(item.extension_data) > MAX_U16:
            raise Malformed("extension_data length out of range")
        body += struct.pack("!HH", item.extension_type, len(item.extension_data))
        body += item.extension_data
    if len(body) > MAX_U16:
        raise Malformed("sth_extensions vector too large")
    return struct.pack("!H", len(body)) + body


def _decode_extensions(r: _Reader) -> tuple[Extension, ...]:
    vector_len = r.u16()
    end = r.pos + vector_len
    if end > len(r.data):
        raise Truncated("truncated sth_extensions")
    out: list[Extension] = []
    previous = -1
    while r.pos < end:
        if end - r.pos < 4:
            raise Truncated("truncated Extension header")
        typ = r.u16()
        size = r.u16()
        if typ <= previous:
            raise Malformed("STH extensions must be strictly ordered and unique")
        previous = typ
        if r.pos + size > end:
            raise Truncated("extension_data crosses vector boundary")
        out.append(Extension(typ, r.take(size)))
    if r.pos != end:
        raise Malformed("non-canonical extension vector boundary")
    return tuple(out)


def encode_tree_head(tree: TreeHeadDataV2, *, hash_size: int) -> bytes:
    _strict_u64(tree.timestamp, "timestamp")
    _strict_u64(tree.tree_size, "tree_size")
    if type(hash_size) is not int or not (32 <= hash_size <= 255):
        raise ProfileError("invalid HASH_SIZE")
    if not isinstance(tree.root_hash, bytes) or len(tree.root_hash) != hash_size:
        raise Malformed("root_hash length does not match HASH_SIZE")
    return (
        struct.pack("!QQB", tree.timestamp, tree.tree_size, len(tree.root_hash))
        + tree.root_hash
        + _encode_extensions(tree.sth_extensions)
    )


def decode_tree_head(r: _Reader, *, hash_size: int) -> tuple[TreeHeadDataV2, bytes]:
    start = r.pos
    timestamp, tree_size = r.u64(), r.u64()
    root_len = r.u8()
    if root_len != hash_size:
        raise Malformed("root_hash length does not match HASH_SIZE")
    root = r.take(root_len)
    extensions = _decode_extensions(r)
    return TreeHeadDataV2(timestamp, tree_size, root, extensions), r.data[start:r.pos]


def encode_signed_sth(item: SignedTreeHeadV2, *, hash_size: int) -> bytes:
    _validate_log_id(item.log_id)
    if not isinstance(item.signature, bytes) or not (1 <= len(item.signature) <= MAX_U16):
        raise Malformed("signature length out of range")
    tree = encode_tree_head(item.tree_head, hash_size=hash_size)
    return (
        struct.pack("!HB", SIGNED_TREE_HEAD_V2, len(item.log_id))
        + item.log_id
        + tree
        + struct.pack("!H", len(item.signature))
        + item.signature
    )


def decode_signed_sth(data: bytes, *, hash_size: int) -> tuple[SignedTreeHeadV2, bytes]:
    if type(hash_size) is not int or not (32 <= hash_size <= 255):
        raise ProfileError("invalid HASH_SIZE")
    r = _Reader(data)
    if r.u16() != SIGNED_TREE_HEAD_V2:
        raise WrongType("not signed_tree_head_v2")
    log_len = r.u8()
    if not (MIN_LOG_ID <= log_len <= MAX_LOG_ID):
        raise Malformed("LogID length out of range")
    log_id = r.take(log_len)
    _validate_log_id(log_id)
    tree, tree_bytes = decode_tree_head(r, hash_size=hash_size)
    sig_len = r.u16()
    if sig_len == 0:
        raise Malformed("signature must not be empty")
    signature = r.take(sig_len)
    if r.pos != len(data):
        raise TrailingData("trailing bytes after signed_tree_head_v2")
    return SignedTreeHeadV2(log_id, tree, signature), tree_bytes


def _validate_profile(profile: LogProfile) -> None:
    _validate_log_id(profile.log_id)
    if type(profile.hash_size) is not int or not (32 <= profile.hash_size <= 255):
        raise ProfileError("invalid HASH_SIZE")
    if profile.signature_scheme != ED25519:
        raise ProfileError("unsupported signature profile")
    if not isinstance(profile.public_key, bytes) or len(profile.public_key) != 32:
        raise ProfileError("Ed25519 public key must be 32 bytes")


def authenticate_sth(data: bytes, profile: LogProfile) -> AuthenticatedSTH:
    _validate_profile(profile)
    sth, tree_bytes = decode_signed_sth(data, hash_size=profile.hash_size)
    if sth.log_id != profile.log_id:
        raise BindingError("STH LogID does not match immutable log profile")
    try:
        Ed25519PublicKey.from_public_bytes(profile.public_key).verify(sth.signature, tree_bytes)
    except (InvalidSignature, ValueError) as exc:
        raise SignatureError("invalid STH signature") from exc
    return AuthenticatedSTH(profile, sth, tree_bytes)


def sign_sth(tree: TreeHeadDataV2, *, log_id: bytes, private_key: Ed25519PrivateKey, hash_size: int) -> bytes:
    """Reference producer helper used only by deterministic experiments."""
    tree_bytes = encode_tree_head(tree, hash_size=hash_size)
    signature = private_key.sign(tree_bytes)
    return encode_signed_sth(SignedTreeHeadV2(log_id, tree, signature), hash_size=hash_size)


def verify_authenticated_growth(
    old_sth_wire: bytes,
    new_sth_wire: bytes,
    consistency_wire: bytes,
    profile: LogProfile,
) -> bool:
    old = authenticate_sth(old_sth_wire, profile)
    new = authenticate_sth(new_sth_wire, profile)
    if new.sth.tree_head.timestamp <= old.sth.tree_head.timestamp:
        raise BindingError("new STH timestamp must be strictly newer")
    from experiments.ctv2_consistency_wire.protocol import WitnessCheckpoint, verify_bound_growth
    old_cp = WitnessCheckpoint(profile.log_id, old.sth.tree_head.tree_size, old.sth.tree_head.root_hash)
    new_cp = WitnessCheckpoint(profile.log_id, new.sth.tree_head.tree_size, new.sth.tree_head.root_hash)
    return verify_bound_growth(
        consistency_wire, old_cp, new_cp, hash_size=profile.hash_size
    )


def unsafe_trust_parsed_fields(data: bytes, *, hash_size: int) -> SignedTreeHeadV2:
    """Deliberately unsafe: strict parsing without cryptographic authentication."""
    sth, _ = decode_signed_sth(data, hash_size=hash_size)
    return sth
