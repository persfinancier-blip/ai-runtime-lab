from __future__ import annotations

import unittest

from experiments.provider_generation_history.supported import SupportedHistoricalSharedAnchorLedger


class ProvenanceLost(RuntimeError):
    pass


class _Result:
    def __init__(self, row=None):
        self._row = row

    def fetchone(self):
        return self._row


class _FakeConnection:
    def __init__(self):
        self.in_transaction = False
        self.events = []

    def execute(self, sql, params=()):
        if sql == "BEGIN IMMEDIATE":
            self.in_transaction = True
            self.events.append(("begin", id(self)))
            return _Result()
        if sql.startswith("SELECT provider_id"):
            self.events.append(("select", id(self)))
            return _Result(None)
        if sql.startswith("INSERT INTO historical_provider_receipts"):
            self.events.append(("insert", id(self)))
            return _Result()
        raise AssertionError(f"unexpected SQL: {sql}")

    def commit(self):
        self.events.append(("commit", id(self)))
        self.in_transaction = False

    def rollback(self):
        self.events.append(("rollback", id(self)))
        self.in_transaction = False

    def close(self):
        self.events.append(("close", id(self)))


class _FakeHistory:
    def __init__(self, events):
        self.events = events

    def _verify_receipt_locked(self, q, receipt):
        if not q.in_transaction:
            raise AssertionError("receipt verification escaped write transaction")
        self.events.append(("verify", id(q)))
        return receipt


class _Receipt:
    provider_id = "provider"
    generation = 1
    position = 1
    request_id = "request"
    kind = "RECONCILE"
    challenge = "challenge"
    signature = "signature"
    stable_binding = "stable"


class GuardedReceiptLedger(SupportedHistoricalSharedAnchorLedger):
    """Minimal LAB-092-style same-transaction receipt-persistence guard."""

    def _con(self):
        return self.test_connection

    def _history(self):
        return self.test_history

    def _guard_receipt_persistence_locked(self, q):
        if not q.in_transaction:
            raise AssertionError("provenance guard escaped write transaction")
        q.events.append(("guard", id(q)))
        if not self.provenance_complete:
            raise ProvenanceLost("activation provenance lost before receipt persistence")


class StoreReceiptGuardHookTests(unittest.TestCase):
    def _ledger(self, *, complete):
        ledger = object.__new__(GuardedReceiptLedger)
        ledger.test_connection = _FakeConnection()
        ledger.test_history = _FakeHistory(ledger.test_connection.events)
        ledger.provenance_complete = complete
        return ledger

    def test_guard_verification_and_insert_share_one_immediate_transaction(self):
        ledger = self._ledger(complete=True)

        binding = ledger._store_receipt(_Receipt())

        self.assertEqual(binding, "stable")
        names = [event[0] for event in ledger.test_connection.events]
        self.assertEqual(names, ["begin", "guard", "verify", "select", "insert", "commit", "close"])
        connection_ids = {event[1] for event in ledger.test_connection.events}
        self.assertEqual(connection_ids, {id(ledger.test_connection)})

    def test_provenance_loss_rolls_back_before_history_verification_or_insert(self):
        ledger = self._ledger(complete=False)

        with self.assertRaisesRegex(ProvenanceLost, "provenance lost"):
            ledger._store_receipt(_Receipt())

        names = [event[0] for event in ledger.test_connection.events]
        self.assertEqual(names, ["begin", "guard", "rollback", "close"])


if __name__ == "__main__":
    unittest.main()
