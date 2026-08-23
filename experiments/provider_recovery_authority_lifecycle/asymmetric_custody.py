from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey


class CustodyError(RuntimeError):
    pass


class CustodyThresholdNotMet(CustodyError):
    pass


class CustodySubstitution(CustodyError):
    pass


class CustodyRollback(CustodyError):
    pass


def canon(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def sha(obj) -> str:
    return hashlib.sha256(canon(obj)).hexdigest()


def _strict_hex(value, size_bytes: int) -> bool:
    return isinstance(value, str) and len(value) == size_bytes * 2 and all(c in "0123456789abcdef" for c in value)


def _public_hex(key: Ed25519PublicKey) -> str:
    return key.public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw).hex()


def signer_id(public_key_hex: str) -> str:
    if not _strict_hex(public_key_hex, 32):
        raise CustodyError("invalid public key encoding")
    return hashlib.sha256(bytes.fromhex(public_key_hex)).hexdigest()


@dataclass(frozen=True)
class PublicRecoveryAuthority:
    name: str
    version: int
    generation: int
    threshold: int
    public_keys: dict[str, str]
    revoked: tuple[str, ...] = ()

    def validate(self):
        if not isinstance(self.name, str) or not self.name:
            raise CustodyError("invalid recovery authority name")
        if type(self.version) is not int or self.version < 1:
            raise CustodyError("invalid recovery authority version")
        if type(self.generation) is not int or self.generation < 1:
            raise CustodyError("invalid recovery authority generation")
        if type(self.threshold) is not int or self.threshold < 1:
            raise CustodyError("invalid recovery threshold")
        if not isinstance(self.public_keys, dict) or not self.public_keys:
            raise CustodyError("missing recovery public keys")
        revoked = set(self.revoked)
        if len(revoked) != len(self.revoked):
            raise CustodyError("duplicate revoked signer")
        active = 0
        for sid, public_hex in self.public_keys.items():
            if not isinstance(sid, str) or sid != signer_id(public_hex):
                raise CustodyError("recovery signer id/public-key mismatch")
            try:
                Ed25519PublicKey.from_public_bytes(bytes.fromhex(public_hex))
            except Exception as exc:
                raise CustodyError("invalid recovery public key") from exc
            if sid not in revoked:
                active += 1
        if self.threshold > active:
            raise CustodyError("threshold exceeds active recovery signers")
        if any(sid not in self.public_keys for sid in revoked):
            raise CustodyError("revoked unknown signer")
        return self

    @property
    def descriptor(self):
        self.validate()
        return {
            "name": self.name,
            "version": self.version,
            "generation": self.generation,
            "threshold": self.threshold,
            "public_keys": dict(sorted(self.public_keys.items())),
            "revoked": sorted(self.revoked),
        }

    @property
    def authority_id(self):
        return sha(self.descriptor)


class RecoverySigner:
    """Runtime signing capability; private bytes are intentionally not durable state."""

    def __init__(self, private_key: Ed25519PrivateKey):
        if not isinstance(private_key, Ed25519PrivateKey):
            raise TypeError("Ed25519PrivateKey required")
        self.__private_key = private_key
        self.public_key_hex = _public_hex(private_key.public_key())
        self.signer_id = signer_id(self.public_key_hex)

    @classmethod
    def from_seed(cls, seed: bytes):
        if not isinstance(seed, bytes) or len(seed) != 32:
            raise ValueError("Ed25519 seed must be exactly 32 bytes")
        return cls(Ed25519PrivateKey.from_private_bytes(seed))

    def sign(self, payload: dict) -> "PublicSignature":
        return PublicSignature(self.signer_id, self.__private_key.sign(canon(payload)).hex())


@dataclass(frozen=True)
class PublicSignature:
    signer_id: str
    signature: str

    def validate(self):
        if not isinstance(self.signer_id, str) or not self.signer_id:
            raise CustodyError("invalid signer id")
        if not _strict_hex(self.signature, 64):
            raise CustodyError("invalid Ed25519 signature encoding")
        return self


@dataclass(frozen=True)
class CustodyRotationProof:
    intent_digest: str
    old_signatures: tuple[PublicSignature, ...]
    new_signatures: tuple[PublicSignature, ...]


def custody_rotation_payload(old: PublicRecoveryAuthority, new: PublicRecoveryAuthority, root_authority_id: str) -> dict:
    old.validate(); new.validate()
    return {
        "kind": "provider-recovery-custody-rotation",
        "root_authority_id": root_authority_id,
        "old_recovery_authority_id": old.authority_id,
        "new_recovery_authority": new.descriptor,
    }


