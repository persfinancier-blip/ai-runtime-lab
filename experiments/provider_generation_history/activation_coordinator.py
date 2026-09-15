from __future__ import annotations

from experiments.anchor_attestation.protocol import UnknownOutcome
from experiments.provider_generation_history.activation import ActivationTicket
from experiments.provider_generation_history.protocol import HistoricalVerificationError


class ActivationCoordinatorMixin:
    """Coordinator-owned LAB-090 durable activation acknowledgement primitive.

    This mixin deliberately does not own construction, database identity, provider
    history, or schema installation. The composed supported ledger supplies ``_con``
    and keeps provider-history authority private. Its only job is to preserve the
    cross-boundary ordering after the SQL generation transition is already durable:

        SQL_COMMITTED -> provider COMMITTED_FENCED -> durable COMMITTED -> RELEASED

    Provider release is therefore never used as acknowledgement of the SQLite write.
    """

    @staticmethod
    def _ticket_from_activation_row(row) -> ActivationTicket:
        return ActivationTicket(row[2], row[3], row[4], row[0], row[5])

    def _activation_row(self, *, activation_id=None, generation_id=None):
        if (activation_id is None) == (generation_id is None):
            raise ValueError("select exactly one activation identity")
        q = self._con()
        try:
            if activation_id is not None:
                return q.execute(
                    "SELECT activation_id,new_generation_id,provider_id,generation,expected_position,fence,status "
                    "FROM provider_generation_activations WHERE activation_id=?",
                    (activation_id,),
                ).fetchone()
            return q.execute(
                "SELECT activation_id,new_generation_id,provider_id,generation,expected_position,fence,status "
                "FROM provider_generation_activations WHERE new_generation_id=?",
                (generation_id,),
            ).fetchone()
        finally:
            q.close()

    def _mark_activation_committed(self, ticket: ActivationTicket) -> None:
        """Durably acknowledge exactly one provider-committed activation ticket."""
        q = self._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            changed = q.execute(
                "UPDATE provider_generation_activations SET status='COMMITTED' "
                "WHERE activation_id=? AND provider_id=? AND generation=? "
                "AND expected_position=? AND fence=? AND status IN ('SQL_COMMITTED','COMMITTED')",
                (
                    ticket.activation_id,
                    ticket.provider_id,
                    ticket.generation,
                    ticket.expected_position,
                    ticket.fence,
                ),
            ).rowcount
            if changed != 1:
                raise HistoricalVerificationError("durable activation ticket mismatch")
            q.commit()
        except:
            if q.in_transaction:
                q.rollback()
            raise
        finally:
            q.close()

    @staticmethod
    def _release_committed_activation(provider, ticket: ActivationTicket) -> None:
        status = provider.activation_status(ticket)
        if status == "RELEASED":
            return
        if status != "COMMITTED_FENCED":
            raise HistoricalVerificationError(
                "durably committed activation is not provider-committed"
            )
        released = provider.release_activation(ticket)
        if released != "RELEASED":
            raise HistoricalVerificationError("provider activation fence did not release")

    def _commit_or_reconcile_activation(self, provider, ticket: ActivationTicket) -> None:
        """Commit provider fence, durably acknowledge exact ticket, then release it."""
        try:
            status = provider.commit_activation(ticket)
        except UnknownOutcome:
            status = provider.activation_status(ticket)
        if status != "COMMITTED_FENCED":
            raise HistoricalVerificationError(
                "provider activation must remain fenced until durable acknowledgement"
            )
        self._mark_activation_committed(ticket)
        self._release_committed_activation(provider, ticket)
