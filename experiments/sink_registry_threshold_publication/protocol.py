from __future__ import annotations

import hashlib
import hmac
import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path

from experiments.anchor_threshold_root.protocol import RootState, Signature, key_id, root_descriptor
from experiments.sink_registry_binding.protocol import RegistryEntry, canon


class ThresholdPublicationError(RuntimeError):
    pass


class AuthorityMismatch(ThresholdPublicationError):
    pass


class InvalidSignatureSet(ThresholdPublicationError):
    pass


class ProofSubstitution(ThresholdPublicationError):
    pass


def digest_obj(obj) -> str:
    return hashlib.sha256(canon(obj)).hexdigest()


def authority_id(root: RootState) -> str:
    root.validate()
    return digest_obj(root_descriptor(root))


def threshold_issuer_id(root: RootState) -> str:
    return f"threshold:{authority_id(root)}"


def publication_entry(
    root: RootState,
    *,
    sink_id: str,
    generation: int,
    adapter_digest: str,
    endpoint_origin: str,
    operation_profile: str,
    predecessor_entry_digest: str | None = None,
) -> RegistryEntry:
    root.validate()
    entry = RegistryEntry(
        sink_id,
        generation,
        adapter_digest,
        endpoint_origin,
        operation_profile,
        predecessor_entry_digest,
        threshold_issuer_id(root),
        root.version,
        "",
    )
    entry.validate_shape()
    return entry


def sign_publication(entry: RegistryEntry, signer_key: bytes) -> Signature:
    return Signature(
        key_id(signer_key),
        hmac.new(signer_key, canon(entry.unsigned), hashlib.sha256).hexdigest(),
    )


@dataclass(frozen=True)
class ThresholdProof:
    authority_id: str
    authority_version: int
    signatures: tuple[Signature, ...]

    @property
    def canonical(self):
        return {
            "authority_id": self.authority_id,
            "authority_version": self.authority_version,
            "signatures": [
                {"signer_id": s.signer_id, "signature": s.signature}
                for s in sorted(self.signatures, key=lambda item: item.signer_id)
            ],
        }

    @property
    def proof_digest(self) -> str:
        return digest_obj(self.canonical)


@dataclass(frozen=True)
class ThresholdEnvelope:
    entry: RegistryEntry
    proof: ThresholdProof

    @property
    def entry_digest(self) -> str:
        return self.entry.entry_digest


