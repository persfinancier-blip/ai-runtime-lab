from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Iterable, Sequence

HASH_SIZE = hashlib.sha256().digest_size


class ProofError(ValueError):
    pass


class SizeError(ProofError):
    pass


class MalformedProof(ProofError):
    pass


class RootMismatch(ProofError):
    pass


def _sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def empty_root() -> bytes:
    return _sha256(b"")


def leaf_hash(data: bytes) -> bytes:
    return _sha256(b"\x00" + data)


def node_hash(left: bytes, right: bytes) -> bytes:
    _require_hash(left)
    _require_hash(right)
    return _sha256(b"\x01" + left + right)


def _require_hash(value: bytes) -> None:
    if not isinstance(value, bytes) or len(value) != HASH_SIZE:
        raise MalformedProof(f"expected {HASH_SIZE}-byte hash")


def _largest_power_of_two_less_than(n: int) -> int:
    if n <= 1:
        raise SizeError("n must be > 1")
    return 1 << ((n - 1).bit_length() - 1)


def merkle_tree_hash(entries: Sequence[bytes]) -> bytes:
    n = len(entries)
    if n == 0:
        return empty_root()
    if n == 1:
        return leaf_hash(entries[0])
    k = _largest_power_of_two_less_than(n)
    return node_hash(merkle_tree_hash(entries[:k]), merkle_tree_hash(entries[k:]))


def consistency_proof(first: int, entries: Sequence[bytes]) -> tuple[bytes, ...]:
    """RFC 9162 PROOF(first, D_n), for 0 < first < n."""
    second = len(entries)
    if first <= 0 or first >= second:
        raise SizeError("generation requires 0 < first < second")
    return tuple(_subproof(first, entries, True))


def _subproof(m: int, entries: Sequence[bytes], complete: bool) -> list[bytes]:
    n = len(entries)
    if m <= 0 or m > n:
        raise SizeError("invalid subproof range")
    if m == n:
        return [] if complete else [merkle_tree_hash(entries)]
    k = _largest_power_of_two_less_than(n)
    if m <= k:
        return _subproof(m, entries[:k], complete) + [merkle_tree_hash(entries[k:])]
    return _subproof(m - k, entries[k:], False) + [merkle_tree_hash(entries[:k])]


def verify_consistency(
    first: int,
    second: int,
    first_root: bytes,
    second_root: bytes,
    proof: Iterable[bytes],
) -> bool:
    """Fail-closed RFC 9162 consistency verification plus equal-size semantics.

    RFC 9162 defines the compact algorithm for 0 < first < second. For equal
    sizes this wrapper accepts iff the proof is empty and roots are identical.
    A proof from the empty tree is intentionally rejected as meaningless, which
    matches the transparency-dev/merkle reference implementation.
    """
    _require_hash(first_root)
    _require_hash(second_root)
    path = tuple(proof)
    for item in path:
        _require_hash(item)

    if type(first) is not int or type(second) is not int:
        raise SizeError("tree sizes must be integers, not booleans or coercible values")
    if first < 0 or second < 0:
        raise SizeError("tree sizes must be non-negative")
    if first == 0:
        raise SizeError("consistency proof from empty tree is meaningless")
    if second < first:
        raise SizeError("first tree cannot be larger than second")
    if first == second:
        if path:
            raise MalformedProof("equal-size proof must be empty")
        if first_root != second_root:
            raise RootMismatch("equal-size roots differ")
        return True
    if not path:
        raise MalformedProof("non-equal trees require a non-empty proof")
    max_nodes = (second - 1).bit_length() + 1
    if len(path) > max_nodes:
        raise MalformedProof("proof exceeds RFC 9162 logarithmic node bound")

    work = list(path)
    if first & (first - 1) == 0:
        work.insert(0, first_root)

    fn = first - 1
    sn = second - 1
    if fn & 1:
        while fn & 1:
            fn >>= 1
            sn >>= 1

    fr = work[0]
    sr = work[0]
    for c in work[1:]:
        if sn == 0:
            raise MalformedProof("proof contains extra node")
        if (fn & 1) or fn == sn:
            fr = node_hash(c, fr)
            sr = node_hash(c, sr)
            if not (fn & 1):
                while fn != 0 and not (fn & 1):
                    fn >>= 1
                    sn >>= 1
        else:
            sr = node_hash(sr, c)
        fn >>= 1
        sn >>= 1

    if sn != 0:
        raise MalformedProof("proof ended before reaching second root")
    if fr != first_root:
        raise RootMismatch("proof does not reconstruct first root")
    if sr != second_root:
        raise RootMismatch("proof does not reconstruct second root")
    return True


def unsafe_verify_new_root_only(
    first: int,
    second: int,
    claimed_first_root: bytes,
    second_root: bytes,
    proof: Iterable[bytes],
) -> bool:
    """Deliberately unsafe seed: reconstructs the new root but ignores old root.

    For non-power-of-two |first|, the proof contains its own seed. Ignoring the
    reconstructed old root lets an attacker pair a valid growth proof with an
    unrelated claimed old checkpoint.
    """
    _require_hash(claimed_first_root)
    _require_hash(second_root)
    path = tuple(proof)
    if not (0 < first < second) or not path:
        return False
    for item in path:
        _require_hash(item)
    work = list(path)
    if first & (first - 1) == 0:
        work.insert(0, claimed_first_root)
    fn, sn = first - 1, second - 1
    if fn & 1:
        while fn & 1:
            fn >>= 1
            sn >>= 1
    fr = sr = work[0]
    for c in work[1:]:
        if sn == 0:
            return False
        if (fn & 1) or fn == sn:
            fr = node_hash(c, fr)
            sr = node_hash(c, sr)
            if not (fn & 1):
                while fn != 0 and not (fn & 1):
                    fn >>= 1
                    sn >>= 1
        else:
            sr = node_hash(sr, c)
        fn >>= 1
        sn >>= 1
    return sn == 0 and sr == second_root


@dataclass(frozen=True)
class Checkpoint:
    size: int
    root: bytes

    def __post_init__(self) -> None:
        if self.size < 0:
            raise SizeError("checkpoint size must be non-negative")
        _require_hash(self.root)


def verify_checkpoint_growth(old: Checkpoint, new: Checkpoint, proof: Iterable[bytes]) -> bool:
    """LAB-040 integration boundary: consumes only heads + compact proof."""
    return verify_consistency(old.size, new.size, old.root, new.root, proof)
