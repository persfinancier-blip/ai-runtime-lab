import sqlite3
import tempfile
import unittest
from pathlib import Path

from experiments.asymmetric_break_glass_history.migration_guard import MigrationGuardError
from experiments.asymmetric_break_glass_history.tests.test_suffix import (
    AsymmetricSuffixIntegrationTests,
)


class PreCutoffLab086ProofCardinalityTests(unittest.TestCase):
    def make_ledger(self, path):
        return AsymmetricSuffixIntegrationTests().make_ledger(path)[0]

    def test_orphan_asymmetric_break_glass_proof_blocks_cutoff(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            ledger = self.make_ledger(path)
            root = ledger.rotation_authority.current()
            public = ledger.public_recovery_custody.current()
            q = sqlite3.connect(path)
            q.execute(
                "INSERT INTO provider_asymmetric_break_glass_proofs VALUES(?,?,?,?,?,?,?,?,?,?)",
                (
                    "f" * 64,
                    root.authority_id,
                    root.version,
                    root.generation,
                    public.authority_id,
                    public.version,
                    public.generation,
                    "0" * 64,
                    "0" * 64,
                    "[]",
                ),
            )
            q.commit()
            q.close()

            with self.assertRaises(MigrationGuardError):
                ledger.migration_guard.payload()

    def test_orphan_public_recovery_root_proof_blocks_cutoff(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            ledger = self.make_ledger(path)
            root = ledger.rotation_authority.current()
            public = ledger.public_recovery_custody.current()
            q = sqlite3.connect(path)
            q.execute(
                "INSERT INTO provider_asymmetric_recovery_public_root_proofs VALUES(?,?,?,?,?,?,?)",
                (
                    "f" * 64,
                    public.authority_id,
                    root.authority_id,
                    root.version,
                    root.generation,
                    "0" * 64,
                    "[]",
                ),
            )
            q.commit()
            q.close()

            with self.assertRaises(MigrationGuardError):
                ledger.migration_guard.payload()


if __name__ == "__main__":
    unittest.main()
