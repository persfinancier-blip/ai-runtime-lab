from __future__ import annotations

import hashlib
import hmac
import json
import sqlite3
import threading
from dataclasses import dataclass
from pathlib import Path


class JournalError(RuntimeError):
    pass


class RequestConflict(JournalError):
    pass


class StaleCredential(JournalError):
    pass


class UnknownOutcome(JournalError):
    pass


class CorruptJournal(JournalError):
    pass


class PendingEffects(JournalError):
    pass


@dataclass(frozen=True)
class Request:
    request_id: str
    task_id: str
    scope: str
    credential_generation: int
    payload: str

    def canonical(self) -> bytes:
        if not all(isinstance(x, str) and x for x in (self.request_id, self.task_id, self.scope)):
            raise JournalError("invalid request identity")
        if not isinstance(self.payload, str):
            raise JournalError("invalid payload")
        if type(self.credential_generation) is not int or self.credential_generation < 1:
            raise JournalError("invalid credential generation")
        return json.dumps(
            {
                "credential_generation": self.credential_generation,
                "payload": self.payload,
                "request_id": self.request_id,
                "scope": self.scope,
                "task_id": self.task_id,
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode()

    @property
    def digest(self) -> str:
        return hashlib.sha256(self.canonical()).hexdigest()


@dataclass(frozen=True)
class Result:
    request_id: str
    outcome: str
    receipt: str
    effect_key: str


class TransactionalJournal:
    """Local SQL serialization boundary. It does not make external effects exactly-once."""

    def __init__(self, path: str | Path, generation: int = 1):
        if type(generation) is not int or generation < 1:
            raise JournalError("invalid generation")
        self.path = str(path)
        q = self._con()
        try:
            q.execute("PRAGMA journal_mode=WAL")
            q.executescript(
                """
                CREATE TABLE IF NOT EXISTS broker_meta(
                  singleton INTEGER PRIMARY KEY CHECK(singleton=1),
                  credential_generation INTEGER NOT NULL CHECK(credential_generation>=1)
                );
                CREATE TABLE IF NOT EXISTS broker_requests(
                  request_id TEXT PRIMARY KEY,
                  request_digest TEXT NOT NULL,
                  task_id TEXT NOT NULL,
                  scope TEXT NOT NULL,
                  credential_generation INTEGER NOT NULL,
                  effect_key TEXT NOT NULL UNIQUE,
                  status TEXT NOT NULL CHECK(status IN ('INTENT','UNKNOWN','CONFIRMED')),
                  receipt TEXT
                );
                """
            )
            row = q.execute("SELECT credential_generation FROM broker_meta WHERE singleton=1").fetchone()
            if row is None:
                q.execute("INSERT INTO broker_meta VALUES(1,?)", (generation,))
                q.commit()
            elif row[0] != generation:
                raise StaleCredential("supplied generation does not match durable journal")
        finally:
            q.close()

    def _con(self):
        q = sqlite3.connect(self.path, timeout=5, isolation_level=None, check_same_thread=False)
        q.execute("PRAGMA busy_timeout=5000")
        return q

    def generation(self) -> int:
        q = self._con()
        try:
            return q.execute("SELECT credential_generation FROM broker_meta WHERE singleton=1").fetchone()[0]
        finally:
            q.close()

    def rotate(self) -> int:
        q = self._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            current = q.execute("SELECT credential_generation FROM broker_meta WHERE singleton=1").fetchone()[0]
            unresolved = q.execute(
                """
                SELECT COUNT(*) FROM broker_requests
                WHERE credential_generation=? AND status IN ('INTENT','UNKNOWN')
                """,
                (current,),
            ).fetchone()[0]
            if unresolved:
                raise PendingEffects(
                    f"credential rotation blocked by {unresolved} unresolved request(s)"
                )
            nxt = current + 1
            q.execute("UPDATE broker_meta SET credential_generation=? WHERE singleton=1", (nxt,))
            q.commit()
            return nxt
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()

    @staticmethod
    def _effect_key(request: Request) -> str:
        return "broker-effect:" + hashlib.sha256(
            (request.request_id + "\0" + request.digest).encode()
        ).hexdigest()

    def reserve(self, request: Request) -> tuple[str, str, str | None]:
        digest = request.digest
        q = self._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            row = q.execute(
                "SELECT request_digest,status,effect_key,receipt FROM broker_requests WHERE request_id=?",
                (request.request_id,),
            ).fetchone()
            if row is not None:
                prior_digest, status, effect_key, receipt = row
                if prior_digest != digest:
                    raise RequestConflict("request_id reused with different content")
                q.commit()
                return status, effect_key, receipt

            current_generation = q.execute(
                "SELECT credential_generation FROM broker_meta WHERE singleton=1"
            ).fetchone()[0]
            if request.credential_generation != current_generation:
                raise StaleCredential("new request uses stale credential generation")
            effect_key = self._effect_key(request)
            q.execute(
                """
                INSERT INTO broker_requests(
                  request_id,request_digest,task_id,scope,credential_generation,effect_key,status,receipt
                ) VALUES(?,?,?,?,?,?,'INTENT',NULL)
                """,
                (
                    request.request_id,
                    digest,
                    request.task_id,
                    request.scope,
                    request.credential_generation,
                    effect_key,
                ),
            )
            q.commit()
            return "INTENT", effect_key, None
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()

    def mark_unknown(self, request: Request) -> None:
        q = self._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            row = q.execute(
                "SELECT request_digest,status FROM broker_requests WHERE request_id=?",
                (request.request_id,),
            ).fetchone()
            if row is None or row[0] != request.digest:
                raise RequestConflict("unknown request identity")
            if row[1] != "CONFIRMED":
                q.execute(
                    "UPDATE broker_requests SET status='UNKNOWN' WHERE request_id=?",
                    (request.request_id,),
                )
            q.commit()
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()

    def confirm(self, request: Request, receipt: str) -> None:
        if not isinstance(receipt, str) or not receipt:
            raise JournalError("invalid receipt")
        q = self._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            row = q.execute(
                "SELECT request_digest,status,receipt FROM broker_requests WHERE request_id=?",
                (request.request_id,),
            ).fetchone()
            if row is None or row[0] != request.digest:
                raise RequestConflict("confirmation identity mismatch")
            if row[1] == "CONFIRMED":
                if row[2] != receipt:
                    raise RequestConflict("conflicting receipt")
                q.commit()
                return
            q.execute(
                "UPDATE broker_requests SET status='CONFIRMED',receipt=? WHERE request_id=?",
                (receipt, request.request_id),
            )
            q.commit()
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()

    def record(self, request_id: str):
        q = self._con()
        try:
            return q.execute(
                "SELECT request_digest,status,effect_key,receipt FROM broker_requests WHERE request_id=?",
                (request_id,),
            ).fetchone()
        finally:
            q.close()

    def verify_durable(self) -> bool:
        q = self._con()
        try:
            meta = q.execute("SELECT singleton,credential_generation FROM broker_meta").fetchall()
            if len(meta) != 1 or meta[0][0] != 1 or type(meta[0][1]) is not int or meta[0][1] < 1:
                raise CorruptJournal("invalid meta")
            rows = q.execute(
                "SELECT request_id,request_digest,credential_generation,effect_key,status,receipt FROM broker_requests"
            ).fetchall()
            seen_effects = set()
            for rid, digest, generation, effect_key, status, receipt in rows:
                if not isinstance(rid, str) or not rid:
                    raise CorruptJournal("invalid request id")
                if (
                    not isinstance(digest, str)
                    or len(digest) != 64
                    or any(char not in "0123456789abcdef" for char in digest)
                ):
                    raise CorruptJournal("invalid digest")
                if type(generation) is not int or generation < 1 or generation > meta[0][1]:
                    raise CorruptJournal("invalid generation")
                if not isinstance(effect_key, str) or not effect_key or effect_key in seen_effects:
                    raise CorruptJournal("invalid effect key")
                seen_effects.add(effect_key)
                if status not in {"INTENT", "UNKNOWN", "CONFIRMED"}:
                    raise CorruptJournal("invalid status")
                if status == "CONFIRMED" and (not isinstance(receipt, str) or not receipt):
                    raise CorruptJournal("missing receipt")
                if status != "CONFIRMED" and receipt is not None:
                    raise CorruptJournal("premature receipt")
            return True
        finally:
            q.close()


class IdempotentSink:
    """Separate durable side-effect simulator with a UNIQUE effect identity."""

    def __init__(self, path: str | Path):
        self.path = str(path)
        q = self._con()
        try:
            q.executescript(
                """
                CREATE TABLE IF NOT EXISTS sink_effects(
                  effect_key TEXT PRIMARY KEY,
                  payload_digest TEXT NOT NULL,
                  receipt TEXT NOT NULL
                );
                """
            )
        finally:
            q.close()

    def _con(self):
        q = sqlite3.connect(self.path, timeout=5, isolation_level=None, check_same_thread=False)
        q.execute("PRAGMA busy_timeout=5000")
        return q

    def apply(self, effect_key: str, payload: str, secret: bytes, *, timeout_after_commit=False) -> str:
        payload_digest = hashlib.sha256(payload.encode()).hexdigest()
        receipt = "sink-receipt:" + hmac.new(
            secret, (effect_key + "\0" + payload_digest).encode(), hashlib.sha256
        ).hexdigest()
        q = self._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            row = q.execute(
                "SELECT payload_digest,receipt FROM sink_effects WHERE effect_key=?",
                (effect_key,),
            ).fetchone()
            if row is None:
                q.execute(
                    "INSERT INTO sink_effects VALUES(?,?,?)",
                    (effect_key, payload_digest, receipt),
                )
            else:
                if row[0] != payload_digest:
                    raise RequestConflict("effect key reused for different payload")
                receipt = row[1]
            q.commit()
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()
        if timeout_after_commit:
            raise UnknownOutcome(effect_key)
        return receipt

    def lookup(self, effect_key: str) -> str | None:
        q = self._con()
        try:
            row = q.execute(
                "SELECT receipt FROM sink_effects WHERE effect_key=?", (effect_key,)
            ).fetchone()
            return None if row is None else row[0]
        finally:
            q.close()

    def apply_count(self) -> int:
        q = self._con()
        try:
            return q.execute("SELECT COUNT(*) FROM sink_effects").fetchone()[0]
        finally:
            q.close()


class BrokerWorker:
    def __init__(self, journal: TransactionalJournal, sink: IdempotentSink, secret: bytes):
        self.journal = journal
        self.sink = sink
        self.secret = bytes(secret)

    def process(self, request: Request, *, timeout_after_commit=False) -> Result:
        status, effect_key, receipt = self.journal.reserve(request)
        if status == "CONFIRMED":
            assert receipt is not None
            return Result(request.request_id, "ALREADY_COMMITTED", receipt, effect_key)

        observed = self.sink.lookup(effect_key)
        if observed is not None:
            self.journal.confirm(request, observed)
            return Result(request.request_id, "RECONCILED", observed, effect_key)

        try:
            receipt = self.sink.apply(
                effect_key,
                request.payload,
                self.secret,
                timeout_after_commit=timeout_after_commit,
            )
        except UnknownOutcome:
            self.journal.mark_unknown(request)
            raise
        self.journal.confirm(request, receipt)
        return Result(request.request_id, "COMMITTED", receipt, effect_key)


class UnsafeCheckThenApply:
    """Deliberately unsafe concurrent check-then-act baseline."""

    def __init__(self):
        self.effects: dict[str, str] = {}
        self.apply_count = 0
        self._lock = threading.Lock()

    def process_with_barrier(self, request: Request, barrier: threading.Barrier) -> str:
        if request.request_id in self.effects:
            return self.effects[request.request_id]
        barrier.wait(timeout=5)
        # Side effect is intentionally non-idempotent and happens before durable identity.
        with self._lock:
            self.apply_count += 1
            receipt = f"unsafe:{self.apply_count}"
        self.effects[request.request_id] = receipt
        return receipt
