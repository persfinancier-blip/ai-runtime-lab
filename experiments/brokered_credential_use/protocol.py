from __future__ import annotations

import hashlib
import hmac
import json
import os
import socket
import struct
from dataclasses import dataclass
from pathlib import Path


class BrokerError(RuntimeError):
    pass


class UnauthorizedSender(BrokerError):
    pass


class StaleCredential(BrokerError):
    pass


class InvalidRequest(BrokerError):
    pass


class UnknownOutcome(BrokerError):
    pass


_UCRED = struct.Struct("3i")


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
    """Reference operation broker: secret bytes never leave this object."""

    def __init__(self, secret: bytes, generation: int = 1):
        self._secret = bytes(secret)
        self.generation = generation
        self._effects: dict[str, tuple[str, str]] = {}
        self._pidfds: dict[tuple[int, int], int] = {}
        self.apply_count = 0

    def rotate(self, secret: bytes) -> int:
        self._secret = bytes(secret)
        self.generation += 1
        return self.generation

    def permit(self, task_id: str, scope: str, target_pid: int) -> OperationPermit:
        starttime = proc_starttime(target_pid)
        pidfd = os.pidfd_open(target_pid, 0)
        key = (target_pid, starttime)
        old = self._pidfds.pop(key, None)
        if old is not None:
            os.close(old)
        self._pidfds[key] = pidfd
        return OperationPermit(task_id, scope, self.generation, target_pid, starttime)

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
            try:
                os.close(fd)
            except OSError:
                pass
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

        # Reconcile an exact already-committed effect before consulting current
        # credential generation. Rotation revokes future operations; it must not
        # make an UNKNOWN committed result unrecoverable.
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
        if timeout_after_commit:
            raise UnknownOutcome(rid)
        return BrokerEvidence(rid, request.sender_pid, b["task_id"], b["scope"], b["credential_generation"], "COMMITTED", receipt)

    def evidence_contains_secret(self, evidence: BrokerEvidence, secret: bytes) -> bool:
        return secret.decode(errors="ignore") in json.dumps(evidence.__dict__, sort_keys=True)


class UnsafeSocketPossessionBroker:
    """Deliberately unsafe: possession of the transferred socket is treated as identity."""

    def __init__(self):
        self.apply_count = 0

    def execute(self, request: ReceivedRequest) -> str:
        self.apply_count += 1
        return f"accepted:{request.sender_pid}"