def accepted_public_signatures(authority: PublicRecoveryAuthority, payload: dict, signatures) -> tuple[PublicSignature, ...]:
    authority.validate()
    seen = set(); accepted = []
    for item in signatures:
        try:
            item.validate()
        except CustodyError:
            continue
        if item.signer_id in seen or item.signer_id in authority.revoked:
            continue
        seen.add(item.signer_id)
        public_hex = authority.public_keys.get(item.signer_id)
        if public_hex is None:
            continue
        try:
            Ed25519PublicKey.from_public_bytes(bytes.fromhex(public_hex)).verify(bytes.fromhex(item.signature), canon(payload))
            accepted.append(item)
        except InvalidSignature:
            continue
    return tuple(accepted)


def verify_public_threshold(authority: PublicRecoveryAuthority, payload: dict, signatures) -> tuple[str, ...]:
    accepted = accepted_public_signatures(authority, payload, signatures)
    if len(accepted) < authority.threshold:
        raise CustodyThresholdNotMet(f"valid={len(accepted)} threshold={authority.threshold}")
    return tuple(sorted(item.signer_id for item in accepted))


class AsymmetricRecoveryCustody:
    """Durable public-only verification history for recovery-authority generations."""

    def __init__(self, path: str | Path, bootstrap: PublicRecoveryAuthority):
        bootstrap.validate()
        self.path = str(path)
        self.bootstrap = PublicRecoveryAuthority(
            bootstrap.name, bootstrap.version, bootstrap.generation, bootstrap.threshold,
            dict(bootstrap.public_keys), tuple(bootstrap.revoked),
        )
        self._init()
        self.verify_durable()

    def _con(self):
        q = sqlite3.connect(self.path, timeout=5, isolation_level=None)
        q.execute("PRAGMA busy_timeout=5000")
        return q

    def _init(self):
        q = self._con()
        try:
            q.executescript(
                """
                CREATE TABLE IF NOT EXISTS provider_recovery_public_authorities(
                  authority_id TEXT PRIMARY KEY,
                  name TEXT NOT NULL,
                  version INTEGER NOT NULL,
                  generation INTEGER NOT NULL,
                  threshold INTEGER NOT NULL,
                  public_keys_json TEXT NOT NULL,
                  revoked_json TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS provider_recovery_public_head(
                  singleton INTEGER PRIMARY KEY CHECK(singleton=1),
                  authority_id TEXT NOT NULL,
                  version INTEGER NOT NULL,
                  generation INTEGER NOT NULL
                );
                CREATE TABLE IF NOT EXISTS provider_recovery_public_transitions(
                  new_authority_id TEXT PRIMARY KEY,
                  old_authority_id TEXT NOT NULL,
                  root_authority_id TEXT NOT NULL,
                  intent_digest TEXT NOT NULL,
                  old_signatures_json TEXT NOT NULL,
                  new_signatures_json TEXT NOT NULL
                );
                """
            )
            if q.execute("SELECT COUNT(*) FROM provider_recovery_public_head").fetchone()[0] == 0:
                self._insert_authority_locked(q, self.bootstrap)
                q.execute(
                    "INSERT INTO provider_recovery_public_head VALUES(1,?,?,?)",
                    (self.bootstrap.authority_id, self.bootstrap.version, self.bootstrap.generation),
                )
            q.commit()
        finally:
            q.close()

    @staticmethod
    def _encode_signatures(signatures):
        return json.dumps(
            [{"signer_id": s.signer_id, "signature": s.signature} for s in signatures],
            sort_keys=True, separators=(",", ":"),
        )

    @staticmethod
    def _decode_signatures(raw):
        try:
            data = json.loads(raw)
            if not isinstance(data, list):
                raise ValueError()
            return tuple(PublicSignature(x["signer_id"], x["signature"]).validate() for x in data)
        except Exception as exc:
            raise CustodySubstitution("invalid persisted public signature set") from exc

    def _insert_authority_locked(self, q, authority):
        authority.validate()
        expected = (
            authority.name, authority.version, authority.generation, authority.threshold,
            json.dumps(authority.public_keys, sort_keys=True, separators=(",", ":")),
            json.dumps(sorted(authority.revoked), separators=(",", ":")),
        )
        q.execute(
            "INSERT OR IGNORE INTO provider_recovery_public_authorities VALUES(?,?,?,?,?,?,?)",
            (authority.authority_id, *expected),
        )
        stored = q.execute(
            "SELECT name,version,generation,threshold,public_keys_json,revoked_json "
            "FROM provider_recovery_public_authorities WHERE authority_id=?",
            (authority.authority_id,),
        ).fetchone()
        if stored != expected:
            raise CustodySubstitution("public recovery authority substitution")

    def _load_authority_locked(self, q, authority_id):
        row = q.execute(
            "SELECT name,version,generation,threshold,public_keys_json,revoked_json "
            "FROM provider_recovery_public_authorities WHERE authority_id=?",
            (authority_id,),
        ).fetchone()
        if row is None:
            raise CustodySubstitution("missing public recovery authority")
        authority = PublicRecoveryAuthority(
            row[0], row[1], row[2], row[3], dict(json.loads(row[4])), tuple(json.loads(row[5]))
        ).validate()
        if authority.authority_id != authority_id:
            raise CustodySubstitution("public recovery authority digest mismatch")
        return authority

    def current_locked(self, q):
        row = q.execute(
            "SELECT authority_id,version,generation FROM provider_recovery_public_head WHERE singleton=1"
        ).fetchone()
        if row is None:
            raise CustodySubstitution("missing public recovery head")
        authority = self._load_authority_locked(q, row[0])
        if (authority.version, authority.generation) != (row[1], row[2]):
            raise CustodySubstitution("public recovery head mismatch")
        return authority

    def rotate_locked(self, q, new, root_authority_id, old_signatures, new_signatures):
        old = self.current_locked(q); new.validate()
        if new.name != old.name:
            raise CustodySubstitution("recovery authority name changed")
        if new.version != old.version + 1 or new.generation != old.generation + 1:
            raise CustodyRollback("public recovery version/generation must advance exactly one")
        payload = custody_rotation_payload(old, new, root_authority_id)
        accepted_old = accepted_public_signatures(old, payload, old_signatures)
        accepted_new = accepted_public_signatures(new, payload, new_signatures)
        proof = CustodyRotationProof(sha(payload), accepted_old, accepted_new)
        verify_public_threshold(old, payload, proof.old_signatures)
        verify_public_threshold(new, payload, proof.new_signatures)
        self._insert_authority_locked(q, new)
        expected = (
            old.authority_id, root_authority_id, proof.intent_digest,
            self._encode_signatures(proof.old_signatures), self._encode_signatures(proof.new_signatures),
        )
        existing = q.execute(
            "SELECT old_authority_id,root_authority_id,intent_digest,old_signatures_json,new_signatures_json "
            "FROM provider_recovery_public_transitions WHERE new_authority_id=?",
            (new.authority_id,),
        ).fetchone()
        if existing is not None and existing != expected:
            raise CustodySubstitution("public recovery transition substitution")
        if existing is None:
            q.execute(
                "INSERT INTO provider_recovery_public_transitions VALUES(?,?,?,?,?,?)",
                (new.authority_id, *expected),
            )
        changed = q.execute(
            "UPDATE provider_recovery_public_head SET authority_id=?,version=?,generation=? "
            "WHERE singleton=1 AND authority_id=? AND version=? AND generation=?",
            (new.authority_id, new.version, new.generation, old.authority_id, old.version, old.generation),
        ).rowcount
        if changed != 1:
            raise CustodyRollback("public recovery head changed")
        return new

    def rotate(self, new, root_authority_id, old_signatures, new_signatures):
        q = self._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            result = self.rotate_locked(q, new, root_authority_id, old_signatures, new_signatures)
            q.commit(); return result
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()

    def historical(self, authority_id):
        q = self._con()
        try:
            return self._load_authority_locked(q, authority_id)
        finally:
            q.close()

    def verify_durable(self):
        q = self._con()
        try:
            q.execute("BEGIN")
            rows = q.execute(
                "SELECT authority_id FROM provider_recovery_public_authorities ORDER BY version"
            ).fetchall()
            if not rows:
                raise CustodySubstitution("missing public recovery history")
            authorities = [self._load_authority_locked(q, row[0]) for row in rows]
            if authorities[0].authority_id != self.bootstrap.authority_id:
                raise CustodySubstitution("public recovery bootstrap changed")
            for old, new in zip(authorities, authorities[1:]):
                if new.version != old.version + 1 or new.generation != old.generation + 1:
                    raise CustodyRollback("public recovery history gap")
                row = q.execute(
                    "SELECT old_authority_id,root_authority_id,intent_digest,old_signatures_json,new_signatures_json "
                    "FROM provider_recovery_public_transitions WHERE new_authority_id=?",
                    (new.authority_id,),
                ).fetchone()
                if row is None or row[0] != old.authority_id:
                    raise CustodySubstitution("missing public recovery transition")
                payload = custody_rotation_payload(old, new, row[1])
                if row[2] != sha(payload):
                    raise CustodySubstitution("public recovery transition digest mismatch")
                verify_public_threshold(old, payload, self._decode_signatures(row[3]))
                verify_public_threshold(new, payload, self._decode_signatures(row[4]))
            head = self.current_locked(q)
            if head.authority_id != authorities[-1].authority_id:
                raise CustodyRollback("public recovery head rollback")
            if q.execute("SELECT COUNT(*) FROM provider_recovery_public_transitions").fetchone()[0] != len(authorities) - 1:
                raise CustodySubstitution("orphan public recovery transition")
            q.commit(); return True
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()