def _strict_verify_signatures(
    root: RootState, payload: dict, signatures: tuple[Signature, ...]
) -> tuple[str, ...]:
    root.validate()
    seen = set()
    valid = []
    for item in signatures:
        if item.signer_id in seen:
            raise InvalidSignatureSet("duplicate signer identity")
        seen.add(item.signer_id)
        if item.signer_id in root.revoked:
            raise InvalidSignatureSet("revoked signer included")
        key_hex = root.keys.get(item.signer_id)
        if key_hex is None:
            raise InvalidSignatureSet("unknown signer included")
        if (
            not isinstance(item.signature, str)
            or len(item.signature) != 64
            or any(c not in "0123456789abcdef" for c in item.signature)
        ):
            raise InvalidSignatureSet("malformed signature")
        expected = hmac.new(
            bytes.fromhex(key_hex), canon(payload), hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(expected, item.signature):
            raise InvalidSignatureSet("invalid signer signature")
        valid.append(item.signer_id)
    if len(valid) < root.threshold:
        raise InvalidSignatureSet(
            f"threshold not met: valid={len(valid)} threshold={root.threshold}"
        )
    return tuple(sorted(valid))


def make_envelope(
    root: RootState, entry: RegistryEntry, signatures: tuple[Signature, ...]
) -> ThresholdEnvelope:
    proof = ThresholdProof(authority_id(root), root.version, tuple(signatures))
    signed_entry = RegistryEntry(**entry.unsigned, signature=proof.proof_digest)
    envelope = ThresholdEnvelope(signed_entry, proof)
    verify_envelope(root, envelope)
    return envelope


def verify_envelope(root: RootState, envelope: ThresholdEnvelope) -> ThresholdEnvelope:
    root.validate()
    entry = envelope.entry
    entry.validate_shape()
    proof = envelope.proof
    expected_authority = authority_id(root)
    if entry.issuer_id != f"threshold:{expected_authority}":
        raise AuthorityMismatch("entry is not bound to exact authority identity")
    if entry.issuer_generation != root.version:
        raise AuthorityMismatch("entry authority version mismatch")
    if proof.authority_id != expected_authority or proof.authority_version != root.version:
        raise AuthorityMismatch("proof authority mismatch")
    if entry.signature != proof.proof_digest:
        raise ProofSubstitution("entry/proof digest mismatch")
    _strict_verify_signatures(root, entry.unsigned, proof.signatures)
    return envelope


class ThresholdProofStore:
    """Reference historical proof store for the isolated LAB-077 slice."""

    def __init__(self, path: str | Path):
        self.path = str(path)
        q = sqlite3.connect(self.path)
        q.execute(
            """
            CREATE TABLE IF NOT EXISTS threshold_publications(
              entry_digest TEXT PRIMARY KEY,
              entry_json TEXT NOT NULL,
              proof_json TEXT NOT NULL,
              root_json TEXT NOT NULL
            )
            """
        )
        q.commit()
        q.close()

    def accept(self, root: RootState, envelope: ThresholdEnvelope) -> str:
        verify_envelope(root, envelope)
        entry_json = json.dumps(
            {**envelope.entry.unsigned, "signature": envelope.entry.signature},
            sort_keys=True,
            separators=(",", ":"),
        )
        proof_json = json.dumps(
            envelope.proof.canonical, sort_keys=True, separators=(",", ":")
        )
        root_json = json.dumps(
            root_descriptor(root), sort_keys=True, separators=(",", ":")
        )
        q = sqlite3.connect(self.path)
        try:
            q.execute("BEGIN IMMEDIATE")
            q.execute(
                "INSERT OR IGNORE INTO threshold_publications VALUES(?,?,?,?)",
                (envelope.entry_digest, entry_json, proof_json, root_json),
            )
            row = q.execute(
                "SELECT entry_json,proof_json,root_json FROM threshold_publications "
                "WHERE entry_digest=?",
                (envelope.entry_digest,),
            ).fetchone()
            if row != (entry_json, proof_json, root_json):
                raise ProofSubstitution(
                    "same entry identity has different historical proof"
                )
            q.commit()
            return envelope.entry_digest
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()

    def verify_historical(self, entry_digest: str) -> ThresholdEnvelope:
        q = sqlite3.connect(self.path)
        try:
            row = q.execute(
                "SELECT entry_json,proof_json,root_json FROM threshold_publications "
                "WHERE entry_digest=?",
                (entry_digest,),
            ).fetchone()
        finally:
            q.close()
        if row is None:
            raise ProofSubstitution("missing historical threshold proof")
        e = json.loads(row[0])
        p = json.loads(row[1])
        r = json.loads(row[2])
        root = RootState(
            r["provider_id"],
            r["version"],
            r["authority_epoch"],
            r["threshold"],
            dict(r["keys"]),
            tuple(r.get("revoked", [])),
        )
        entry = RegistryEntry(
            e["sink_id"],
            e["generation"],
            e["adapter_digest"],
            e["endpoint_origin"],
            e["operation_profile"],
            e.get("predecessor_entry_digest"),
            e["issuer_id"],
            e["issuer_generation"],
            e["signature"],
        )
        proof = ThresholdProof(
            p["authority_id"],
            p["authority_version"],
            tuple(
                Signature(x["signer_id"], x["signature"])
                for x in p["signatures"]
            ),
        )
        envelope = ThresholdEnvelope(entry, proof)
        if entry.entry_digest != entry_digest:
            raise ProofSubstitution("stored entry digest mismatch")
        return verify_envelope(root, envelope)


class UnsafeSingleSignerPublication:
    """Deliberately unsafe: any one active key is enough to publish."""

    @staticmethod
    def accepts(root: RootState, entry: RegistryEntry, signature: Signature) -> bool:
        key_hex = root.keys.get(signature.signer_id)
        if key_hex is None or signature.signer_id in root.revoked:
            return False
        expected = hmac.new(
            bytes.fromhex(key_hex), canon(entry.unsigned), hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected, signature.signature)
