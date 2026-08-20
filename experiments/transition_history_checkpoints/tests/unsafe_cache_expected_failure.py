import sqlite3
import tempfile
import unittest
from pathlib import Path

from experiments.transition_history_checkpoints.protocol import UnsafeCheckpointCache
from experiments.transition_history_checkpoints.tests.test_protocol import ChainBuilder


class UnsafeExpectedFailure(unittest.TestCase):
    def test_unauthenticated_cache_should_not_be_authority_but_is(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "db"
            b = ChainBuilder(path).append(4)
            q = sqlite3.connect(path)
            row = q.execute(
                "SELECT successor_root_id,successor_recovery_id FROM transitions WHERE sequence=2"
            ).fetchone()
            q.close()
            result = UnsafeCheckpointCache().resume(
                b.store, {"sequence": 2, "root_id": row[0], "recovery_id": row[1]}
            )
            self.assertIsNone(result, "unsafe unauthenticated cache was accepted as authority")


if __name__ == "__main__":
    unittest.main()
