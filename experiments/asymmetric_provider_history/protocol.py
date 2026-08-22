from __future__ import annotations

import hashlib
import hmac
import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)


class AsymmetricHistoryError(RuntimeError):
    pass


class InvalidTransition(AsymmetricHistoryError):
    pass


class HistoricalVerificationError(AsymmetricHistoryError):
    pass


class CurrentGenerationRequired(AsymmetricHistoryError):
    pass


class HistoryRollback(AsymmetricHistoryError):
    pass


def canon(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def sha(obj) -> str:
    return hashlib.sha256(canon(obj)).hexdigest()


def _raw_public(key: Ed25519PublicKey) -> bytes:
    return key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )


def _strict_hex(value, size_bytes: int) -> bool:
    return (
        isinstance(value, str)
        and len(value) == size_bytes * 2
        and all(c in "0123456789abcdef" for c in value)
    )


@dataclass(frozen=True)
class PublicGeneration:
    provider_id: str
    generation: int
    public_key_hex: str

    def validate(self):
        if not isinstance(self.provider_id, str) or not self.provider_id:
            raise HistoricalVerificationError("invalid provider id")
        if type(self.generation) is not int or self.generation < 1:
            raise HistoricalVerificationError("invalid generation")
        if not _strict_hex(self.public_key_hex, 32):
            raise HistoricalVerificationError("public key must be canonical lowercase 32-byte hex")
        try:
            raw = bytes.fromhex(self.public_key_hex)
            Ed25519PublicKey.from_public_bytes(raw)
        except Exception as exc:
            raise HistoricalVerificationError("invalid Ed25519 public key") from exc
        return self

    @property
    def public_key(self) -> Ed25519PublicKey:
        self.validate()
        return Ed25519PublicKey.from_public_bytes(bytes.fromhex(self.public_key_hex))

    @property
    def descriptor(self):
        return {
            "provider_id": self.provider_id,
            "generation": self.generation,
            "public_key_hex": self.public_key_hex,
        }

    @property
    def generation_id(self):
        return sha(self.descriptor)


class GenerationSigner:
    """Runtime signing capability. Private bytes are never exposed to the durable store."""

    def __init__(self, provider_id: str, generation: int, private_key: Ed25519PrivateKey):
        if not isinstance(private_key, Ed25519PrivateKey):
            raise TypeError("Ed25519PrivateKey required")
        self.provider_id = provider_id
        self.generation = generation
        self.__private_key = private_key
        self.public = PublicGeneration(
            provider_id,
            generation,
            _raw_public(private_key.public_key()).hex(),
        )
        self.public.validate()

    @classmethod
    def from_seed(cls, provider_id: str, generation: int, seed: bytes):
        if not isinstance(seed, bytes) or len(seed) != 32:
            raise ValueError("Ed25519 seed must be exactly 32 bytes")
        return cls(provider_id, generation, Ed25519PrivateKey.from_private_bytes(seed))

    def sign(self, payload: dict) -> str:
        return self.__private_key.sign(canon(payload)).hex()


@dataclass(frozen=True)
class TransitionProof:
    provider_id: str
    old_generation_id: str
    new_generation_id: str
    old_signature: str
    new_signature: str

    def validate(self):
        if not isinstance(self.provider_id, str) or not self.provider_id:
            raise InvalidTransition("invalid transition provider")
        if not _strict_hex(self.old_generation_id, 32) or not _strict_hex(self.new_generation_id, 32):
            raise InvalidTransition("invalid transition generation identity")
        if not _strict_hex(self.old_signature, 64) or not _strict_hex(self.new_signature, 64):
            raise InvalidTransition("invalid transition signature encoding")
        return self

    @property
    def unsigned(self):
        return {
            "kind": "provider-generation-transition",
            "provider_id": self.provider_id,
            "old_generation_id": self.old_generation_id,
            "new_generation_id": self.new_generation_id,
        }


