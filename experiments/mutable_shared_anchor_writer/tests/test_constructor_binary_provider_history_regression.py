from __future__ import annotations

from types import SimpleNamespace

import experiments.mutable_shared_anchor_writer.history_bound_operation_scoped as target
from experiments.mutable_shared_anchor_writer.history_bound_operation_scoped import (
    SupportedHistoryBoundOperationScopedAsymmetricSharedAnchorLedger,
)


class _FakeConnection:
    def __init__(self):
        self.in_transaction = False

    def execute(self, sql):
        if sql == "BEGIN IMMEDIATE":
            self.in_transaction = True
        return self

    def commit(self):
        self.in_transaction = False

    def rollback(self):
        self.in_transaction = False

    def close(self):
        pass


def test_install_guards_upgrades_receipt_helper_before_durable_verification(monkeypatch):
    ledger = object.__new__(
        SupportedHistoryBoundOperationScopedAsymmetricSharedAnchorLedger
    )
    ledger.path = "unused.db"
    ledger.provider_history = SimpleNamespace(bootstrap="bootstrap")
    q = _FakeConnection()
    events = []

    class _BinaryProbe:
        def __init__(self, path, bootstrap):
            events.append(("binary", path, bootstrap))
            self.bootstrap = bootstrap

    monkeypatch.setattr(target, "BinaryIdentityIntegratedAsymmetricProviderHistory", _BinaryProbe)
    monkeypatch.setattr(ledger, "_con", lambda: q)
    monkeypatch.setattr(
        ledger,
        "verify_durable",
        lambda: events.append(("verify", type(ledger.provider_history))),
    )
    monkeypatch.setattr(target, "install_full_operation_guards", lambda q: None)
    monkeypatch.setattr(target, "install_cross_table_guards", lambda q: None)
    monkeypatch.setattr(target, "install_history_binding_guards", lambda q: None)
    monkeypatch.setattr(target, "validate_protected_trigger_surface", lambda q: True)
    monkeypatch.setattr(target, "validate_required_not_null_contract", lambda q: True)
    monkeypatch.setattr(target, "validate_existing_mutable_state_locked", lambda q: True)

    SupportedHistoryBoundOperationScopedAsymmetricSharedAnchorLedger._install_guards(ledger)

    assert events[0] == ("binary", "unused.db", "bootstrap")
    assert events[1] == ("verify", _BinaryProbe)
    assert isinstance(ledger.provider_history, _BinaryProbe)
