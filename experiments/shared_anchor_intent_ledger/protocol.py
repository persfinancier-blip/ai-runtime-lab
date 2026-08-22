from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path

from experiments.anchor_attestation.protocol import AttestedCatchup


class SharedAnchorError(RuntimeError):
    pass


class IntentConflict(SharedAnchorError):
    pass


class IntentGap(SharedAnchorError):
    pass


class IntentSubstitution(SharedAnchorError):
    pass


class PendingIntent(SharedAnchorError):
    pass


class ProviderMismatch(SharedAnchorError):
    pass


class UnexplainedAdvance(SharedAnchorError):
    pass


ALLOWED_INTENT_TYPES = {"migration", "root_rotation", "archive_checkpoint"}


def canon(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def sha(obj) -> str:
    return hashlib.sha256(canon(obj)).hexdigest()


@dataclass(frozen=True)
class Intent:
    intent_id: str
    component_id: str
    intent_type: str
    payload: dict

    def validate(self):
        if not all(isinstance(x, str) and x for x in (self.intent_id, self.component_id)):
            raise IntentSubstitution("invalid intent identity")
        if self.intent_type not in ALLOWED_INTENT_TYPES:
            raise IntentSubstitution("unknown intent type")
        if not isinstance(self.payload, dict):
            raise IntentSubstitution("payload must be an object")
        return self

    @property
    def payload_digest(self):
        self.validate()
        return sha(
            {
                "component_id": self.component_id,
                "intent_type": self.intent_type,
                "payload": self.payload,
            }
        )


@dataclass(frozen=True)
class LedgerEntry:
    intent_id: str
    component_id: str
    intent_type: str
    payload_digest: str
    provider_id: str
    provider_generation: int
    predecessor_position: int
    position: int
    request_id: str
    status: str
    receipt_binding: str | None


class SharedAnchorLedger:
    def __init__(self, path: str | Path, attested: AttestedCatchup):
        if type(attested) is not AttestedCatchup:
            raise TypeError("exact LAB-036 AttestedCatchup required")
        self.path = str(path)
        self.attested = attested
        self._init()

    def _con(self):
        q = sqlite3.connect(self.path, timeout=5, isolation_level=None)
        q.execute("PRAGMA busy_timeout=5000")
        return q

    def _init(self):
        q = self._con()
        try:
            q.executescript(
                """
                CREATE TABLE IF NOT EXISTS shared_anchor_meta(
                  singleton INTEGER PRIMARY KEY CHECK(singleton=1),
                  reserved_position INTEGER NOT NULL CHECK(reserved_position>=0)
                );
                INSERT OR IGNORE INTO shared_anchor_meta VALUES(1,0);
                CREATE TABLE IF NOT EXISTS shared_anchor_intents(
                  intent_id TEXT PRIMARY KEY,
                  component_id TEXT NOT NULL,
                  intent_type TEXT NOT NULL,
                  payload_digest TEXT NOT NULL,
                  provider_id TEXT NOT NULL,
                  provider_generation INTEGER NOT NULL,
                  predecessor_position INTEGER NOT NULL,
                  position INTEGER NOT NULL UNIQUE,
                  request_id TEXT NOT NULL UNIQUE,
                  status TEXT NOT NULL CHECK(status IN ('PREPARED','CONFIRMED')),
                  receipt_binding TEXT
                );
                CREATE TABLE IF NOT EXISTS component_anchor_watermarks(
                  component_id TEXT PRIMARY KEY,
                  position INTEGER NOT NULL CHECK(position>=0)
                );
                """
            )
            q.commit()
        finally:
            q.close()

    def _provider(self):
        expected = self.attested.verifier.expected
        return expected.provider_id, expected.generation

    @staticmethod
    def _request_id(position, intent_id, component_id, intent_type, payload_digest):
        binding = sha(
            {
                "position": position,
                "intent_id": intent_id,
                "component_id": component_id,
                "intent_type": intent_type,
                "payload_digest": payload_digest,
            }
        )
        return f"shared-anchor:{position}:{binding}"

    @staticmethod
    def _stable_receipt(obs):
        return sha(
            {
                "provider_id": obs.provider_id,
                "generation": obs.generation,
                "position": obs.position,
                "request_id": obs.request_id,
            }
        )

    @staticmethod
    def _validate_digest(value, label):
        if (
            not isinstance(value, str)
            or len(value) != 64
            or any(c not in "0123456789abcdef" for c in value)
        ):
            raise IntentSubstitution(f"invalid {label}")

    def _row_entry(self, row):
        if row is None:
            raise IntentSubstitution("missing ledger entry")
        entry = LedgerEntry(*row)
        self._validate_digest(entry.payload_digest, "payload digest")
        if entry.status not in {"PREPARED", "CONFIRMED"}:
            raise IntentSubstitution("invalid status")
        if type(entry.provider_generation) is not int or entry.provider_generation < 1:
            raise IntentSubstitution("invalid provider generation")
        if (
            type(entry.predecessor_position) is not int
            or type(entry.position) is not int
            or entry.position != entry.predecessor_position + 1
        ):
            raise IntentSubstitution("invalid position/predecessor")
        if not all(
            isinstance(x, str) and x
            for x in (entry.intent_id, entry.component_id)
        ):
            raise IntentSubstitution("invalid durable intent identity")
        if entry.intent_type not in ALLOWED_INTENT_TYPES:
            raise IntentSubstitution("unknown durable intent type")
        expected_request = self._request_id(
            entry.position,
            entry.intent_id,
            entry.component_id,
            entry.intent_type,
            entry.payload_digest,
        )
        if entry.request_id != expected_request:
            raise IntentSubstitution("request identity mismatch")
        if entry.status == "PREPARED" and entry.receipt_binding is not None:
            raise IntentSubstitution("prepared entry has receipt")
        if entry.status == "CONFIRMED":
            self._validate_digest(entry.receipt_binding, "receipt binding")
        return entry

    def reserve(self, intent: Intent):
        intent.validate()
        provider_id, generation = self._provider()
        q = self._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            existing = q.execute(
                "SELECT intent_id,component_id,intent_type,payload_digest,provider_id,provider_generation,"
                "predecessor_position,position,request_id,status,receipt_binding "
                "FROM shared_anchor_intents WHERE intent_id=?",
                (intent.intent_id,),
            ).fetchone()
            if existing is not None:
                entry = self._row_entry(existing)
                if (
                    entry.component_id != intent.component_id
                    or entry.intent_type != intent.intent_type
                    or entry.payload_digest != intent.payload_digest
                ):
                    raise IntentConflict("intent_id reused with different content")
                q.commit()
                return entry

            pending = q.execute(
                "SELECT COUNT(*) FROM shared_anchor_intents WHERE status='PREPARED'"
            ).fetchone()[0]
            if pending:
                raise PendingIntent("another anchor intent is unresolved")
            predecessor = q.execute(
                "SELECT reserved_position FROM shared_anchor_meta WHERE singleton=1"
            ).fetchone()[0]
            position = predecessor + 1
            request_id = self._request_id(
                position,
                intent.intent_id,
                intent.component_id,
                intent.intent_type,
                intent.payload_digest,
            )
            q.execute(
                "INSERT INTO shared_anchor_intents VALUES(?,?,?,?,?,?,?,?,?,'PREPARED',NULL)",
                (
                    intent.intent_id,
                    intent.component_id,
                    intent.intent_type,
                    intent.payload_digest,
                    provider_id,
                    generation,
                    predecessor,
                    position,
                    request_id,
                ),
            )
            q.execute(
                "UPDATE shared_anchor_meta SET reserved_position=? WHERE singleton=1 AND reserved_position=?",
                (position, predecessor),
            )
            q.commit()
            return self.entry(intent.intent_id)
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()

    def entry(self, intent_id):
        q = self._con()
        try:
            return self._row_entry(
                q.execute(
                    "SELECT intent_id,component_id,intent_type,payload_digest,provider_id,provider_generation,"
                    "predecessor_position,position,request_id,status,receipt_binding "
                    "FROM shared_anchor_intents WHERE intent_id=?",
                    (intent_id,),
                ).fetchone()
            )
        finally:
            q.close()

    def _reauthenticate(self, entry: LedgerEntry):
        provider_id, generation = self._provider()
        if (entry.provider_id, entry.provider_generation) != (provider_id, generation):
            raise ProviderMismatch("ledger entry provider generation is not current")
        challenge = self.attested.challenge()
        obs = self.attested.provider.reconcile_increment(
            challenge=challenge, request_id=entry.request_id
        )
        if obs is None:
            raise UnexplainedAdvance("provider has no result for ledger request")
        verified = self.attested.verifier.verify(
            obs, expected_challenge=challenge, allowed_kinds={"RECONCILE"}
        )
        if verified.position != entry.position or verified.request_id != entry.request_id:
            raise UnexplainedAdvance("provider result does not bind ledger position/request")
        return self._stable_receipt(verified)

    def execute(self, intent: Intent, *, timeout_after_commit=False):
        entry = self.reserve(intent)
        if entry.status == "CONFIRMED":
            receipt = self._reauthenticate(entry)
            if receipt != entry.receipt_binding:
                raise IntentSubstitution("confirmed receipt binding changed")
            return entry
        try:
            self.attested.catch_up_one(
                db_sequence=entry.position,
                request_id=entry.request_id,
                timeout_after_commit=timeout_after_commit,
            )
            receipt = self._reauthenticate(entry)
        except Exception as exc:
            raise PendingIntent(str(exc)) from exc
        q = self._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            current = self._row_entry(
                q.execute(
                    "SELECT intent_id,component_id,intent_type,payload_digest,provider_id,provider_generation,"
                    "predecessor_position,position,request_id,status,receipt_binding "
                    "FROM shared_anchor_intents WHERE intent_id=?",
                    (intent.intent_id,),
                ).fetchone()
            )
            if current != entry:
                raise IntentSubstitution("ledger entry changed before confirmation")
            q.execute(
                "UPDATE shared_anchor_intents SET status='CONFIRMED',receipt_binding=? "
                "WHERE intent_id=? AND status='PREPARED' AND receipt_binding IS NULL",
                (receipt, intent.intent_id),
            )
            q.commit()
            return self.entry(intent.intent_id)
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()

    def watermark(self, component_id):
        q = self._con()
        try:
            row = q.execute(
                "SELECT position FROM component_anchor_watermarks WHERE component_id=?",
                (component_id,),
            ).fetchone()
            return 0 if row is None else row[0]
        finally:
            q.close()

    def verify_component(self, component_id):
        if not isinstance(component_id, str) or not component_id:
            raise IntentSubstitution("invalid component")
        challenge = self.attested.challenge()
        observed = self.attested.authenticated_read(
            challenge=challenge, request_id=f"shared-ledger-read:{component_id}"
        )
        provider_id, generation = self._provider()
        if (observed.provider_id, observed.generation) != (provider_id, generation):
            raise ProviderMismatch("read provider mismatch")
        local = self.watermark(component_id)
        if observed.position < local:
            raise UnexplainedAdvance("external anchor rolled back below component watermark")
        if observed.position == local:
            return local

        q = self._con()
        try:
            rows = q.execute(
                "SELECT intent_id,component_id,intent_type,payload_digest,provider_id,provider_generation,"
                "predecessor_position,position,request_id,status,receipt_binding "
                "FROM shared_anchor_intents WHERE position>? AND position<=? ORDER BY position",
                (local, observed.position),
            ).fetchall()
        finally:
            q.close()
        if len(rows) != observed.position - local:
            raise IntentGap("missing ledger position")
        expected = local + 1
        for row in rows:
            entry = self._row_entry(row)
            if entry.position != expected or entry.predecessor_position != expected - 1:
                raise IntentGap("non-contiguous ledger history")
            if entry.status != "CONFIRMED":
                raise UnexplainedAdvance("ahead position is not confirmed")
            receipt = self._reauthenticate(entry)
            if receipt != entry.receipt_binding:
                raise IntentSubstitution("stored receipt differs from authenticated provider result")
            expected += 1

        q = self._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            # Re-read the exact ledger slice after external verification.  The
            # watermark may advance only if the rows we authenticated are still
            # byte-for-byte the authoritative rows at the commit boundary.
            current_rows = q.execute(
                "SELECT intent_id,component_id,intent_type,payload_digest,provider_id,provider_generation,"
                "predecessor_position,position,request_id,status,receipt_binding "
                "FROM shared_anchor_intents WHERE position>? AND position<=? ORDER BY position",
                (local, observed.position),
            ).fetchall()
            if current_rows != rows:
                raise IntentSubstitution("ledger changed after external verification")
            prior = q.execute(
                "SELECT position FROM component_anchor_watermarks WHERE component_id=?",
                (component_id,),
            ).fetchone()
            if prior is None:
                q.execute(
                    "INSERT INTO component_anchor_watermarks VALUES(?,?)",
                    (component_id, observed.position),
                )
            elif prior[0] != local:
                raise IntentConflict("component watermark changed during verification")
            else:
                q.execute(
                    "UPDATE component_anchor_watermarks SET position=? WHERE component_id=? AND position=?",
                    (observed.position, component_id, local),
                )
            q.commit()
            return observed.position
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()


class UnsafeMonotonicOnly:
    @staticmethod
    def accepts(local_position, external_position):
        return external_position >= local_position
