from __future__ import annotations

from dataclasses import dataclass, field

from experiments.anchor_attestation.protocol import (
    AnchorMismatch,
    ProviderUnavailable,
    SignedAnchorProvider,
    UnknownOutcome,
)


class ActivationError(RuntimeError):
    pass


class ActivationFenced(ActivationError):
    pass


class ActivationTicketMismatch(ActivationError):
    pass


@dataclass(frozen=True)
class ActivationTicket:
    provider_id: str
    generation: int
    expected_position: int
    activation_id: str
    fence: int


@dataclass
class ActivationState:
    """Provider-owned durable state for activation reservations.

    A real external provider must persist the equivalent state atomically with its
    position/CAS metadata. Sharing one ActivationState across reconstructed test
    provider objects models that provider-side durability without pretending that
    coordinator SQLite can serialize the external service.
    """

    next_fence: int = 0
    pending: ActivationTicket | None = None
    committed: dict[str, ActivationTicket] = field(default_factory=dict)


class FencedActivationProvider(SignedAnchorProvider):
    """SignedAnchorProvider with provider-owned generation-activation fencing.

    `prepare_activation` is the external linearization point: it atomically checks
    the exact observed position and installs a monotonically fenced reservation.
    While the reservation is pending, ordinary increments are rejected. Commit and
    abort are idempotent by activation_id; status survives coordinator restart when
    the same provider-owned ActivationState is supplied.
    """

    def __init__(self, *args, activation_state: ActivationState | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.activation_state = activation_state or ActivationState()

    def _ticket_matches_runtime(self, ticket: ActivationTicket) -> None:
        if (
            ticket.provider_id != self.provider_id
            or ticket.generation != self.generation
        ):
            raise ActivationTicketMismatch("activation ticket provider generation mismatch")

    def prepare_activation(self, *, expected_position: int, activation_id: str) -> ActivationTicket:
        if not self.available:
            raise ProviderUnavailable("activation path unavailable")
        if not isinstance(activation_id, str) or not activation_id:
            raise ValueError("activation_id must be non-empty")
        expected_position = int(expected_position)

        committed = self.activation_state.committed.get(activation_id)
        if committed is not None:
            self._ticket_matches_runtime(committed)
            if committed.expected_position != expected_position:
                raise ActivationTicketMismatch("activation_id reused with different position")
            return committed

        pending = self.activation_state.pending
        if pending is not None:
            self._ticket_matches_runtime(pending)
            if pending.activation_id != activation_id:
                raise ActivationFenced("provider has another pending activation")
            if pending.expected_position != expected_position:
                raise ActivationTicketMismatch("activation_id reused with different position")
            return pending

        if self.value != expected_position:
            raise AnchorMismatch(f"expected={expected_position} current={self.value}")

        self.activation_state.next_fence += 1
        ticket = ActivationTicket(
            self.provider_id,
            self.generation,
            expected_position,
            activation_id,
            self.activation_state.next_fence,
        )
        self.activation_state.pending = ticket
        return ticket

    def activation_status(self, ticket: ActivationTicket) -> str:
        self._ticket_matches_runtime(ticket)
        committed = self.activation_state.committed.get(ticket.activation_id)
        if committed is not None:
            if committed != ticket:
                raise ActivationTicketMismatch("committed activation ticket mismatch")
            return "COMMITTED"
        pending = self.activation_state.pending
        if pending == ticket:
            return "PREPARED"
        if pending is not None and pending.activation_id == ticket.activation_id:
            raise ActivationTicketMismatch("pending activation ticket mismatch")
        return "ABSENT"

    def commit_activation(self, ticket: ActivationTicket, *, timeout_after_commit: bool = False) -> str:
        if not self.available:
            raise ProviderUnavailable("activation path unavailable")
        self._ticket_matches_runtime(ticket)
        status = self.activation_status(ticket)
        if status == "COMMITTED":
            return status
        if status != "PREPARED":
            raise ActivationTicketMismatch("activation is not pending")
        if self.value != ticket.expected_position:
            raise AnchorMismatch(
                f"activation position changed: expected={ticket.expected_position} current={self.value}"
            )
        self.activation_state.committed[ticket.activation_id] = ticket
        self.activation_state.pending = None
        if timeout_after_commit:
            raise UnknownOutcome("activation committed; acknowledgement lost")
        return "COMMITTED"

    def abort_activation(self, ticket: ActivationTicket) -> str:
        self._ticket_matches_runtime(ticket)
        status = self.activation_status(ticket)
        if status == "COMMITTED":
            return status
        if status == "ABSENT":
            return status
        self.activation_state.pending = None
        return "ABORTED"

    def increment(self, *, expected, challenge, request_id, timeout_after_commit=False):
        pending = self.activation_state.pending
        if pending is not None:
            raise ActivationFenced(
                f"provider activation {pending.activation_id} fence={pending.fence} is pending"
            )
        return super().increment(
            expected=expected,
            challenge=challenge,
            request_id=request_id,
            timeout_after_commit=timeout_after_commit,
        )
