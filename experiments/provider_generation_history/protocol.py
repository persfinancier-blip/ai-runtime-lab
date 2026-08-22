from __future__ import annotations

import hashlib
import hmac
import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path


class ProviderHistoryError(RuntimeError):
    pass


class InvalidTransition(ProviderHistoryError):
    pass


class HistoricalVerificationError(ProviderHistoryError):
    pass


class CurrentGenerationRequired(ProviderHistoryError):
    pass


class PendingRotationBlocked(ProviderHistoryError):
    pass


class HistoryRollback(ProviderHistoryError):
    pass


def canon(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def sha(obj) -> str:
    return hashlib.sha256(canon(obj)).hexdigest()


def key_id(key: bytes) -> str:
    return hashlib.sha256(key).hexdigest()


def mac(key: bytes, obj) -> str:
    return hmac.new(key, canon(obj), hashlib.sha256).hexdigest()


@dataclass(frozen=True)
class GenerationDescriptor:
    provider_id: str
    generation: int
    verification_key_hex: str

    def validate(self):
        if not isinstance(self.provider_id, str) or not self.provider_id:
            raise InvalidTransition("invalid provider id")
        if type(self.generation) is not int or self.generation < 1:
            raise InvalidTransition("invalid generation")
        try:
            key = bytes.fromhex(self.verification_key_hex)
        except Exception as exc:
            raise InvalidTransition("invalid verification key encoding") from exc
        if not key:
            raise InvalidTransition("empty verification key")
        return self

    @property
    def key(self):
        self.validate()
        return bytes.fromhex(self.verification_key_hex)

    @property
    def descriptor(self):
        return {
            "provider_id": self.provider_id,
            "generation": self.generation,
            "verification_key_id": key_id(self.key),
        }

    @property
    def generation_id(self):
        return sha(self.descriptor)


@dataclass(frozen=True)
class TransitionProof:
    provider_id: str
    old_generation_id: str
    new_generation_id: str
    old_mac: str
    new_mac: str

    @property
    def unsigned(self):
        return {
            "provider_id": self.provider_id,
            "old_generation_id": self.old_generation_id,
            "new_generation_id": self.new_generation_id,
        }


@dataclass(frozen=True)
class HistoricalReceipt:
    provider_id: str
    generation: int
    position: int
    request_id: str
    kind: str
    challenge: str
    signature: str

    @property
    def unsigned(self):
        return {
            "provider_id": self.provider_id,
            "generation": self.generation,
            "position": self.position,
            "request_id": self.request_id,
            "kind": self.kind,
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


class DurableProviderHistory:
    """Single-provider generation lifecycle with verification-only historical keys."""

    def __init__(self, path: str | Path, bootstrap: GenerationDescriptor):
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
                CREATE TABLE IF NOT EXISTS provider_generations(
                  generation_id TEXT PRIMARY KEY,
                  provider_id TEXT NOT NULL,
                  generation INTEGER NOT NULL,
                  verification_key_hex TEXT NOT NULL,
                  UNIQUE(provider_id,generation)
                );
                CREATE TABLE IF NOT EXISTS provider_generation_transitions(
                  new_generation_id TEXT PRIMARY KEY,
                  old_generation_id TEXT NOT NULL,
                  provider_id TEXT NOT NULL,
                  old_mac TEXT NOT NULL,
                  new_mac TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS provider_generation_head(
                  singleton INTEGER PRIMARY KEY CHECK(singleton=1),
                  generation_id TEXT NOT NULL,
                  generation INTEGER NOT NULL
                );
                CREATE TABLE IF NOT EXISTS historical_provider_receipts(
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
            row = q.execute("SELECT COUNT(*) FROM provider_generation_head").fetchone()[0]
            if row == 0:
                q.execute(
                    "INSERT INTO provider_generations VALUES(?,?,?,?)",
                    (
                        self.bootstrap.generation_id,
                        self.bootstrap.provider_id,
                        self.bootstrap.generation,
                        self.bootstrap.verification_key_hex,
                    ),
                )
                q.execute(
                    "INSERT INTO provider_generation_head VALUES(1,?,?)",
                    (self.bootstrap.generation_id, self.bootstrap.generation),
                )
            q.commit()
        finally:
            q.close()

    @staticmethod
    def make_transition(old: GenerationDescriptor, new: GenerationDescriptor) -> TransitionProof:
        old.validate(); new.validate()
        if old.provider_id != new.provider_id:
            raise InvalidTransition("provider id changed")
        if new.generation != old.generation + 1:
            raise InvalidTransition("generation must advance exactly one")
        body = {
            "provider_id": old.provider_id,
            "old_generation_id": old.generation_id,
            "new_generation_id": new.generation_id,
        }
        return TransitionProof(
            old.provider_id,
            old.generation_id,
            new.generation_id,
            mac(old.key, body),
            mac(new.key, body),
        )

    def _descriptor_locked(self, q, generation_id):
        row = q.execute(
            "SELECT provider_id,generation,verification_key_hex FROM provider_generations WHERE generation_id=?",
            (generation_id,),
        ).fetchone()
        if row is None:
            raise HistoricalVerificationError("missing generation material")
        desc = GenerationDescriptor(*row)
        if desc.generation_id != generation_id:
            raise HistoricalVerificationError("generation content substitution")
        return desc

    def current(self):
        q = self._con()
        try:
            gid, generation = q.execute(
                "SELECT generation_id,generation FROM provider_generation_head WHERE singleton=1"
            ).fetchone()
            desc = self._descriptor_locked(q, gid)
            if desc.generation != generation:
                raise HistoryRollback("head generation mismatch")
            return desc
        finally:
            q.close()

    def rotate(self, new: GenerationDescriptor, proof: TransitionProof, *, pending_prepared=0):
        new.validate()
        if pending_prepared:
            raise PendingRotationBlocked("unresolved PREPARED anchor intent")
        q = self._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            head_id, head_generation = q.execute(
                "SELECT generation_id,generation FROM provider_generation_head WHERE singleton=1"
            ).fetchone()
            old = self._descriptor_locked(q, head_id)
            expected = self.make_transition(old, new)
            if proof != expected:
                raise InvalidTransition("transition proof mismatch")
            if new.provider_id != old.provider_id or new.generation != head_generation + 1:
                raise InvalidTransition("invalid successor")
            q.execute(
                "INSERT INTO provider_generations VALUES(?,?,?,?)",
                (new.generation_id, new.provider_id, new.generation, new.verification_key_hex),
            )
            q.execute(
                "INSERT INTO provider_generation_transitions VALUES(?,?,?,?,?)",
                (new.generation_id, old.generation_id, new.provider_id, proof.old_mac, proof.new_mac),
            )
            changed = q.execute(
                "UPDATE provider_generation_head SET generation_id=?,generation=? "
                "WHERE singleton=1 AND generation_id=? AND generation=?",
                (new.generation_id, new.generation, old.generation_id, old.generation),
            ).rowcount
            if changed != 1:
                raise HistoryRollback("generation head changed during rotation")
            q.commit()
            return new
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()

    def verify_durable(self):
        q = self._con()
        try:
            q.execute("BEGIN")
            rows = q.execute(
                "SELECT generation_id,provider_id,generation,verification_key_hex FROM provider_generations ORDER BY generation"
            ).fetchall()
            if not rows:
                raise HistoricalVerificationError("missing provider history")
            descriptors = []
            for gid, provider_id, generation, key_hex in rows:
                desc = GenerationDescriptor(provider_id, generation, key_hex)
                if desc.generation_id != gid:
                    raise HistoricalVerificationError("generation identity mismatch")
                descriptors.append(desc)
            if descriptors[0].generation_id != self.bootstrap.generation_id:
                raise HistoryRollback("bootstrap generation changed")
            for old, new in zip(descriptors, descriptors[1:]):
                row = q.execute(
                    "SELECT old_generation_id,provider_id,old_mac,new_mac FROM provider_generation_transitions WHERE new_generation_id=?",
                    (new.generation_id,),
                ).fetchone()
                if row is None:
                    raise HistoricalVerificationError("missing transition proof")
                proof = TransitionProof(row[1], row[0], new.generation_id, row[2], row[3])
                if proof != self.make_transition(old, new):
                    raise HistoricalVerificationError("corrupt transition proof")
            head_id, head_generation = q.execute(
                "SELECT generation_id,generation FROM provider_generation_head WHERE singleton=1"
            ).fetchone()
            if descriptors[-1].generation_id != head_id or descriptors[-1].generation != head_generation:
                raise HistoryRollback("provider head rollback/substitution")
            q.commit()
            return True
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()

    def require_current(self, provider_id, generation):
        current = self.current()
        if (provider_id, generation) != (current.provider_id, current.generation):
            raise CurrentGenerationRequired("historical generation is verification-only")
        return current

    def store_receipt(self, receipt: HistoricalReceipt):
        self.verify_receipt(receipt)
        q = self._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            existing = q.execute(
                "SELECT provider_id,generation,position,kind,challenge,signature,stable_binding "
                "FROM historical_provider_receipts WHERE request_id=?",
                (receipt.request_id,),
            ).fetchone()
            expected = (
                receipt.provider_id, receipt.generation, receipt.position, receipt.kind,
                receipt.challenge, receipt.signature, receipt.stable_binding,
            )
            if existing is not None and existing != expected:
                raise HistoricalVerificationError("request receipt substitution")
            if existing is None:
                q.execute(
                    "INSERT INTO historical_provider_receipts VALUES(?,?,?,?,?,?,?,?)",
                    (
                        receipt.request_id, receipt.provider_id, receipt.generation, receipt.position,
                        receipt.kind, receipt.challenge, receipt.signature, receipt.stable_binding,
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
                "SELECT provider_id,generation,position,request_id,kind,challenge,signature "
                "FROM historical_provider_receipts WHERE request_id=?",
                (request_id,),
            ).fetchone()
            if row is None:
                raise HistoricalVerificationError("missing historical receipt")
            receipt = HistoricalReceipt(*row)
            self.verify_receipt(receipt)
            return receipt
        finally:
            q.close()

    def verify_receipt(self, receipt: HistoricalReceipt):
        q = self._con()
        try:
            row = q.execute(
                "SELECT generation_id FROM provider_generations WHERE provider_id=? AND generation=?",
                (receipt.provider_id, receipt.generation),
            ).fetchone()
            if row is None:
                raise HistoricalVerificationError("unknown historical generation")
            desc = self._descriptor_locked(q, row[0])
            expected = mac(desc.key, receipt.unsigned)
            if not hmac.compare_digest(expected, receipt.signature):
                raise HistoricalVerificationError("historical receipt signature mismatch")
            return receipt
        finally:
            q.close()


class UnsafeCallerHistoricalKeyring:
    """Unsafe baseline: caller supplies arbitrary historical keys with no authenticated lifecycle."""

    @staticmethod
    def verify(receipt: HistoricalReceipt, key: bytes):
        return hmac.compare_digest(mac(key, receipt.unsigned), receipt.signature)