@dataclass(frozen=True)
class SignedReceipt:
    provider_id: str
    generation: int
    position: int
    request_id: str
    kind: str
    challenge: str
    signature: str

    def validate(self):
        if not isinstance(self.provider_id, str) or not self.provider_id:
            raise HistoricalVerificationError("invalid receipt provider")
        if type(self.generation) is not int or self.generation < 1:
            raise HistoricalVerificationError("invalid receipt generation")
        if type(self.position) is not int or self.position < 0:
            raise HistoricalVerificationError("invalid receipt position")
        if not all(isinstance(x, str) and x for x in (self.request_id, self.kind, self.challenge)):
            raise HistoricalVerificationError("invalid receipt text field")
        if not _strict_hex(self.signature, 64):
            raise HistoricalVerificationError("invalid receipt signature encoding")
        return self

    @property
    def unsigned(self):
        return {
            "kind": self.kind,
            "provider_id": self.provider_id,
            "generation": self.generation,
            "position": self.position,
            "request_id": self.request_id,
            "challenge": self.challenge,
        }

    @property
    def stable_binding(self):
        return sha(
            {
                "provider_id": self.provider_id,
                "generation": self.generation,
                "position": self.position,
                "request_id": self.request_id,
            }
        )


def verify_signature(public: PublicGeneration, payload: dict, signature_hex: str):
    public.validate()
    if not _strict_hex(signature_hex, 64):
        raise HistoricalVerificationError("signature must be canonical lowercase 64-byte hex")
    try:
        signature = bytes.fromhex(signature_hex)
        public.public_key.verify(signature, canon(payload))
    except InvalidSignature as exc:
        raise HistoricalVerificationError("Ed25519 signature verification failed") from exc
    return True


