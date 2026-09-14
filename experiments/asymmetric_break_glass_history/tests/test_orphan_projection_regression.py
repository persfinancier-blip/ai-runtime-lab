import sqlite3
import tempfile
import unittest
from pathlib import Path

from experiments.asymmetric_break_glass_history.migration_guard import (
    AuthenticatedBreakGlassMigrationGuard,
    MigrationGuardError,
)
from experiments.asymmetric_break_glass_history.tests.test_migration_guard import (
    MigrationGuardIntegrationTests,
)


class OrphanProjectionRegressionTests(unittest.TestCase):
    def test_orphan_projection_without_boundary_is_rejected(self):
        helper = MigrationGuardIntegrationTests()
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            ledger, *_ = helper.make_ledger(path)
            guard = AuthenticatedBreakGlassMigrationGuard(ledger)

            q = sqlite3.connect(path)
            q.execute(
                "INSERT INTO provider_asymmetric_break_glass_legacy_projection "
                "VALUES(1,?)",
                ('{"schema_version":1}',),
            )
            q.commit()
            q.close()

            with self.assertRaises(MigrationGuardError):
                guard.verify()

    def test_orphan_public_rotation_root_proof_blocks_cutoff(self):
        helper = MigrationGuardIntegrationTests()
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            ledger, *_ = helper.make_ledger(path)
            guard = AuthenticatedBreakGlassMigrationGuard(ledger)

            q = sqlite3.connect(path)
            q.execute(
                "INSERT INTO provider_asymmetric_recovery_public_root_proofs "
                "VALUES(?,?,?,?,?,?,?)",
                ("future", "old", "root", 1, 1, "0" * 64, "[]"),
            )
            q.commit()
            q.close()

            with self.assertRaises(RuntimeError):
                guard.payload()

    def test_orphan_asymmetric_break_glass_proof_blocks_cutoff(self):
        helper = MigrationGuardIntegrationTests()
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            ledger, *_ = helper.make_ledger(path)
            guard = AuthenticatedBreakGlassMigrationGuard(ledger)

            q = sqlite3.connect(path)
            q.execute(
                "CREATE TABLE provider_asymmetric_break_glass_proofs("
                "new_rotation_authority_id TEXT PRIMARY KEY)"
            )
            q.execute(
                "INSERT INTO provider_asymmetric_break_glass_proofs VALUES('future')"
            )
            q.commit()
            q.close()

            with self.assertRaises(RuntimeError):
                guard.payload()


if __name__ == "__main__":
    unittest.main()
