from __future__ import annotations

import hmac
import json
import sqlite3
from dataclasses import dataclass
from typing import Iterable

from experiments.provider_threshold_rotation.protocol import (
    DurableRotationAuthority,
    InvalidAuthority,
    RotationAuthority,
    Signature,
    StaleAuthority,
    ThresholdNotMet,
    key_id,
    mac,
    sha,
)


class RecoveryError(RuntimeError):
    pass


class RecoveryAuthorityMismatch(RecoveryError):
    pass


class RecoveryProofSubstitution(RecoveryError):
    pass


@dataclass(frozen=True)
class RecoveryAuthority:
    name: str
    generation: int
    threshold: int
    keys: dict[str, str]
    revoked: tuple[str, ...] = ()

    def validate(self):
        if not isinstance(self.name, str) or not self.name:
            raise RecoveryError("recovery authority name")
        if type(self.generation) is not int or self.generation < 1:
            raise RecoveryError("recovery generation")
        if type(self.keys) is not dict or type(self.revoked) is not tuple:
            raise RecoveryError("noncanonical recovery authority container")
        if len(set(self.revoked)) != len(self.revoked):
            raise RecoveryError("duplicate revoked recovery signer")
        active = set(self.keys) - set(self.revoked)
        if type(self.threshold) is not int or self.threshold < 1 or self.threshold > len(active):
            raise RecoveryError("recovery threshold")
        for signer_id, hx in self.keys.items():
            if (
                not isinstance(signer_id, str)
                or not signer_id
                or not isinstance(hx, str)
                or len(hx) == 0
                or len(hx) % 2
                or any(c not in "0123456789abcdef" for c in hx)
            ):
                raise RecoveryError("noncanonical recovery key")
            try:
                raw = bytes.fromhex(hx)
            except ValueError as exc:
                raise RecoveryError("recovery key encoding") from exc
            if signer_id != key_id(raw):
                raise RecoveryError("recovery signer/key mismatch")
        for signer_id in self.revoked:
            if signer_id not in self.keys:
                raise RecoveryError("unknown revoked recovery signer")
        return self

    @property
    def descriptor(self):
        self.validate()
        return {
            "name": self.name,
            "generation": self.generation,
            "threshold": self.threshold,
            "keys": dict(sorted(self.keys.items())),
            "revoked": sorted(self.revoked),
        }

    @property
    def authority_id(self):
        return sha(self.descriptor)


@dataclass(frozen=True)
class RecoveryIntent:
    old_authority_id: str
    old_authority_version: int
    old_authority_generation: int
    new_authority: dict
    recovery_authority_id: str
    recovery_generation: int

    @property
    def payload(self):
        return {
            "kind": "provider-rotation-authority-break-glass-recovery",
            "old_authority_id": self.old_authority_id,
            "old_authority_version": self.old_authority_version,
            "old_authority_generation": self.old_authority_generation,
            "new_authority": self.new_authority,
            "recovery_authority_id": self.recovery_authority_id,
            "recovery_generation": self.recovery_generation,
        }

    @property
    def intent_digest(self):
        return sha(self.payload)


@dataclass(frozen=True)
class RecoveryProof:
    intent_digest: str
    recovery_authority_id: str
    recovery_generation: int
    signatures: tuple[Signature, ...]


def verify_recovery_threshold(
    recovery: RecoveryAuthority, intent: RecoveryIntent, proof: RecoveryProof
):
    recovery.validate()
    if (
        intent.recovery_authority_id != recovery.authority_id
        or intent.recovery_generation != recovery.generation
    ):
        raise RecoveryAuthorityMismatch("intent recovery authority mismatch")
    if (
        proof.intent_digest != intent.intent_digest
        or proof.recovery_authority_id != recovery.authority_id
        or proof.recovery_generation != recovery.generation
    ):
        raise RecoveryProofSubstitution("recovery proof does not bind exact intent")
    seen = set()
    valid = []
    revoked = set(recovery.revoked)
    for sig in proof.signatures:
        if sig.signer_id in seen:
            continue
        seen.add(sig.signer_id)
        if sig.signer_id in revoked:
            continue
        hx = recovery.keys.get(sig.signer_id)
        if hx is None:
            continue
        if hmac.compare_digest(mac(bytes.fromhex(hx), intent.payload), sig.signature):
            valid.append(sig.signer_id)
    if len(valid) < recovery.threshold:
        raise ThresholdNotMet(
            f"recovery valid={len(valid)} threshold={recovery.threshold}"
        )
    return tuple(sorted(valid))


