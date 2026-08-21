from __future__ import annotations

import hashlib
import hmac
import json
import os
import socket
import struct
import tempfile
from dataclasses import dataclass
from pathlib import Path


class BrokerError(RuntimeError): pass
class UnauthorizedSender(BrokerError): pass
class StaleCredential(BrokerError): pass
class InvalidRequest(BrokerError): pass
class UnknownOutcome(BrokerError): pass
class DurableStateError(BrokerError): pass

_UCRED = struct.Struct("3i")
_STATE_SCHEMA = 1


def proc_starttime(pid: int) -> int:
    text = Path(f"/proc/{pid}/stat").read_text()
    rest = text[text.rfind(")") + 2 :].split()
    return int(rest[19])


@dataclass(frozen=True)
class OperationPermit:
    task_id: str
    scope: str
    credential_generation: int
    target_pid: int
    target_starttime: int


@dataclass(frozen=True)
class BrokerEvidence:
    request_id: str
    sender_pid: int
    task_id: str
    scope: str
    credential_generation: int
    outcome: str
    receipt: str | None


@dataclass(frozen=True)
class ReceivedRequest:
    body: dict
    sender_pid: int
    sender_uid: int
    sender_gid: int


def credential_socketpair() -> tuple[socket.socket, socket.socket]:
    broker, sender = socket.socketpair(socket.AF_UNIX, socket.SOCK_DGRAM)
    broker.setsockopt(socket.SOL_SOCKET, socket.SO_PASSCRED, 1)
    return broker, sender


def recv_kernel_request(sock: socket.socket) -> ReceivedRequest:
    data, ancillary, _flags, _addr = sock.recvmsg(64 * 1024, socket.CMSG_SPACE(_UCRED.size))
    creds = []
    for level, kind, raw in ancillary:
        if level == socket.SOL_SOCKET and kind == socket.SCM_CREDENTIALS:
            creds.append(_UCRED.unpack(raw[: _UCRED.size]))
    if len(creds) != 1:
        raise UnauthorizedSender("exactly one kernel SCM_CREDENTIALS record required")
    pid, uid, gid = creds[0]
    try:
        body = json.loads(data.decode("utf-8"))
    except Exception as exc:
        raise InvalidRequest("invalid JSON request") from exc
    if not isinstance(body, dict):
        raise InvalidRequest("request must be an object")
    return ReceivedRequest(body, pid, uid, gid)


