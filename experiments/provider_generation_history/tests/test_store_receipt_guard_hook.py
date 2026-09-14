from __future__ import annotations

import unittest

from experiments.provider_generation_history.supported import SupportedHistoricalSharedAnchorLedger


class ProvenanceLost(RuntimeError):
    pass


class GuardedReceiptLedger(SupportedHistoricalSharedAnchorLedger):
    """Minimal LAB-092-style last-moment receipt-persistence guard."""

    def _provenance_allows_receipt_persistence(self) -> bool:
        return False

    def _history(self):
        raise AssertionError("history strategy must not be reached after guard failure")

    def _store_receipt(self, receipt):
        if not self._provenance_allows_receipt_persistence():
            raise ProvenanceLost("activation provenance lost before receipt persistence")
        return super()._store_receipt(receipt)


class StoreReceiptGuardHookTests(unittest.TestCase):
    def test_subclass_can_fail_closed_before_private_history_strategy_is_reached(self):
        ledger = object.__new__(GuardedReceiptLedger)
        receipt = object()

        with self.assertRaisesRegex(ProvenanceLost, "provenance lost"):
            ledger._store_receipt(receipt)


if __name__ == "__main__":
    unittest.main()