class DurableRecoveryController:
    """Reference LAB-084 recovery layer over LAB-083's SQLite authority store."""

    def __init__(
        self,
        path,
        rotation_store: DurableRotationAuthority,
        bootstrap_recovery: RecoveryAuthority,
    ):
        bootstrap_recovery.validate()
        self.path = str(path)
        self.rotation_store = rotation_store
        self.bootstrap_recovery = bootstrap_recovery
        q = self._con()
        try:
            q.executescript(
                """
                CREATE TABLE IF NOT EXISTS provider_rotation_recovery_authorities(
                  authority_id TEXT PRIMARY KEY,
                  name TEXT NOT NULL,
                  generation INTEGER NOT NULL,
                  threshold INTEGER NOT NULL,
                  keys_json TEXT NOT NULL,
                  revoked_json TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS provider_rotation_recovery_head(
                  singleton INTEGER PRIMARY KEY CHECK(singleton=1),
                  authority_id TEXT NOT NULL,
                  generation INTEGER NOT NULL
                );
                CREATE TABLE IF NOT EXISTS provider_rotation_recovery_transitions(
                  new_rotation_authority_id TEXT PRIMARY KEY,
                  old_rotation_authority_id TEXT NOT NULL,
                  old_rotation_version INTEGER NOT NULL,
                  old_rotation_generation INTEGER NOT NULL,
                  recovery_authority_id TEXT NOT NULL,
                  recovery_generation INTEGER NOT NULL,
                  intent_digest TEXT NOT NULL,
                  signatures_json TEXT NOT NULL
                );
                """
            )
            if q.execute(
                "SELECT COUNT(*) FROM provider_rotation_recovery_head"
            ).fetchone()[0] == 0:
                self._insert_recovery_locked(q, bootstrap_recovery)
                q.execute(
                    "INSERT INTO provider_rotation_recovery_head VALUES(1,?,?)",
                    (
                        bootstrap_recovery.authority_id,
                        bootstrap_recovery.generation,
                    ),
                )
            q.commit()
        finally:
            q.close()
        self.verify_durable()

    def _con(self):
        q = sqlite3.connect(self.path, timeout=5, isolation_level=None)
        q.execute("PRAGMA busy_timeout=5000")
        return q

    @staticmethod
    def _encode_signatures(signatures: Iterable[Signature]):
        return json.dumps(
            [
                {"signer_id": s.signer_id, "signature": s.signature}
                for s in signatures
            ],
            sort_keys=True,
            separators=(",", ":"),
        )

    @staticmethod
    def _decode_signatures(raw):
        try:
            values = json.loads(raw)
            if not isinstance(values, list):
                raise ValueError()
            return tuple(
                Signature(v["signer_id"], v["signature"]) for v in values
            )
        except Exception as exc:
            raise RecoveryError("invalid persisted recovery signatures") from exc

    def _insert_recovery_locked(self, q, recovery: RecoveryAuthority):
        recovery.validate()
        expected = (
            recovery.name,
            recovery.generation,
            recovery.threshold,
            json.dumps(recovery.keys, sort_keys=True, separators=(",", ":")),
            json.dumps(sorted(recovery.revoked), separators=(",", ":")),
        )
        q.execute(
            "INSERT OR IGNORE INTO provider_rotation_recovery_authorities VALUES(?,?,?,?,?,?)",
            (recovery.authority_id, *expected),
        )
        stored = q.execute(
            "SELECT name,generation,threshold,keys_json,revoked_json "
            "FROM provider_rotation_recovery_authorities WHERE authority_id=?",
            (recovery.authority_id,),
        ).fetchone()
        if stored != expected:
            raise RecoveryError("recovery authority substitution")

    def _load_recovery_locked(self, q, authority_id):
        row = q.execute(
            "SELECT name,generation,threshold,keys_json,revoked_json "
            "FROM provider_rotation_recovery_authorities WHERE authority_id=?",
            (authority_id,),
        ).fetchone()
        if row is None:
            raise RecoveryError("missing recovery authority")
        recovery = RecoveryAuthority(
            row[0],
            row[1],
            row[2],
            dict(json.loads(row[3])),
            tuple(json.loads(row[4])),
        )
        recovery.validate()
        if recovery.authority_id != authority_id:
            raise RecoveryError("recovery authority digest mismatch")
        return recovery

    def current_recovery_locked(self, q):
        row = q.execute(
            "SELECT authority_id,generation FROM provider_rotation_recovery_head "
            "WHERE singleton=1"
        ).fetchone()
        if row is None:
            raise RecoveryError("missing recovery head")
        recovery = self._load_recovery_locked(q, row[0])
        if recovery.generation != row[1]:
            raise RecoveryError("recovery head mismatch")
        return recovery

    @staticmethod
    def make_intent(
        old: RotationAuthority,
        new: RotationAuthority,
        recovery: RecoveryAuthority,
    ):
        return RecoveryIntent(
            old.authority_id,
            old.version,
            old.generation,
            new.descriptor,
            recovery.authority_id,
            recovery.generation,
        )

    def recover_locked(
        self,
        q,
        new_authority: RotationAuthority,
        recovery_signatures: tuple[Signature, ...],
    ):
        old = self.rotation_store.current_locked(q)
        recovery = self.current_recovery_locked(q)
        new_authority.validate()
        if new_authority.authority_name != old.authority_name:
            raise InvalidAuthority("authority name changed during recovery")
        if (
            new_authority.version != old.version + 1
            or new_authority.generation != old.generation + 1
        ):
            raise StaleAuthority("recovery must advance authority exactly one")
        intent = self.make_intent(old, new_authority, recovery)
        proof = RecoveryProof(
            intent.intent_digest,
            recovery.authority_id,
            recovery.generation,
            tuple(recovery_signatures),
        )
        signers = verify_recovery_threshold(recovery, intent, proof)

        existing = q.execute(
            "SELECT old_rotation_authority_id,old_rotation_version,"
            "old_rotation_generation,recovery_authority_id,recovery_generation,"
            "intent_digest,signatures_json "
            "FROM provider_rotation_recovery_transitions "
            "WHERE new_rotation_authority_id=?",
            (new_authority.authority_id,),
        ).fetchone()
        expected = (
            old.authority_id,
            old.version,
            old.generation,
            recovery.authority_id,
            recovery.generation,
            intent.intent_digest,
            self._encode_signatures(recovery_signatures),
        )
        if existing is not None and existing != expected:
            raise RecoveryProofSubstitution("recovery transition substitution")
        if existing is None:
            self.rotation_store._insert_authority_locked(q, new_authority)
            q.execute(
                "INSERT INTO provider_rotation_recovery_transitions "
                "VALUES(?,?,?,?,?,?,?,?)",
                (new_authority.authority_id, *expected),
            )
        changed = q.execute(
            "UPDATE provider_rotation_authority_head "
            "SET authority_id=?,version=?,generation=? "
            "WHERE singleton=1 AND authority_id=? AND version=? AND generation=?",
            (
                new_authority.authority_id,
                new_authority.version,
                new_authority.generation,
                old.authority_id,
                old.version,
                old.generation,
            ),
        ).rowcount
        if changed != 1:
            raise StaleAuthority("rotation authority head changed during recovery")
        return {
            "kind": "recovery",
            "old_authority_id": old.authority_id,
            "new_authority_id": new_authority.authority_id,
            "recovery_authority_id": recovery.authority_id,
            "recovery_generation": recovery.generation,
            "recovery_signers": signers,
        }

    def recover(self, new_authority, recovery_signatures):
        q = self._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            out = self.recover_locked(q, new_authority, recovery_signatures)
            q.commit()
            return out
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()

    def verify_recovery_transition_locked(
        self, q, old: RotationAuthority, new: RotationAuthority
    ):
        row = q.execute(
            "SELECT old_rotation_authority_id,old_rotation_version,"
            "old_rotation_generation,recovery_authority_id,recovery_generation,"
            "intent_digest,signatures_json "
            "FROM provider_rotation_recovery_transitions "
            "WHERE new_rotation_authority_id=?",
            (new.authority_id,),
        ).fetchone()
        if row is None:
            raise RecoveryError("missing recovery transition")
        if (row[0], row[1], row[2]) != (
            old.authority_id,
            old.version,
            old.generation,
        ):
            raise RecoveryProofSubstitution("recovery predecessor mismatch")
        current_recovery = self.current_recovery_locked(q)
        if (row[3], row[4]) != (
            current_recovery.authority_id,
            current_recovery.generation,
        ):
            raise RecoveryAuthorityMismatch(
                "recovery transition does not bind authoritative recovery head"
            )
        recovery = self._load_recovery_locked(q, row[3])
        if recovery.generation != row[4]:
            raise RecoveryProofSubstitution("recovery generation mismatch")
        intent = self.make_intent(old, new, recovery)
        proof = RecoveryProof(
            row[5], row[3], row[4], self._decode_signatures(row[6])
        )
        verify_recovery_threshold(recovery, intent, proof)
        return True

    def verify_durable(self):
        q = self._con()
        try:
            q.execute("BEGIN")
            heads = q.execute(
                "SELECT authority_id,generation FROM provider_rotation_recovery_head "
                "WHERE singleton=1"
            ).fetchall()
            if len(heads) != 1:
                raise RecoveryError("missing/duplicate recovery head")
            current = self._load_recovery_locked(q, heads[0][0])
            if current.generation != heads[0][1]:
                raise RecoveryError("recovery head generation mismatch")
            if current.authority_id != self.bootstrap_recovery.authority_id:
                raise RecoveryAuthorityMismatch("recovery bootstrap/head substitution")

            rows = q.execute(
                "SELECT new_rotation_authority_id,old_rotation_authority_id "
                "FROM provider_rotation_recovery_transitions"
            ).fetchall()
            for new_id, old_id in rows:
                old = self.rotation_store._load_locked(q, old_id)
                new = self.rotation_store._load_locked(q, new_id)
                if (
                    new.authority_name != old.authority_name
                    or new.version != old.version + 1
                    or new.generation != old.generation + 1
                ):
                    raise RecoveryProofSubstitution(
                        "persisted recovery authority continuity mismatch"
                    )
                self.verify_recovery_transition_locked(q, old, new)
            q.commit()
            return True
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()


class UnsafeSelfAuthorizedRecovery:
    @staticmethod
    def allows(normal_authority_quorum_valid: bool):
        return bool(normal_authority_quorum_valid)
