from __future__ import annotations

import hashlib
import struct
from dataclasses import dataclass
from enum import Enum

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

X509_ENTRY_V2 = 0x0100
PRECERT_ENTRY_V2 = 0x0101
X509_SCT_V2 = 0x0102
PRECERT_SCT_V2 = 0x0103
ED25519 = 0x0807
MAX_U16 = (1 << 16) - 1
MAX_U24 = (1 << 24) - 1
MIN_LOG_ID = 2
MAX_LOG_ID = 127


class SCTError(ValueError): pass
class Truncated(SCTError): pass
class TrailingData(SCTError): pass
class WrongType(SCTError): pass
class Malformed(SCTError): pass
class BindingError(SCTError): pass
class SignatureError(SCTError): pass
class TemporalBindingError(SCTError): pass
class SnapshotError(SCTError): pass


@dataclass(frozen=True)
class Extension:
    extension_type: int
    extension_data: bytes


@dataclass(frozen=True)
class SignedCertificateTimestampV2:
    versioned_type: int
    log_id: bytes
    timestamp: int
    sct_extensions: tuple[Extension, ...]
    signature: bytes


@dataclass(frozen=True)
class ExactLeafBinding:
    versioned_type: int
    timestamp: int
    issuer_key_hash: bytes
    tbs_certificate: bytes
    sct_extensions: tuple[Extension, ...]


@dataclass(frozen=True)
class AuthenticatedSCT:
    sct: SignedCertificateTimestampV2
    leaf: ExactLeafBinding
    leaf_bytes: bytes


class PromiseStatus(str, Enum):
    FULFILLED = "FULFILLED"
    NOT_YET_AUDITABLE = "NOT_YET_AUDITABLE"
    INCONCLUSIVE_AFTER_DEADLINE = "INCONCLUSIVE_AFTER_DEADLINE"
    MMD_VIOLATION = "MMD_VIOLATION"


@dataclass(frozen=True)
class PromiseAudit:
    status: PromiseStatus
    sct_timestamp: int
    mmd_deadline: int
    observed_sth_timestamp: int
    evidence: str


class _Reader:
    def __init__(self, data: bytes):
        if not isinstance(data, bytes):
            raise Malformed("wire input must be bytes")
        self.data = data
        self.pos = 0

    def take(self, n: int) -> bytes:
        if type(n) is not int or n < 0 or self.pos + n > len(self.data):
            raise Truncated("truncated field")
        out = self.data[self.pos:self.pos + n]
        self.pos += n
        return out

    def u8(self) -> int: return self.take(1)[0]
    def u16(self) -> int: return struct.unpack("!H", self.take(2))[0]
    def u24(self) -> int:
        b = self.take(3)
        return (b[0] << 16) | (b[1] << 8) | b[2]
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
            raise Malformed("extensions must be strictly ordered and unique")
        previous = item.extension_type
        if not isinstance(item.extension_data, bytes) or len(item.extension_data) > MAX_U16:
            raise Malformed("extension_data length out of range")
        body += struct.pack("!HH", item.extension_type, len(item.extension_data))
        body += item.extension_data
    if len(body) > MAX_U16:
        raise Malformed("extension vector too large")
    return struct.pack("!H", len(body)) + body


def _decode_extensions(r: _Reader) -> tuple[Extension, ...]:
    vector_len = r.u16()
    end = r.pos + vector_len
    if end > len(r.data):
        raise Truncated("truncated extensions")
    out: list[Extension] = []
    previous = -1
    while r.pos < end:
        if end - r.pos < 4:
            raise Truncated("truncated Extension header")
        typ, size = r.u16(), r.u16()
        if typ <= previous:
            raise Malformed("extensions must be strictly ordered and unique")
        previous = typ
        if r.pos + size > end:
            raise Truncated("extension_data crosses vector boundary")
        out.append(Extension(typ, r.take(size)))
    if r.pos != end:
        raise Malformed("non-canonical extension vector boundary")
    return tuple(out)


def encode_sct(item: SignedCertificateTimestampV2) -> bytes:
    if item.versioned_type not in {X509_SCT_V2, PRECERT_SCT_V2}:
        raise WrongType("SCT must be x509_sct_v2 or precert_sct_v2")
    _validate_log_id(item.log_id)
    _strict_u64(item.timestamp, "timestamp")
    if not isinstance(item.signature, bytes) or not (1 <= len(item.signature) <= MAX_U16):
        raise Malformed("signature length out of range")
    return (
        struct.pack("!HB", item.versioned_type, len(item.log_id))
        + item.log_id
        + struct.pack("!Q", item.timestamp)
        + _encode_extensions(item.sct_extensions)
        + struct.pack("!H", len(item.signature))
        + item.signature
    )