class CredentialBroker:
    """Reference operation broker: raw secret bytes never leave this object or durable state."""

    def __init__(self, secret: bytes, generation: int = 1, *, state_path: str | Path | None = None):
        self._secret = bytes(secret)
        self._state_path = None if state_path is None else Path(state_path)
        self._pidfds: dict[tuple[int, int], int] = {}
        self._permits: dict[tuple[str, str], OperationPermit] = {}
        self._effects: dict[str, tuple[str, str]] = {}
        if type(generation) is not int or generation < 1:
            raise DurableStateError("invalid supplied credential generation")
        self.generation = generation
        self.apply_count = 0
        if self._state_path is not None and self._state_path.exists():
            supplied_generation = generation
            self._load_state()
            if self.generation != supplied_generation:
                raise StaleCredential("supplied credential generation does not match durable broker state")
        elif self._state_path is not None:
            self._persist_state()

    def _state_dict(self) -> dict:
        return {
            "schema_version": _STATE_SCHEMA,
            "generation": self.generation,
            "permits": [p.__dict__ for p in sorted(self._permits.values(), key=lambda x: (x.task_id, x.scope))],
            "effects": {rid: {"request_digest": pair[0], "receipt": pair[1]} for rid, pair in sorted(self._effects.items())},
            "apply_count": self.apply_count,
        }

    def _persist_state(self) -> None:
        if self._state_path is None:
            return
        self._state_path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(prefix=self._state_path.name + ".", dir=str(self._state_path.parent))
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                json.dump(self._state_dict(), fh, sort_keys=True, separators=(",", ":"))
                fh.flush(); os.fsync(fh.fileno())
            os.replace(tmp, self._state_path)
            dfd = os.open(self._state_path.parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
            try: os.fsync(dfd)
            finally: os.close(dfd)
        finally:
            if os.path.exists(tmp): os.unlink(tmp)

    def _load_state(self) -> None:
        try:
            raw = json.loads(self._state_path.read_text(encoding="utf-8"))
        except Exception as exc:
            raise DurableStateError("invalid durable broker state") from exc
        required = {"schema_version", "generation", "permits", "effects", "apply_count"}
        if not isinstance(raw, dict) or set(raw) != required:
            raise DurableStateError("invalid durable broker state shape")
        if type(raw["schema_version"]) is not int or raw["schema_version"] != _STATE_SCHEMA:
            raise DurableStateError("unsupported durable broker state")
        if type(raw["generation"]) is not int or raw["generation"] < 1:
            raise DurableStateError("invalid durable credential generation")
        if type(raw["apply_count"]) is not int or raw["apply_count"] < 0:
            raise DurableStateError("invalid durable apply_count")
        if not isinstance(raw["effects"], dict) or not isinstance(raw["permits"], list):
            raise DurableStateError("invalid durable collections")
        self.generation = raw["generation"]
        self.apply_count = raw["apply_count"]
        self._effects = {}
        for rid, item in raw["effects"].items():
            if not isinstance(rid, str) or not rid:
                raise DurableStateError("invalid durable request id")
            if not isinstance(item, dict) or set(item) != {"request_digest", "receipt"}:
                raise DurableStateError("invalid durable effect")
            request_digest, receipt = item["request_digest"], item["receipt"]
            if (
                not isinstance(request_digest, str)
                or len(request_digest) != 64
                or any(ch not in "0123456789abcdef" for ch in request_digest)
                or not isinstance(receipt, str)
                or not receipt
            ):
                raise DurableStateError("invalid durable effect identity")
            self._effects[rid] = (request_digest, receipt)
        if self.apply_count != len(self._effects):
            raise DurableStateError("durable apply_count/effect cardinality mismatch")
        self._permits = {}
        permit_fields = {"task_id", "scope", "credential_generation", "target_pid", "target_starttime"}
        for item in raw["permits"]:
            if not isinstance(item, dict) or set(item) != permit_fields:
                raise DurableStateError("invalid durable permit shape")
            if not isinstance(item["task_id"], str) or not item["task_id"]:
                raise DurableStateError("invalid durable permit task")
            if not isinstance(item["scope"], str) or not item["scope"]:
                raise DurableStateError("invalid durable permit scope")
            if (
                type(item["credential_generation"]) is not int
                or item["credential_generation"] < 1
                or item["credential_generation"] > self.generation
                or type(item["target_pid"]) is not int
                or item["target_pid"] < 1
                or type(item["target_starttime"]) is not int
                or item["target_starttime"] < 1
            ):
                raise DurableStateError("invalid durable permit identity")
            p = OperationPermit(**item)
            key = (p.task_id, p.scope)
            if key in self._permits:
                raise DurableStateError("duplicate durable permit")
            self._permits[key] = p

    def rotate(self, secret: bytes) -> int:
        self._secret = bytes(secret)
        self.generation += 1
        self._persist_state()
        return self.generation

    def _install_pidfd(self, permit: OperationPermit) -> None:
        pidfd = os.pidfd_open(permit.target_pid, 0)
        if self._pidfd_target_pid(pidfd) != permit.target_pid or not self._pidfd_live(pidfd):
            os.close(pidfd); raise UnauthorizedSender("failed to reacquire target process instance")
        try:
            current_start = proc_starttime(permit.target_pid)
        except (FileNotFoundError, ProcessLookupError) as exc:
            os.close(pidfd); raise UnauthorizedSender("target exited during reacquisition") from exc
        if current_start != permit.target_starttime:
            os.close(pidfd); raise UnauthorizedSender("saved PID now refers to a different process instance")
        key = (permit.target_pid, permit.target_starttime)
        old = self._pidfds.pop(key, None)
        if old is not None: os.close(old)
        self._pidfds[key] = pidfd

    def permit(self, task_id: str, scope: str, target_pid: int) -> OperationPermit:
        starttime = proc_starttime(target_pid)
        permit = OperationPermit(task_id, scope, self.generation, target_pid, starttime)
        self._install_pidfd(permit)
        self._permits[(task_id, scope)] = permit
        self._persist_state()
        return permit

    def reacquire_permit(self, task_id: str, scope: str) -> OperationPermit:
        permit = self._permits.get((task_id, scope))
        if permit is None:
            raise UnauthorizedSender("no durable permit for task/scope")
        self._install_pidfd(permit)
        return permit

    @staticmethod
    def _pidfd_live(fd: int) -> bool:
        import select
        return not bool(select.select([fd], [], [], 0)[0])

    @staticmethod
    def _pidfd_target_pid(fd: int) -> int:
        for line in Path(f"/proc/self/fdinfo/{fd}").read_text().splitlines():
            if line.startswith("Pid:"):
                return int(line.split(":", 1)[1].strip())
        raise UnauthorizedSender("pidfd target identity unavailable")

    def _validate_sender(self, request: ReceivedRequest, permit: OperationPermit) -> None:
        if request.sender_pid != permit.target_pid:
            raise UnauthorizedSender(f"kernel sender pid {request.sender_pid} != authorized target {permit.target_pid}")
        fd = self._pidfds.get((permit.target_pid, permit.target_starttime))
        if fd is None:
            raise UnauthorizedSender("no live pidfd authority for target process instance")
        if not self._pidfd_live(fd) or self._pidfd_target_pid(fd) != permit.target_pid:
            raise UnauthorizedSender("target process instance is no longer live")
        try:
            starttime = proc_starttime(request.sender_pid)
        except (FileNotFoundError, ProcessLookupError) as exc:
            raise UnauthorizedSender("sender exited before instance validation") from exc
        if starttime != permit.target_starttime:
            raise UnauthorizedSender("numeric PID refers to a different process instance")

    def close(self) -> None:
        for fd in self._pidfds.values():
            try: os.close(fd)
            except OSError: pass
        self._pidfds.clear()

    @staticmethod
    def _shape_and_digest(body: dict) -> tuple[str, str]:
        required = {"request_id", "task_id", "scope", "credential_generation", "payload"}
        if set(body) != required:
            raise InvalidRequest("unexpected/missing request fields")
        if not all(isinstance(body[k], str) for k in ("request_id", "task_id", "scope", "payload")):
            raise InvalidRequest("string request fields required")
        if type(body["credential_generation"]) is not int:
            raise InvalidRequest("integer credential_generation required")
        digest = hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        return body["request_id"], digest

    def execute(self, request: ReceivedRequest, permit: OperationPermit, *, timeout_after_commit: bool = False) -> BrokerEvidence:
        self._validate_sender(request, permit)
        b = request.body
        rid, request_digest = self._shape_and_digest(b)
        if rid in self._effects:
            prior_digest, receipt = self._effects[rid]
            if prior_digest != request_digest:
                raise InvalidRequest("request_id reused with different request content")
            if b["task_id"] != permit.task_id or b["scope"] != permit.scope:
                raise InvalidRequest("task/scope binding mismatch")
            return BrokerEvidence(rid, request.sender_pid, b["task_id"], b["scope"], b["credential_generation"], "ALREADY_COMMITTED", receipt)
        if b["task_id"] != permit.task_id or b["scope"] != permit.scope:
            raise InvalidRequest("task/scope binding mismatch")
        if b["credential_generation"] != permit.credential_generation or permit.credential_generation != self.generation:
            raise StaleCredential("credential generation is no longer current")
        material = rid.encode() + b"\0" + b["task_id"].encode() + b"\0" + b["scope"].encode() + b"\0" + b["payload"].encode()
        receipt = "receipt:" + hmac.new(self._secret, material, hashlib.sha256).hexdigest()
        self._effects[rid] = (request_digest, receipt)
        self.apply_count += 1
        self._persist_state()
        if timeout_after_commit:
            raise UnknownOutcome(rid)
        return BrokerEvidence(rid, request.sender_pid, b["task_id"], b["scope"], b["credential_generation"], "COMMITTED", receipt)

    def evidence_contains_secret(self, evidence: BrokerEvidence, secret: bytes) -> bool:
        return secret.decode(errors="ignore") in json.dumps(evidence.__dict__, sort_keys=True)


class UnsafeSocketPossessionBroker:
    def __init__(self): self.apply_count = 0
    def execute(self, request: ReceivedRequest) -> str:
        self.apply_count += 1
        return f"accepted:{request.sender_pid}"
