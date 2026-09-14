import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from experiments.asymmetric_break_glass_history.final_supported import (
    SupportedFencedAsymmetricBreakGlassLedger,
)
from experiments.asymmetric_provider_history.supported import (
    SupportedAsymmetricHistoricalSharedAnchorLedger,
)


class _PublicCustodyProbe:
    def __init__(self):
        self.calls = 0

    def verify_durable(self):
        self.calls += 1
        return True


class _LedgerProbe:
    def __init__(self, path):
        self.path = str(path)
        self.public_recovery_custody = _PublicCustodyProbe()
        self.public_verify_calls = 0
        self.lab086_locked_calls = 0

    def _con(self):
        q = sqlite3.connect(self.path, timeout=0.05, isolation_level=None)
        q.execute("PRAGMA busy_timeout=50")
        return q

    def verify_durable(self):
        # The old LAB-086 final verifier called this public method first and only
        # acquired its own write-excluding transaction afterwards.  Keep this
        # probe so the regression fails if that split-snapshot path returns.
        self.public_verify_calls += 1
        return True

    def _verify_lab086_locked(self, q):
        self.lab086_locked_calls += 1
        self._assert_other_writer_blocked()
        return True

    def _assert_other_writer_blocked(self):
        other = self._con()
        try:
            try:
                other.execute("BEGIN IMMEDIATE")
            except sqlite3.OperationalError as exc:
                if "locked" not in str(exc).lower():
                    raise
                return
            else:
                other.rollback()
                raise AssertionError(
                    "final verifier did not hold a write-excluding transaction"
                )
        finally:
            other.close()


class FinalVerificationSnapshotTests(unittest.TestCase):
    def test_final_verifier_holds_one_guard_across_lower_and_lab086_layers(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            sqlite3.connect(path).close()
            probe = _LedgerProbe(path)
            final = SupportedFencedAsymmetricBreakGlassLedger.__new__(
                SupportedFencedAsymmetricBreakGlassLedger
            )
            final._ledger = probe

            lower_calls = []

            def lower_verify(_ledger):
                lower_calls.append(True)
                _ledger._assert_other_writer_blocked()
                return True

            # This test isolates the serialization contract.  Schema/fence
            # correctness has its own exact strict-fence suite; here the important
            # property is that all lower verification happens while the final
            # BEGIN IMMEDIATE is already held.
            with patch.object(
                SupportedFencedAsymmetricBreakGlassLedger,
                "_install_fence_locked",
                classmethod(lambda cls, q: None),
            ), patch(
                "experiments.asymmetric_break_glass_history.final_supported.assert_public_mutation_fence_locked",
                lambda q: True,
            ), patch.object(
                SupportedAsymmetricHistoricalSharedAnchorLedger,
                "verify_durable",
                lower_verify,
            ):
                self.assertTrue(final.verify_durable())

            self.assertEqual(probe.public_verify_calls, 0)
            self.assertEqual(probe.public_recovery_custody.calls, 1)
            self.assertEqual(probe.lab086_locked_calls, 1)
            self.assertEqual(len(lower_calls), 1)


if __name__ == "__main__":
    unittest.main()
