from __future__ import annotations

import sqlite3

import pytest

from experiments.anchor_attestation.protocol import UnknownOutcome
from experiments.provider_generation_history.activation import ActivationTicket
from experiments.provider_generation_history.activation_coordinator import ActivationCoordinatorMixin
from experiments.provider_generation_history.protocol import HistoricalVerificationError


DDL = """CREATE TABLE provider_generation_activations(
  activation_id TEXT PRIMARY KEY,
  new_generation_id TEXT NOT NULL UNIQUE,
  provider_id TEXT NOT NULL,
  generation INTEGER NOT NULL,
  expected_position INTEGER NOT NULL,
  fence INTEGER NOT NULL,
  status TEXT NOT NULL CHECK(status IN ('SQL_COMMITTED','COMMITTED'))
)"""


class Coordinator(ActivationCoordinatorMixin):
    def __init__(self, path):
        self.path = str(path)

    def _con(self):
        return sqlite3.connect(self.path)


class Provider:
    def __init__(self, coordinator, ticket, *, unknown=False):
        self.coordinator = coordinator
        self.ticket = ticket
        self.status = "PREPARED"
        self.unknown = unknown
        self.trace = []

    def commit_activation(self, ticket):
        assert ticket == self.ticket
        self.trace.append("provider-commit")
        self.status = "COMMITTED_FENCED"
        if self.unknown:
            raise UnknownOutcome("ack lost")
        return self.status

    def activation_status(self, ticket):
        assert ticket == self.ticket
        self.trace.append("provider-status")
        return self.status

    def release_activation(self, ticket):
        assert ticket == self.ticket
        row = self.coordinator._activation_row(activation_id=ticket.activation_id)
        assert row[6] == "COMMITTED", "release occurred before durable acknowledgement"
        self.trace.append("provider-release")
        self.status = "RELEASED"
        return self.status


def seeded(tmp_path):
    path = tmp_path / "activation.sqlite"
    q = sqlite3.connect(path)
    q.execute(DDL)
    ticket = ActivationTicket("provider-a", 2, 7, "activation:g2:7", 11)
    q.execute(
        "INSERT INTO provider_generation_activations VALUES(?,?,?,?,?,?,'SQL_COMMITTED')",
        (ticket.activation_id, "g2", ticket.provider_id, ticket.generation, ticket.expected_position, ticket.fence),
    )
    q.commit()
    q.close()
    return Coordinator(path), ticket


@pytest.mark.parametrize("unknown", [False, True])
def test_commit_acknowledges_exact_ticket_before_release(tmp_path, unknown):
    coordinator, ticket = seeded(tmp_path)
    provider = Provider(coordinator, ticket, unknown=unknown)

    coordinator._commit_or_reconcile_activation(provider, ticket)

    row = coordinator._activation_row(activation_id=ticket.activation_id)
    assert row[6] == "COMMITTED"
    assert provider.status == "RELEASED"
    assert provider.trace[-1] == "provider-release"


def test_wrong_ticket_cannot_acknowledge_or_release(tmp_path):
    coordinator, ticket = seeded(tmp_path)
    wrong = ActivationTicket(
        ticket.provider_id,
        ticket.generation,
        ticket.expected_position,
        ticket.activation_id,
        ticket.fence + 1,
    )
    provider = Provider(coordinator, wrong)

    with pytest.raises(HistoricalVerificationError, match="durable activation ticket mismatch"):
        coordinator._commit_or_reconcile_activation(provider, wrong)

    row = coordinator._activation_row(activation_id=ticket.activation_id)
    assert row[6] == "SQL_COMMITTED"
    assert provider.status == "COMMITTED_FENCED"
    assert "provider-release" not in provider.trace
