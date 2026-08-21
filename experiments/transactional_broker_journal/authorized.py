from __future__ import annotations

from dataclasses import dataclass

from experiments.brokered_credential_use.protocol import (
    CredentialBroker,
    InvalidRequest as AuthorityInvalidRequest,
    OperationPermit,
    ReceivedRequest,
    proc_starttime,
)

from .protocol import BrokerWorker, IdempotentSink, Request, Result, TransactionalJournal


@dataclass(frozen=True)
class AuthorizedRequest:
    """A journal request derived only after LAB-071 kernel sender validation."""

    received: ReceivedRequest
    journal_request: Request


def bind_sender_to_journal_generation(
    *,
    authority: CredentialBroker,
    journal: TransactionalJournal,
    task_id: str,
    scope: str,
    target_pid: int,
) -> OperationPermit:
    """Bind LAB-071 process identity to LAB-072's single durable generation authority.

    CredentialBroker is deliberately used only for pidfd/starttime process-instance
    authority here. The journal is the only durable credential-generation authority,
    avoiding a split-commit between LAB-071 JSON state and LAB-072 SQL state.
    """

    starttime = proc_starttime(target_pid)
    permit = OperationPermit(
        task_id=task_id,
        scope=scope,
        credential_generation=journal.generation(),
        target_pid=target_pid,
        target_starttime=starttime,
    )
    # Reuse the exact LAB-071 pidfd/starttime reacquisition logic. A promoted runtime
    # should expose this as a public side-effect-free sender-authority API.
    authority._install_pidfd(permit)
    return permit


class KernelAuthorizedBrokerWorker:
    """Put LAB-072 durable reservation behind LAB-071's process-instance authority boundary.

    LAB-071 remains authoritative for SCM_CREDENTIALS + pidfd/starttime sender identity.
    LAB-072 remains authoritative for credential generation, concurrent reservation,
    idempotency, and UNKNOWN state. The raw credential is held only by the worker and
    is never persisted by the journal.
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
        # No call to reserve()/sink is reachable before the kernel process-instance check.
        self.authority._validate_sender(received, self.permit)

        body = received.body
        required = {"request_id", "task_id", "scope", "credential_generation", "payload"}
        if not isinstance(body, dict) or set(body) != required:
            raise AuthorityInvalidRequest("unexpected/missing request fields")
        if body["task_id"] != self.permit.task_id or body["scope"] != self.permit.scope:
            raise AuthorityInvalidRequest("task/scope binding mismatch")

        request = Request(
            request_id=body["request_id"],
            task_id=body["task_id"],
            scope=body["scope"],
            credential_generation=body["credential_generation"],
            payload=body["payload"],
        )
        # Canonicalization/type validation happens before any durable reservation.
        # Request generation is intentionally left to the SQL journal: only the journal
        # can distinguish a new stale operation from an exact retry of an older committed
        # request after rotation/restart. The permit proves process/task/scope identity.
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