class AsymmetricProviderHistory:
    """Durable provider history that stores public verification material only."""

    def __init__(self, path: str | Path, bootstrap: PublicGeneration):
        bootstrap.validate()
        self.path = str(path)
        self.bootstrap = bootstrap
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
                CREATE TABLE IF NOT EXISTS asymmetric_provider_generations(
                  generation_id TEXT PRIMARY KEY,
                  provider_id TEXT NOT NULL,
                  generation INTEGER NOT NULL,
                  public_key_hex TEXT NOT NULL,
                  UNIQUE(provider_id,generation)
                );
                CREATE TABLE IF NOT EXISTS asymmetric_provider_transitions(
                  new_generation_id TEXT PRIMARY KEY,
                  old_generation_id TEXT NOT NULL,
                  provider_id TEXT NOT NULL,
                  old_signature TEXT NOT NULL,
                  new_signature TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS asymmetric_provider_head(
                  singleton INTEGER PRIMARY KEY CHECK(singleton=1),
                  generation_id TEXT NOT NULL,
                  generation INTEGER NOT NULL
                );
                CREATE TABLE IF NOT EXISTS asymmetric_provider_receipts(
                  request_id TEXT PRIMARY KEY,
                  provider_id TEXT NOT NULL,
                  generation INTEGER NOT NULL,
                  position INTEGER NOT NULL,
                  kind TEXT NOT NULL,
                  challenge TEXT NOT NULL,
                  signature TEXT NOT NULL,
                  stable_binding TEXT NOT NULL
                );
                """
            )
            if q.execute("SELECT COUNT(*) FROM asymmetric_provider_head").fetchone()[0] == 0:
                q.execute(
                    "INSERT INTO asymmetric_provider_generations VALUES(?,?,?,?)",
                    (
                        self.bootstrap.generation_id,
                        self.bootstrap.provider_id,
                        self.bootstrap.generation,
                        self.bootstrap.public_key_hex,
                    ),
                )
                q.execute(
                    "INSERT INTO asymmetric_provider_head VALUES(1,?,?)",
                    (self.bootstrap.generation_id, self.bootstrap.generation),
                )
            q.commit()
        finally:
            q.close()

    def _public_locked(self, q, generation_id):
        row = q.execute(
            "SELECT provider_id,generation,public_key_hex "
            "FROM asymmetric_provider_generations WHERE generation_id=?",
            (generation_id,),
        ).fetchone()
        if row is None:
            raise HistoricalVerificationError("missing public generation material")
        public = PublicGeneration(*row)
        if public.generation_id != generation_id:
            raise HistoricalVerificationError("public generation content substitution")
        return public

    def current(self):
        q = self._con()
        try:
            gid, generation = q.execute(
                "SELECT generation_id,generation FROM asymmetric_provider_head WHERE singleton=1"
            ).fetchone()
            public = self._public_locked(q, gid)
            if public.generation != generation:
                raise HistoryRollback("head generation mismatch")
            return public
        finally:
            q.close()

    @staticmethod
    def make_transition(old_signer: GenerationSigner, new_signer: GenerationSigner):
        old = old_signer.public
        new = new_signer.public
        if old.provider_id != new.provider_id:
            raise InvalidTransition("provider changed")
        if new.generation != old.generation + 1:
            raise InvalidTransition("generation must advance exactly one")
        unsigned = {
            "kind": "provider-generation-transition",
            "provider_id": old.provider_id,
            "old_generation_id": old.generation_id,
            "new_generation_id": new.generation_id,
        }
        return TransitionProof(
            old.provider_id,
            old.generation_id,
            new.generation_id,
            old_signer.sign(unsigned),
            new_signer.sign(unsigned),
        )

    def rotate(self, new: PublicGeneration, proof: TransitionProof):
        new.validate()
        proof.validate()
        q = self._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            head_id, head_generation = q.execute(
                "SELECT generation_id,generation FROM asymmetric_provider_head WHERE singleton=1"
            ).fetchone()
            old = self._public_locked(q, head_id)
            if (
                proof.provider_id != old.provider_id
                or proof.old_generation_id != old.generation_id
                or proof.new_generation_id != new.generation_id
            ):
                raise InvalidTransition("transition identity mismatch")
            if new.provider_id != old.provider_id or new.generation != head_generation + 1:
                raise InvalidTransition("invalid successor")
            verify_signature(old, proof.unsigned, proof.old_signature)
            verify_signature(new, proof.unsigned, proof.new_signature)
            q.execute(
                "INSERT INTO asymmetric_provider_generations VALUES(?,?,?,?)",
                (new.generation_id, new.provider_id, new.generation, new.public_key_hex),
            )
            q.execute(
                "INSERT INTO asymmetric_provider_transitions VALUES(?,?,?,?,?)",
                (
                    new.generation_id,
                    old.generation_id,
                    old.provider_id,
                    proof.old_signature,
                    proof.new_signature,
                ),
            )
            changed = q.execute(
                "UPDATE asymmetric_provider_head SET generation_id=?,generation=? "
                "WHERE singleton=1 AND generation_id=? AND generation=?",
                (new.generation_id, new.generation, old.generation_id, old.generation),
            ).rowcount
            if changed != 1:
                raise HistoryRollback("provider head changed")
            q.commit()
            return new
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()

    def sign_current_receipt(
        self,
        signer: GenerationSigner,
        *,
        position: int,
        request_id: str,
        kind: str = "RECONCILE",
        challenge: str = "challenge",
    ):
        current = self.current()
        if signer.public.generation_id != current.generation_id:
            raise CurrentGenerationRequired("signer is not the current durable generation")
        if type(position) is not int or position < 0:
            raise HistoricalVerificationError("invalid receipt position")
        if not all(isinstance(x, str) and x for x in (request_id, kind, challenge)):
            raise HistoricalVerificationError("invalid receipt fields")
        unsigned = {
            "kind": kind,
            "provider_id": current.provider_id,
            "generation": current.generation,
            "position": position,
            "request_id": request_id,
            "challenge": challenge,
        }
        return SignedReceipt(
            current.provider_id,
            current.generation,
            position,
            request_id,
            kind,
            challenge,
            signer.sign(unsigned),
        )

    def _verify_receipt_locked(self, q, receipt: SignedReceipt):
        receipt.validate()
        row = q.execute(
            "SELECT generation_id FROM asymmetric_provider_generations "
            "WHERE provider_id=? AND generation=?",
            (receipt.provider_id, receipt.generation),
        ).fetchone()
        if row is None:
            raise HistoricalVerificationError("unknown receipt generation")
        public = self._public_locked(q, row[0])
        verify_signature(public, receipt.unsigned, receipt.signature)
        return receipt

    def store_receipt(self, receipt: SignedReceipt):
        q = self._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            self._verify_receipt_locked(q, receipt)
            expected = (
                receipt.provider_id,
                receipt.generation,
                receipt.position,
                receipt.kind,
                receipt.challenge,
                receipt.signature,
                receipt.stable_binding,
            )
            existing = q.execute(
                "SELECT provider_id,generation,position,kind,challenge,signature,stable_binding "
                "FROM asymmetric_provider_receipts WHERE request_id=?",
                (receipt.request_id,),
            ).fetchone()
            if existing is not None and existing != expected:
                raise HistoricalVerificationError("receipt substitution")
            if existing is None:
                q.execute(
                    "INSERT INTO asymmetric_provider_receipts VALUES(?,?,?,?,?,?,?,?)",
                    (
                        receipt.request_id,
                        receipt.provider_id,
                        receipt.generation,
                        receipt.position,
                        receipt.kind,
                        receipt.challenge,
                        receipt.signature,
                        receipt.stable_binding,
                    ),
                )
            q.commit()
            return receipt.stable_binding
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()

    def load_receipt(self, request_id):
        q = self._con()
        try:
            row = q.execute(
                "SELECT provider_id,generation,position,request_id,kind,challenge,signature,stable_binding "
                "FROM asymmetric_provider_receipts WHERE request_id=?",
                (request_id,),
            ).fetchone()
            if row is None:
                raise HistoricalVerificationError("missing receipt")
            receipt = self._verify_receipt_locked(q, SignedReceipt(*row[:7]))
            if row[7] != receipt.stable_binding:
                raise HistoricalVerificationError("receipt stable binding mismatch")
            return receipt
        finally:
            q.close()

    def verify_durable(self):
        q = self._con()
        try:
            q.execute("BEGIN")
            rows = q.execute(
                "SELECT generation_id,provider_id,generation,public_key_hex "
                "FROM asymmetric_provider_generations ORDER BY generation"
            ).fetchall()
            if not rows:
                raise HistoricalVerificationError("missing provider history")
            publics = []
            for gid, provider_id, generation, public_hex in rows:
                public = PublicGeneration(provider_id, generation, public_hex)
                if public.generation_id != gid:
                    raise HistoricalVerificationError("public generation identity mismatch")
                publics.append(public)
            if publics[0].generation_id != self.bootstrap.generation_id:
                raise HistoryRollback("bootstrap changed")
            for old, new in zip(publics, publics[1:]):
                row = q.execute(
                    "SELECT old_generation_id,provider_id,old_signature,new_signature "
                    "FROM asymmetric_provider_transitions WHERE new_generation_id=?",
                    (new.generation_id,),
                ).fetchone()
                if row is None:
                    raise HistoricalVerificationError("missing transition")
                proof = TransitionProof(row[1], row[0], new.generation_id, row[2], row[3])
                try:
                    proof.validate()
                except InvalidTransition as exc:
                    raise HistoricalVerificationError("invalid persisted transition schema") from exc
                if (
                    proof.provider_id != old.provider_id
                    or proof.old_generation_id != old.generation_id
                    or proof.new_generation_id != new.generation_id
                    or new.provider_id != old.provider_id
                    or new.generation != old.generation + 1
                ):
                    raise HistoricalVerificationError("transition continuity mismatch")
                verify_signature(old, proof.unsigned, proof.old_signature)
                verify_signature(new, proof.unsigned, proof.new_signature)
            head_id, head_generation = q.execute(
                "SELECT generation_id,generation FROM asymmetric_provider_head WHERE singleton=1"
            ).fetchone()
            if publics[-1].generation_id != head_id or publics[-1].generation != head_generation:
                raise HistoryRollback("head rollback/substitution")
            for row in q.execute(
                "SELECT provider_id,generation,position,request_id,kind,challenge,signature,stable_binding "
                "FROM asymmetric_provider_receipts"
            ).fetchall():
                receipt = self._verify_receipt_locked(q, SignedReceipt(*row[:7]))
                if row[7] != receipt.stable_binding:
                    raise HistoricalVerificationError("receipt stable binding mismatch")
            q.commit()
            return True
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()

    def durable_public_rows(self):
        q = self._con()
        try:
            return q.execute(
                "SELECT provider_id,generation,public_key_hex FROM asymmetric_provider_generations ORDER BY generation"
            ).fetchall()
        finally:
            q.close()


class UnsafeSymmetricHistory:
    """Unsafe baseline: the durable verification key is also a signing key."""

    def __init__(self, durable_key: bytes):
        self.durable_key = durable_key

    def sign(self, payload: dict):
        return hmac.new(self.durable_key, canon(payload), hashlib.sha256).hexdigest()

    def verify(self, payload: dict, signature: str):
        return hmac.compare_digest(self.sign(payload), signature)