def decode_sct(data: bytes) -> SignedCertificateTimestampV2:
    r = _Reader(data)
    typ = r.u16()
    if typ not in {X509_SCT_V2, PRECERT_SCT_V2}:
        raise WrongType("not an SCT v2 TransItem")
    log_len = r.u8()
    if not (MIN_LOG_ID <= log_len <= MAX_LOG_ID):
        raise Malformed("LogID length out of range")
    log_id = r.take(log_len)
    _validate_log_id(log_id)
    timestamp = r.u64()
    extensions = _decode_extensions(r)
    sig_len = r.u16()
    if sig_len == 0:
        raise Malformed("signature must not be empty")
    signature = r.take(sig_len)
    if r.pos != len(data):
        raise TrailingData("trailing bytes after SCT")
    return SignedCertificateTimestampV2(typ, log_id, timestamp, extensions, signature)


def encode_leaf(
    *,
    versioned_type: int,
    timestamp: int,
    issuer_key_hash: bytes,
    tbs_certificate: bytes,
    sct_extensions: tuple[Extension, ...] = (),
) -> bytes:
    if versioned_type not in {X509_ENTRY_V2, PRECERT_ENTRY_V2}:
        raise WrongType("leaf must be x509_entry_v2 or precert_entry_v2")
    _strict_u64(timestamp, "timestamp")
    if not isinstance(issuer_key_hash, bytes) or not (32 <= len(issuer_key_hash) <= 255):
        raise Malformed("issuer_key_hash length out of range")
    if not isinstance(tbs_certificate, bytes) or not (1 <= len(tbs_certificate) <= MAX_U24):
        raise Malformed("TBSCertificate length out of range")
    tbs_len = len(tbs_certificate)
    return (
        struct.pack("!HQB", versioned_type, timestamp, len(issuer_key_hash))
        + issuer_key_hash
        + bytes([(tbs_len >> 16) & 0xFF, (tbs_len >> 8) & 0xFF, tbs_len & 0xFF])
        + tbs_certificate
        + _encode_extensions(sct_extensions)
    )


def decode_exact_leaf(data: bytes) -> ExactLeafBinding:
    r = _Reader(data)
    typ = r.u16()
    if typ not in {X509_ENTRY_V2, PRECERT_ENTRY_V2}:
        raise WrongType("leaf must be x509_entry_v2 or precert_entry_v2")
    timestamp = r.u64()
    issuer_len = r.u8()
    if not (32 <= issuer_len <= 255):
        raise Malformed("issuer_key_hash length out of range")
    issuer = r.take(issuer_len)
    tbs_len = r.u24()
    if tbs_len == 0:
        raise Malformed("TBSCertificate must not be empty")
    tbs = r.take(tbs_len)
    extensions = _decode_extensions(r)
    if r.pos != len(data):
        raise TrailingData("trailing bytes after leaf TransItem")
    return ExactLeafBinding(typ, timestamp, issuer, tbs, extensions)


def _validate_profile(profile) -> None:
    _validate_log_id(profile.log_id)
    if getattr(profile, "signature_scheme", None) != ED25519:
        raise BindingError("reference SCT verifier requires Ed25519 log profile")
    if not isinstance(profile.public_key, bytes) or len(profile.public_key) != 32:
        raise BindingError("invalid Ed25519 log public key")


def _matching_leaf_type(sct_type: int) -> int:
    if sct_type == X509_SCT_V2:
        return X509_ENTRY_V2
    if sct_type == PRECERT_SCT_V2:
        return PRECERT_ENTRY_V2
    raise WrongType("unsupported SCT type")


def authenticate_sct_to_exact_leaf(sct_wire: bytes, leaf_wire: bytes, profile) -> AuthenticatedSCT:
    _validate_profile(profile)
    sct = decode_sct(sct_wire)
    leaf = decode_exact_leaf(leaf_wire)
    if sct.log_id != profile.log_id:
        raise BindingError("SCT LogID does not match immutable log profile")
    if leaf.versioned_type != _matching_leaf_type(sct.versioned_type):
        raise BindingError("SCT type does not match exact leaf type")
    if leaf.timestamp != sct.timestamp:
        raise BindingError("SCT timestamp does not match exact leaf timestamp")
    if leaf.sct_extensions != sct.sct_extensions:
        raise BindingError("SCT extensions do not match exact leaf extensions")
    try:
        Ed25519PublicKey.from_public_bytes(profile.public_key).verify(sct.signature, leaf_wire)
    except (InvalidSignature, ValueError) as exc:
        raise SignatureError("SCT signature does not authenticate exact leaf bytes") from exc
    return AuthenticatedSCT(sct, leaf, leaf_wire)


def sign_sct_for_leaf(leaf_wire: bytes, *, log_id: bytes, private_key: Ed25519PrivateKey) -> bytes:
    """Deterministic experiment producer; the verifier never trusts producer-side reconstruction."""
    leaf = decode_exact_leaf(leaf_wire)
    sct_type = X509_SCT_V2 if leaf.versioned_type == X509_ENTRY_V2 else PRECERT_SCT_V2
    signature = private_key.sign(leaf_wire)
    return encode_sct(SignedCertificateTimestampV2(
        sct_type, log_id, leaf.timestamp, leaf.sct_extensions, signature
    ))


