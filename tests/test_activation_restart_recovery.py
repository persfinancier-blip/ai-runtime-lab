from __future__ import annotations

import sqlite3
from types import SimpleNamespace

import pytest

from experiments.provider_generation_history.activation import ActivationTicket, FencedActivationProvider
from experiments.provider_generation_history.activation_coordinator import ActivationCoordinatorMixin
from experiments.provider_generation_history.activation_schema import ACTIVATION_TABLE_SQL, ACTIVATION_TRIGGER_SQL
from experiments.provider_generation_history.activation_schema_provenance import (
    classify_activation_schema_provenance_locked,
    completion_intent,
)
from experiments.provider_generation_history.protocol import HistoricalVerificationError


class _History:
    def __init__(self, generation_id: str):
        self._current = SimpleNamespace(generation_id=generation_id)

    def current(self):
        return self._current


class _Coordinator(ActivationCoordinatorMixin):
    def __init__(self, path, provider, generation_id="g2"):
        self.path = str(path)
        self.attested = SimpleNamespace(provider=provider)
        self.__history = _History(generation_id)

    def _con(self):
        return sqlite3.connect(self.path)

    def _history(self):
        return self.__history


def _seed_complete_schema(path):
    q = sqlite3.connect(path)
    q.execute(
        "CREATE TABLE shared_anchor_intents("
        "intent_id TEXT PRIMARY KEY, component_id TEXT NOT NULL, intent_type TEXT NOT NULL, "
        "payload_digest TEXT NOT NULL, status TEXT NOT NULL)"
    )
    q.execute(ACTIVATION_TABLE_SQL)
    q.execute(ACTIVATION_TRIGGER_SQL)
    marker = completion_intent()
    q.execute(
        "INSERT INTO shared_anchor_intents VALUES(?,?,?,?,?)",
        (marker.intent_id, marker.component_id, marker.intent_type, marker.payload_digest, "CONFIRMED"),
    )
    q.commit()
    assert classify_activation_schema_provenance_locked(q) == "COMPLETE"
    q.close()


def _insert_activation(path, ticket, *, generation_id="g2", status="SQL_COMMITTED"):
    q = sqlite3.connect(path)
    q.execute(
        "INSERT INTO provider_generation_activations VALUES(?,?,?,?,?,?,?)",
        (ticket.activation_id, generation_id, ticket.provider_id, ticket.generation,
         ticket.expected_position, ticket.fence, status),
    )
    q.commit()
    q.close()


def _prepared_case(tmp_path):
    path = tmp_path / "restart.sqlite"
    _seed_complete_schema(path)
    provider = FencedActivationProvider(generation=2, value=7)
    ticket = provider.prepare_activation(expected_position=7, activation_id="activation:g2:7")
    _insert_activation(path, ticket)
    return path, provider, ticket


def test_restart_sql_committed_prepared_finishes_ack_and_release(tmp_path):
    path, provider, ticket = _prepared_case(tmp_path)
    coordinator = _Coordinator(path, provider)

    coordinator._recover_pending_activation()

    assert coordinator._activation_row(activation_id=ticket.activation_id)[6] == "COMMITTED"
    assert provider.activation_status(ticket) == "RELEASED"


def test_restart_sql_committed_committed_fenced_finishes_durable_ack_then_release(tmp_path):
    path, provider, ticket = _prepared_case(tmp_path)
    assert provider.commit_activation(ticket) == "COMMITTED_FENCED"
    coordinator = _Coordinator(path, provider)

    coordinator._recover_pending_activation()

    assert coordinator._activation_row(activation_id=ticket.activation_id)[6] == "COMMITTED"
    assert provider.activation_status(ticket) == "RELEASED"


def test_restart_rejects_provider_release_before_durable_ack(tmp_path):
    path, provider, ticket = _prepared_case(tmp_path)
    provider.commit_activation(ticket)
    provider.release_activation(ticket)

    with pytest.raises(HistoricalVerificationError, match="released before durable acknowledgement"):
        _Coordinator(path, provider)._recover_pending_activation()


def test_restart_rejects_lost_provider_reservation(tmp_path):
    path = tmp_path / "absent.sqlite"
    _seed_complete_schema(path)
    provider = FencedActivationProvider(generation=2, value=7)
    ticket = ActivationTicket(provider.provider_id, provider.generation, 7, "activation:g2:7", 1)
    _insert_activation(path, ticket)

    with pytest.raises(HistoricalVerificationError, match="lost durable activation reservation"):
        _Coordinator(path, provider)._recover_pending_activation()


def test_restart_rejects_historical_noncurrent_sql_committed(tmp_path):
    path = tmp_path / "historical.sqlite"
    _seed_complete_schema(path)
    provider = FencedActivationProvider(generation=2, value=7)
    historical = ActivationTicket(provider.provider_id, provider.generation, 6, "activation:g1:6", 1)
    _insert_activation(path, historical, generation_id="g1")

    with pytest.raises(HistoricalVerificationError, match="historical provider activation remains unresolved"):
        _Coordinator(path, provider, generation_id="g2")._recover_pending_activation()
