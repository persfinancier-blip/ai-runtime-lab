from __future__ import annotations

from dataclasses import dataclass

from experiments.brokered_credential_use.protocol import (
    CredentialBroker,
    InvalidRequest as AuthorityInvalidRequest,
    OperationPermit,
    ReceivedRequest,
)

from .protocol import BrokerWorker, IdempotentSink, Request, Result, TransactionalJournal


@dataclass(frozen=True)
class AuthorizedRequest:
    """A journal request derived only after LAB-071 kernel sender validation."""

    received: ReceivedRequest
    journal_request: Request


class KernelAuthorizedBrokerWorker:
    """Put LAB-072 durable reservation behind LAB-071's process-instance authority boundary.

    LAB-071 remains authoritative for SCM_CREDENTIALS + pidfd/starttime sender identity.
    LAB-072 remains authoritative for concurrent reservation/idempotency/UNKNOWN state.
    The raw credential is held only by the worker and is never persisted by the journal.
    """

    def __init__(
        self,
        *,
        authority: CredentialBroker,
        permit: OperationPermit,
        journal: TransactionalJournal,
        sink: IdempotentSink,
        secret: bytes,
    ):
        self.authority = authority
        self.permit = permit
        self.worker = BrokerWorker(journal, sink, secret)

    def authorize(self, received: ReceivedRequest) -> AuthorizedRequest:
        # This is intentionally the exact LAB-071 process-instance check rather than
        # a duplicated PID comparison. Promotion into a shared runtime should expose
        # this as a public side-effect-free LAB-071 API rather than keep the private call.
        self.authority._validate_sender(received, self.permit)

        body = received.body
        required = {"request_id", "task_id", "scope", "credential_generation", "payload"}
        if not isinstance(body, dict) or set(body) != required:
            raise AuthorityInvalidRequest("unexpected/missing request fields")
        if body["task_id"] != self.permit.task_id or body["scope"] != self.permit.scope:
            raise AuthorityInvalidRequest("task/scope binding mismatch")
        if body["credential_generation"] != self.permit.credential_generation:
            raise AuthorityInvalidRequest("request generation does not match sender permit")

        request = Request(
            request_id=body["request_id"],
            task_id=body["task_id"],
            scope=body["scope"],
            credential_generation=body["credential_generation"],
            payload=body["payload"],
        )
        # Canonicalization/type validation happens before any durable reservation.
        request.canonical()
        return AuthorizedRequest(received, request)

    def process_received(
        self,
        received: ReceivedRequest,
        *,
        timeout_after_commit: bool = False,
    ) -> Result:
        authorized = self.authorize(received)
        return self.worker.process(
            authorized.journal_request,
            timeout_after_commit=timeout_after_commit,
        )
