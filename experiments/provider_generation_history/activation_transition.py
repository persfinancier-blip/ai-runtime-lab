from __future__ import annotations

from experiments.provider_generation_history.activation import ActivationTicket
from experiments.provider_generation_history.protocol import (
    GenerationDescriptor,
    HistoricalVerificationError,
    InvalidTransition,
    PendingRotationBlocked,
)


class ActivationTransitionMixin:
    """Coordinator-owned pre-ack LAB-090 activation transition.

    The provider first reserves the exact external position. Only then does one
    ``BEGIN IMMEDIATE`` re-check every SQLite prerequisite and atomically bind the
    activation ticket to the provider-history rotation. Provider commit/release is
    deliberately outside this primitive and belongs to ``ActivationCoordinatorMixin``.
    """

    @staticmethod
    def _activation_id(new: GenerationDescriptor, expected_position: int) -> str:
        return f"provider-activation:{new.generation_id}:{int(expected_position)}"

    @staticmethod
    def _validate_activation_ticket(
        ticket: ActivationTicket,
        new: GenerationDescriptor,
        expected_position: int,
        activation_id: str,
    ) -> None:
        if (
            type(ticket) is not ActivationTicket
            or ticket.provider_id != new.provider_id
            or ticket.generation != new.generation
            or ticket.expected_position != expected_position
            or ticket.activation_id != activation_id
            or type(ticket.fence) is not int
            or ticket.fence < 1
        ):
            raise HistoricalVerificationError(
                "provider activation ticket does not bind requested generation"
            )

    def _prepare_activation_transition(self, provider, new: GenerationDescriptor) -> ActivationTicket:
        q = self._con()
        try:
            q.execute("BEGIN")
            row = q.execute(
                "SELECT reserved_position FROM shared_anchor_meta WHERE singleton=1"
            ).fetchone()
            if row is None or type(row[0]) is not int or row[0] < 0:
                raise HistoricalVerificationError("invalid shared anchor tail")
            expected_position = row[0]
            q.commit()
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()

        activation_id = self._activation_id(new, expected_position)
        ticket = provider.prepare_activation(
            expected_position=expected_position,
            activation_id=activation_id,
        )
        self._validate_activation_ticket(ticket, new, expected_position, activation_id)
        if provider.activation_status(ticket) != "PREPARED":
            raise HistoricalVerificationError(
                "provider activation ticket is not exactly PREPARED"
            )
        return ticket

    def _commit_activation_transition_locked(
        self,
        provider,
        ticket: ActivationTicket,
        new: GenerationDescriptor,
        proof,
    ) -> None:
        sql_committed = False
        q = self._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            unresolved = q.execute(
                "SELECT 1 FROM provider_generation_activations "
                "WHERE status='SQL_COMMITTED' LIMIT 1"
            ).fetchone()
            if unresolved is not None:
                raise PendingRotationBlocked(
                    "previous provider activation commit is unresolved"
                )
            pending = q.execute(
                "SELECT COUNT(*) FROM shared_anchor_intents WHERE status='PREPARED'"
            ).fetchone()[0]
            if pending:
                raise PendingRotationBlocked("unresolved PREPARED anchor intent")
            row = q.execute(
                "SELECT reserved_position FROM shared_anchor_meta WHERE singleton=1"
            ).fetchone()
            if row is None or row[0] != ticket.expected_position:
                raise InvalidTransition(
                    "shared anchor tail changed after provider activation prepare"
                )
            q.execute(
                "INSERT INTO provider_generation_activations "
                "VALUES(?,?,?,?,?,?,'SQL_COMMITTED')",
                (
                    ticket.activation_id,
                    new.generation_id,
                    ticket.provider_id,
                    ticket.generation,
                    ticket.expected_position,
                    ticket.fence,
                ),
            )
            self._history()._rotate_locked(q, new, proof)
            q.commit()
            sql_committed = True
        except:
            if q.in_transaction:
                q.rollback()
            # If commit acknowledgement itself were ever ambiguous, durable state is
            # authoritative: never abort a ticket already bound by SQLite.
            row = self._activation_row(activation_id=ticket.activation_id)
            if row is not None and row[6] in {"SQL_COMMITTED", "COMMITTED"}:
                sql_committed = True
            if not sql_committed:
                provider.abort_activation(ticket)
            raise
        finally:
            q.close()

    def _preack_activation_transition(
        self,
        provider,
        new: GenerationDescriptor,
        proof,
    ) -> ActivationTicket:
        ticket = self._prepare_activation_transition(provider, new)
        self._commit_activation_transition_locked(provider, ticket, new, proof)
        return ticket
