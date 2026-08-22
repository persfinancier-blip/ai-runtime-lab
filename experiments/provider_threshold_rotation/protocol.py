from __future__ import annotations

import hashlib
import hmac
import json
import sqlite3
from dataclasses import dataclass
from typing import Iterable


class RotationAuthorizationError(RuntimeError):
    pass


class ThresholdNotMet(RotationAuthorizationError):
    pass


class StaleAuthority(RotationAuthorizationError):
    pass


class InvalidAuthority(RotationAuthorizationError):
    pass


class ProofSubstitution(RotationAuthorizationError):
    pass


def canon(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def sha(obj) -> str:
    return hashlib.sha256(canon(obj)).hexdigest()


def key_id(key: bytes) -> str:
    return hashlib.sha256(key).hexdigest()[:16]


def mac(key: bytes, payload: dict) -> str:
    return hmac.new(key, canon(payload), hashlib.sha256).hexdigest()


@dataclass(frozen=True)
class Signature:
    signer_id: str
    signature: str


@dataclass(frozen=True)
class RotationAuthority:
    authority_name: str
    version: int
    generation: int
    threshold: int
    keys: dict[str, str]
    revoked: tuple[str, ...] = ()

    def validate(self):
        if not isinstance(self.authority_name, str) or not self.authority_name:
            raise InvalidAuthority("authority_name")
        if type(self.version) is not int or self.version < 1:
            raise InvalidAuthority("version")
        if type(self.generation) is not int or self.generation < 1:
            raise InvalidAuthority("generation")
        if len(set(self.revoked)) != len(self.revoked):
            raise InvalidAuthority("duplicate revoked signer")
        active = set(self.keys) - set(self.revoked)
        if type(self.threshold) is not int or self.threshold < 1 or self.threshold > len(active):
            raise InvalidAuthority("threshold")
        for sid, hx in self.keys.items():
            if not isinstance(hx, str) or len(hx) % 2:
                raise InvalidAuthority("key encoding")
            try:
                key = bytes.fromhex(hx)
            except ValueError as exc:
                raise InvalidAuthority("key encoding") from exc
            if sid != key_id(key):
                raise InvalidAuthority("signer/key mismatch")
        return self

    @property
    def descriptor(self):
        return {
            "authority_name": self.authority_name,
            "version": self.version,
            "generation": self.generation,
            "threshold": self.threshold,
            "keys": dict(sorted(self.keys.items())),
            "revoked": sorted(self.revoked),
        }

    @property
    def authority_id(self):
        return sha(self.descriptor)


@dataclass(frozen=True)
class ProviderRotationIntent:
    provider_id: str
    old_generation_id: str
    new_generation_id: str
    authority_id: str
    authority_version: int
    authority_generation: int

    @property
    def payload(self):
        return {
            "kind": "threshold-authorized-provider-generation-transition",
            "provider_id": self.provider_id,
            "old_generation_id": self.old_generation_id,
            "new_generation_id": self.new_generation_id,
            "authority_id": self.authority_id,
            "authority_version": self.authority_version,
            "authority_generation": self.authority_generation,
        }

    @property
    def intent_digest(self):
        return sha(self.payload)


@dataclass(frozen=True)
class ThresholdProof:
    intent_digest: str
    authority_id: str
    authority_version: int
    authority_generation: int
    signatures: tuple[Signature, ...]


def verify_threshold(authority: RotationAuthority, intent: ProviderRotationIntent, proof: ThresholdProof):
    authority.validate()
    if (
        intent.authority_id != authority.authority_id
        or intent.authority_version != authority.version
        or intent.authority_generation != authority.generation
    ):
        raise StaleAuthority("intent does not bind current authority")
    if (
        proof.intent_digest != intent.intent_digest
        or proof.authority_id != authority.authority_id
        or proof.authority_version != authority.version
        or proof.authority_generation != authority.generation
    ):
        raise ProofSubstitution("proof does not bind exact provider rotation intent")
    seen = set()
    valid = []
    revoked = set(authority.revoked)
    for sig in proof.signatures:
        if sig.signer_id in seen:
            continue
        seen.add(sig.signer_id)
        if sig.signer_id in revoked:
            continue
        hx = authority.keys.get(sig.signer_id)
        if hx is None:
            continue
        expected = mac(bytes.fromhex(hx), intent.payload)
        if hmac.compare_digest(expected, sig.signature):
            valid.append(sig.signer_id)
    if len(valid) < authority.threshold:
        raise ThresholdNotMet(f"valid={len(valid)} threshold={authority.threshold}")
    return tuple(sorted(valid))


class DurableRotationAuthority:
    """Threshold rotation authority stored in the caller's SQLite database."""

    def __init__(self, path, bootstrap: RotationAuthority):
        bootstrap.validate()
        self.path = str(path)
        self.bootstrap = bootstrap
        q = self._con()
        try:
            q.executescript(
                """
                CREATE TABLE IF NOT EXISTS provider_rotation_authorities(
                  authority_id TEXT PRIMARY KEY,
                  authority_name TEXT NOT NULL,
                  version INTEGER NOT NULL,
                  generation INTEGER NOT NULL,
                  threshold INTEGER NOT NULL,
                  keys_json TEXT NOT NULL,
                  revoked_json TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS provider_rotation_authority_head(
                  singleton INTEGER PRIMARY KEY CHECK(singleton=1),
                  authority_id TEXT NOT NULL,
                  version INTEGER NOT NULL,
                  generation INTEGER NOT NULL
                );
                CREATE TABLE IF NOT EXISTS provider_rotation_authority_transitions(
                  new_authority_id TEXT PRIMARY KEY,
                  old_authority_id TEXT NOT NULL,
                  payload_digest TEXT NOT NULL,
                  old_signatures_json TEXT NOT NULL,
                  new_signatures_json TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS provider_rotation_threshold_proofs(
                  new_provider_generation_id TEXT PRIMARY KEY,
                  provider_id TEXT NOT NULL,
                  old_provider_generation_id TEXT NOT NULL,
                  authority_id TEXT NOT NULL,
                  authority_version INTEGER NOT NULL,
                  authority_generation INTEGER NOT NULL,
                  intent_digest TEXT NOT NULL,
                  signatures_json TEXT NOT NULL
                );
                """
            )
            if q.execute("SELECT COUNT(*) FROM provider_rotation_authority_head").fetchone()[0] == 0:
                self._insert_authority_locked(q, bootstrap)
                q.execute(
                    "INSERT INTO provider_rotation_authority_head VALUES(1,?,?,?)",
                    (bootstrap.authority_id, bootstrap.version, bootstrap.generation),
                )
            q.commit()
        finally:
            q.close()

    def _con(self):
        q = sqlite3.connect(self.path, timeout=5, isolation_level=None)
        q.execute("PRAGMA busy_timeout=5000")
        return q

    @staticmethod
    def _encode_signatures(signatures: Iterable[Signature]) -> str:
        return json.dumps(
            [{"signer_id": s.signer_id, "signature": s.signature} for s in signatures],
            sort_keys=True,
            separators=(",", ":"),
        )

    @staticmethod
    def _decode_signatures(raw: str) -> tuple[Signature, ...]:
        try:
            vals = json.loads(raw)
            if not isinstance(vals, list):
                raise ValueError()
            return tuple(Signature(x["signer_id"], x["signature"]) for x in vals)
        except Exception as exc:
            raise InvalidAuthority("invalid persisted signature list") from exc

    def _insert_authority_locked(self, q, authority: RotationAuthority):
        authority.validate()
        body = (
            authority.authority_name,
            authority.version,
            authority.generation,
            authority.threshold,
            json.dumps(authority.keys, sort_keys=True, separators=(",", ":")),
            json.dumps(sorted(authority.revoked), separators=(",", ":")),
        )
        q.execute(
            "INSERT OR IGNORE INTO provider_rotation_authorities VALUES(?,?,?,?,?,?,?)",
            (authority.authority_id, *body),
        )
        stored = q.execute(
            "SELECT authority_name,version,generation,threshold,keys_json,revoked_json "
            "FROM provider_rotation_authorities WHERE authority_id=?",
            (authority.authority_id,),
        ).fetchone()
        if stored != body:
            raise InvalidAuthority("authority content substitution")

    def _load_locked(self, q, authority_id) -> RotationAuthority:
        row = q.execute(
            "SELECT authority_name,version,generation,threshold,keys_json,revoked_json "
            "FROM provider_rotation_authorities WHERE authority_id=?",
            (authority_id,),
        ).fetchone()
        if row is None:
            raise InvalidAuthority("missing authority")
        try:
            a = RotationAuthority(
                row[0], row[1], row[2], row[3], dict(json.loads(row[4])), tuple(json.loads(row[5]))
            )
        except Exception as exc:
            raise InvalidAuthority("invalid persisted authority") from exc
        a.validate()
        if a.authority_id != authority_id:
            raise InvalidAuthority("authority digest mismatch")
        return a

    def current_locked(self, q):
        row = q.execute(
            "SELECT authority_id,version,generation FROM provider_rotation_authority_head WHERE singleton=1"
        ).fetchone()
        if row is None:
            raise InvalidAuthority("missing authority head")
        a = self._load_locked(q, row[0])
        if (a.version, a.generation) != (row[1], row[2]):
            raise InvalidAuthority("authority head mismatch")
        return a

    def current(self):
        q = self._con()
        try:
            return self.current_locked(q)
        finally:
            q.close()

    @staticmethod
    def authority_rotation_payload(old: RotationAuthority, new: RotationAuthority):
        return {
            "kind": "provider-rotation-authority-transition",
            "old_authority_id": old.authority_id,
            "new_authority": new.descriptor,
        }

    def rotate_authority_locked(self, q, new: RotationAuthority, old_signatures, new_signatures):
        old = self.current_locked(q)
        new.validate()
        if new.authority_name != old.authority_name:
            raise InvalidAuthority("authority name changed")
        if new.version != old.version + 1 or new.generation != old.generation + 1:
            raise StaleAuthority("authority must advance exactly one")
        payload = self.authority_rotation_payload(old, new)

        def check(a, sigs):
            seen = set()
            good = []
            for sig in sigs:
                if sig.signer_id in seen or sig.signer_id in set(a.revoked):
                    continue
                seen.add(sig.signer_id)
                hx = a.keys.get(sig.signer_id)
                if hx and hmac.compare_digest(mac(bytes.fromhex(hx), payload), sig.signature):
                    good.append(sig.signer_id)
            if len(good) < a.threshold:
                raise ThresholdNotMet()
            return tuple(sorted(good))

        old_valid = check(old, old_signatures)
        new_valid = check(new, new_signatures)
        self._insert_authority_locked(q, new)
        q.execute(
            "INSERT INTO provider_rotation_authority_transitions VALUES(?,?,?,?,?)",
            (
                new.authority_id,
                old.authority_id,
                sha(payload),
                self._encode_signatures(old_signatures),
                self._encode_signatures(new_signatures),
            ),
        )
        changed = q.execute(
            "UPDATE provider_rotation_authority_head SET authority_id=?,version=?,generation=? "
            "WHERE singleton=1 AND authority_id=? AND version=? AND generation=?",
            (
                new.authority_id,
                new.version,
                new.generation,
                old.authority_id,
                old.version,
                old.generation,
            ),
        ).rowcount
        if changed != 1:
            raise StaleAuthority("authority head changed")
        return {"old_signers": old_valid, "new_signers": new_valid}

    def rotate_authority(self, new, old_signatures, new_signatures):
        q = self._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            out = self.rotate_authority_locked(q, new, old_signatures, new_signatures)
            q.commit()
            return out
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()

    def authorize_provider_rotation_locked(
        self,
        q,
        *,
        provider_id,
        old_generation_id,
        new_generation_id,
        signatures,
    ):
        current = self.current_locked(q)
        intent = ProviderRotationIntent(
            provider_id,
            old_generation_id,
            new_generation_id,
            current.authority_id,
            current.version,
            current.generation,
        )
        proof = ThresholdProof(
            intent.intent_digest,
            current.authority_id,
            current.version,
            current.generation,
            tuple(signatures),
        )
        signers = verify_threshold(current, intent, proof)
        existing = q.execute(
            "SELECT provider_id,old_provider_generation_id,authority_id,authority_version,"
            "authority_generation,intent_digest,signatures_json "
            "FROM provider_rotation_threshold_proofs WHERE new_provider_generation_id=?",
            (new_generation_id,),
        ).fetchone()
        expected = (
            provider_id,
            old_generation_id,
            current.authority_id,
            current.version,
            current.generation,
            intent.intent_digest,
            self._encode_signatures(signatures),
        )
        if existing is not None and existing != expected:
            raise ProofSubstitution("provider threshold proof substitution")
        if existing is None:
            q.execute(
                "INSERT INTO provider_rotation_threshold_proofs VALUES(?,?,?,?,?,?,?,?)",
                (new_generation_id, *expected),
            )
        return intent, proof, signers

    def verify_durable_locked(self, q, provider_transitions: Iterable[tuple[str, str, str]]):
        authority_rows = q.execute(
            "SELECT authority_id FROM provider_rotation_authorities ORDER BY version"
        ).fetchall()
        if not authority_rows:
            raise InvalidAuthority("missing authority history")
        authorities = [self._load_locked(q, row[0]) for row in authority_rows]
        if authorities[0].authority_id != self.bootstrap.authority_id:
            raise StaleAuthority("authority bootstrap changed")
        for old, new in zip(authorities, authorities[1:]):
            row = q.execute(
                "SELECT old_authority_id,payload_digest,old_signatures_json,new_signatures_json "
                "FROM provider_rotation_authority_transitions WHERE new_authority_id=?",
                (new.authority_id,),
            ).fetchone()
            if row is None or row[0] != old.authority_id:
                raise InvalidAuthority("missing/incorrect authority transition")
            payload = self.authority_rotation_payload(old, new)
            if row[1] != sha(payload):
                raise InvalidAuthority("authority transition digest mismatch")
            for a, raw in ((old, row[2]), (new, row[3])):
                sigs = self._decode_signatures(raw)
                seen = set()
                valid = 0
                for sig in sigs:
                    if sig.signer_id in seen or sig.signer_id in set(a.revoked):
                        continue
                    seen.add(sig.signer_id)
                    hx = a.keys.get(sig.signer_id)
                    if hx and hmac.compare_digest(mac(bytes.fromhex(hx), payload), sig.signature):
                        valid += 1
                if valid < a.threshold:
                    raise ThresholdNotMet("persisted authority transition below threshold")
        head = self.current_locked(q)
        if head.authority_id != authorities[-1].authority_id:
            raise StaleAuthority("authority head rollback")

        by_id = {a.authority_id: a for a in authorities}
        for provider_id, old_gid, new_gid in provider_transitions:
            row = q.execute(
                "SELECT authority_id,authority_version,authority_generation,intent_digest,signatures_json "
                "FROM provider_rotation_threshold_proofs WHERE new_provider_generation_id=?",
                (new_gid,),
            ).fetchone()
            if row is None:
                raise ThresholdNotMet("provider transition missing threshold proof")
            authority = by_id.get(row[0])
            if authority is None:
                raise InvalidAuthority("threshold proof references unknown authority")
            intent = ProviderRotationIntent(
                provider_id, old_gid, new_gid, authority.authority_id, authority.version, authority.generation
            )
            proof = ThresholdProof(row[3], row[0], row[1], row[2], self._decode_signatures(row[4]))
            verify_threshold(authority, intent, proof)
        return head


class UnsafeOldAndNewOnly:
    @staticmethod
    def allows(old_signature_valid: bool, new_signature_valid: bool):
        return bool(old_signature_valid and new_signature_valid)
