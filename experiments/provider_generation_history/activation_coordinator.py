from __future__ import annotations

from experiments.anchor_attestation.protocol import UnknownOutcome
from experiments.provider_generation_history.activation import ActivationTicket, FencedActivationProvider
from experiments.provider_generation_history.protocol import HistoricalVerificationError


class ActivationCoordinatorMixin:
    """Coordinator-owned LAB-090 durable activation acknowledgement/recovery primitive."""

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
        q = self._con()
        try:
            q.execute("BEGIN IMMEDIATE")
            changed = q.execute(
                "UPDATE provider_generation_activations SET status='COMMITTED' "
                "WHERE activation_id=? AND provider_id=? AND generation=? "
                "AND expected_position=? AND fence=? AND status IN ('SQL_COMMITTED','COMMITTED')",
                (ticket.activation_id, ticket.provider_id, ticket.generation, ticket.expected_position, ticket.fence),
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
            raise HistoricalVerificationError("durably committed activation is not provider-committed")
        released = provider.release_activation(ticket)
        if released != "RELEASED":
            raise HistoricalVerificationError("provider activation fence did not release")

    def _commit_or_reconcile_activation(self, provider, ticket: ActivationTicket) -> None:
        try:
            status = provider.commit_activation(ticket)
        except UnknownOutcome:
            status = provider.activation_status(ticket)
        if status != "COMMITTED_FENCED":
            raise HistoricalVerificationError("provider activation must remain fenced until durable acknowledgement")
        self._mark_activation_committed(ticket)
        self._release_committed_activation(provider, ticket)

    def _recover_pending_activation(self) -> None:
        """Reconcile only the durable current generation, then reject historical unresolved rows."""
        durable = self._history().current()
        row = self._activation_row(generation_id=durable.generation_id)
        if row is not None:
            ticket = self._ticket_from_activation_row(row)
            provider = self.attested.provider
            if not isinstance(provider, FencedActivationProvider):
                raise HistoricalVerificationError("runtime provider cannot reconcile durable activation ticket")
            status = provider.activation_status(ticket)
            if row[6] == "SQL_COMMITTED":
                if status == "PREPARED":
                    self._commit_or_reconcile_activation(provider, ticket)
                elif status == "COMMITTED_FENCED":
                    self._mark_activation_committed(ticket)
                    self._release_committed_activation(provider, ticket)
                elif status == "RELEASED":
                    raise HistoricalVerificationError("provider activation released before durable acknowledgement")
                elif status == "ABSENT":
                    raise HistoricalVerificationError("provider lost durable activation reservation")
                else:
                    raise HistoricalVerificationError("unknown provider activation status")
            elif row[6] == "COMMITTED":
                if status == "COMMITTED_FENCED":
                    self._release_committed_activation(provider, ticket)
                elif status != "RELEASED":
                    raise HistoricalVerificationError("durable committed activation/provider status mismatch")
            else:
                raise HistoricalVerificationError("invalid durable activation status")

        q = self._con()
        try:
            historical = q.execute(
                "SELECT 1 FROM provider_generation_activations "
                "WHERE status='SQL_COMMITTED' AND new_generation_id<>? LIMIT 1",
                (durable.generation_id,),
            ).fetchone()
        finally:
            q.close()
        if historical is not None:
            raise HistoricalVerificationError("historical provider activation remains unresolved")
