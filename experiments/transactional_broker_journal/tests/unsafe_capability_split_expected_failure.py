import tempfile
import unittest
from pathlib import Path

from experiments.transactional_broker_journal.capability import UnsafeSplitAuthority
from experiments.transactional_broker_journal.protocol import IdempotentSink, Request, TransactionalJournal


class UnsafeCapabilitySplit(unittest.TestCase):
    def test_journal_without_capability_binding_should_not_execute_but_does(self):
        with tempfile.TemporaryDirectory() as td:
            journal = TransactionalJournal(Path(td) / "journal.db", 1)
            sink = IdempotentSink(Path(td) / "sink.db")
            request = Request("r", "task", "scope", 1, "payload")
            UnsafeSplitAuthority().process(journal, request, sink, b"secret")
            self.assertEqual(
                sink.apply_count(),
                0,
                "unsafe journal execution ignored authenticated sink capability authority",
            )


if __name__ == "__main__":
    unittest.main()
