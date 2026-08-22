import tempfile, unittest
from pathlib import Path
from experiments.migration_anchor_binding.protocol import UnsafeLocalOnlyMigration
from experiments.migration_anchor_binding.tests.test_protocol import FakeMigration


class Unsafe(unittest.TestCase):
    def test_restored_pre_migration_snapshot_should_be_detected_but_local_only_cannot(self):
        with tempfile.TemporaryDirectory() as td:
            m = FakeMigration(Path(td) / "db.sqlite")
            m.establish()
            q = m._con()
            q.execute("DELETE FROM checkpoint")
            q.commit(); q.close()
            self.assertTrue(UnsafeLocalOnlyMigration().consequential(m))


if __name__ == "__main__":
    unittest.main()
