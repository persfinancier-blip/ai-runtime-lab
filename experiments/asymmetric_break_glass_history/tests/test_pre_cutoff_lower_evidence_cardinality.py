import sqlite3
import tempfile
import unittest
from pathlib import Path

from experiments.asymmetric_break_glass_history.migration_guard import MigrationGuardError
from experiments.asymmetric_break_glass_history.tests.test_suffix import (
    AsymmetricSuffixIntegrationTests,
)


class PreCutoffLowerEvidenceCardinalityTests(unittest.TestCase):
    def make_ledger(self, path):
        return AsymmetricSuffixIntegrationTests().make_ledger(path)

    def test_orphan_provider_transition_blocks_migration_cutoff(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            ledger, signer, *_ = self.make_ledger(path)
            q = sqlite3.connect(path)
            q.execute(
                "INSERT INTO asymmetric_provider_transitions VALUES(?,?,?,?,?)",
                (
                    "f" * 64,
                    signer.public.generation_id,
                    signer.public.provider_id,
                    "00" * 64,
                    "00" * 64,
                ),
            )
            q.commit()
            q.close()

            with self.assertRaises(MigrationGuardError):
                ledger.migration_guard.payload()

    def test_orphan_threshold_proof_blocks_migration_cutoff(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            ledger, signer, *_ = self.make_ledger(path)
            root = ledger.rotation_authority.current()
            q = sqlite3.connect(path)
            q.execute(
                "INSERT INTO provider_rotation_threshold_proofs VALUES(?,?,?,?,?,?,?,?)",
                (
                    "f" * 64,
                    signer.public.provider_id,
                    signer.public.generation_id,
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