def _deadline(timestamp: int, mmd_ms: int) -> int:
    _strict_u64(timestamp, "SCT timestamp")
    if type(mmd_ms) is not int or mmd_ms < 0:
        raise Malformed("MMD must be a non-negative integer number of milliseconds")
    deadline = timestamp + mmd_ms
    if deadline >= 1 << 64:
        raise Malformed("SCT timestamp + MMD overflows uint64")
    return deadline


def _snapshot_root_exact(leaves: tuple[bytes, ...]) -> bytes:
    from experiments.rfc9162_consistency.protocol import merkle_tree_hash
    # A complete CT snapshot is semantic evidence, not merely an arbitrary list of hash preimages.
    # Fail closed if any presented tree entry is not a strict x509/precert v2 leaf.
    for item in leaves:
        decode_exact_leaf(item)
    return merkle_tree_hash(leaves)


def audit_sct_promise(
    *,
    sct_wire: bytes,
    leaf_wire: bytes,
    sth_wire: bytes,
    profile,
    mmd_ms: int,
    inclusion_wire: bytes | None = None,
    complete_snapshot_leaves: tuple[bytes, ...] | None = None,
) -> PromiseAudit:
    """Audit an SCT promise without inventing non-membership evidence.

    Inclusion proof (or an authenticated complete snapshot containing the leaf) establishes
    fulfillment. A post-deadline STH alone is inconclusive: Merkle trees do not provide
    non-membership proofs. MMD_VIOLATION is returned only when a complete snapshot is
    authenticated to the chosen post-deadline STH root and the exact leaf is absent.
    """
    auth_sct = authenticate_sct_to_exact_leaf(sct_wire, leaf_wire, profile)
    from experiments.ctv2_sth_chain.protocol import authenticate_sth
    auth_sth = authenticate_sth(sth_wire, profile)
    sth_ts = auth_sth.sth.tree_head.timestamp
    if sth_ts < auth_sct.sct.timestamp:
        raise TemporalBindingError("selected STH predates the SCT")
    deadline = _deadline(auth_sct.sct.timestamp, mmd_ms)

    if inclusion_wire is not None:
        from experiments.ctv2_inclusion_chain.protocol import verify_authenticated_inclusion
        verify_authenticated_inclusion(leaf_wire, sth_wire, inclusion_wire, profile)
        return PromiseAudit(
            PromiseStatus.FULFILLED, auth_sct.sct.timestamp, deadline, sth_ts,
            "exact leaf has authenticated inclusion under selected STH",
        )

    if complete_snapshot_leaves is not None:
        if not isinstance(complete_snapshot_leaves, tuple) or any(not isinstance(x, bytes) for x in complete_snapshot_leaves):
            raise SnapshotError("complete snapshot must be a tuple of exact leaf bytes")
        if len(complete_snapshot_leaves) != auth_sth.sth.tree_head.tree_size:
            raise SnapshotError("snapshot leaf count does not match authenticated STH tree_size")
        root = _snapshot_root_exact(complete_snapshot_leaves)
        if root != auth_sth.sth.tree_head.root_hash:
            raise SnapshotError("complete snapshot does not reconstruct authenticated STH root")
        if leaf_wire in complete_snapshot_leaves:
            return PromiseAudit(
                PromiseStatus.FULFILLED, auth_sct.sct.timestamp, deadline, sth_ts,
                "authenticated complete snapshot contains exact leaf",
            )
        if sth_ts >= deadline:
            return PromiseAudit(
                PromiseStatus.MMD_VIOLATION, auth_sct.sct.timestamp, deadline, sth_ts,
                "authenticated complete post-deadline snapshot proves exact leaf absent",
            )
        return PromiseAudit(
            PromiseStatus.NOT_YET_AUDITABLE, auth_sct.sct.timestamp, deadline, sth_ts,
            "authenticated complete snapshot predates MMD deadline and exact leaf is not yet present",
        )

    if sth_ts < deadline:
        return PromiseAudit(
            PromiseStatus.NOT_YET_AUDITABLE, auth_sct.sct.timestamp, deadline, sth_ts,
            "selected authenticated STH predates MMD deadline and no inclusion evidence was supplied",
        )
    return PromiseAudit(
        PromiseStatus.INCONCLUSIVE_AFTER_DEADLINE, auth_sct.sct.timestamp, deadline, sth_ts,
        "post-deadline STH without inclusion or authenticated complete snapshot cannot prove non-membership",
    )


def unsafe_accept_inclusion_without_sct_binding(
    *, leaf_wire: bytes, sth_wire: bytes, inclusion_wire: bytes, profile
) -> bool:
    """Deliberately unsafe: proves inclusion but never proves the presented SCT promised this leaf."""
    from experiments.ctv2_inclusion_chain.protocol import verify_authenticated_inclusion
    return verify_authenticated_inclusion(leaf_wire, sth_wire, inclusion_wire, profile)
