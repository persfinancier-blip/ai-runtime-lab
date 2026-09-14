from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from experiments.provider_generation_history.database_identity_migration import (
    migrate_database_identity,
)
from experiments.provider_generation_history.tests.test_database_identity_migration import (
    _History,
    _Ledger,
    _init_database,
)


class _RejectSecondExecuteLedger(_Ledger):
    """First execution installs identity; every later reauthentication fails."""

    def __init__(self, path: Path):
        super().__init__(path)
        self.execute_calls = 0

    def execute(self, intent, *, timeout_after_commit=False):
        self.execute_calls += 1
        if self.execute_calls > 1:
            raise RuntimeError("simulated external reauthentication failure")
        return super().execute(intent, timeout_after_commit=timeout_after_commit)


class CompleteIdentityReauthenticationTests(unittest.TestCase):
    def test_complete_identity_must_not_bypass_external_reauthentication(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db.sqlite"
            _init_database(path)
            ledger = _RejectSecondExecuteLedger(path)
            history = _History(path)

            first = migrate_database_identity(ledger, history)
            self.assertEqual(ledger.execute_calls, 1)

            # COMPLETE local custody is not external authority by itself. A
            # repeated migration/startup verification must drive the existing
            # SharedAnchorLedger.execute() CONFIRMED path so its receipt is
            # reauthenticated before the local identity digest is trusted.
            with self.assertRaisesRegex(
                RuntimeError,
                "simulated external reauthentication failure",
            ):
                migrate_database_identity(ledger, history)

            self.assertEqual(ledger.execute_calls, 2)
            self.assertEqual(len(first), 64)


if __name__ == "__main__":
    unittest.main()
