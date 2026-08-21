import os
import tempfile
import unittest
from pathlib import Path

from experiments.brokered_credential_use.protocol import CredentialBroker, ReceivedRequest
from experiments.transactional_broker_journal.authorized import (
    KernelAuthorizedBrokerWorker,
    bind_sender_to_journal_generation,
)
from experiments.transactional_broker_journal.protocol import (
    IdempotentSink,
    StaleCredential,
    TransactionalJournal,
)


def body(payload="payload", *, request_id="request-1", generation=1):
    return {
        "request_id": request_id,
        "task_id": "task",
        "scope": "read",
        "credential_generation": generation,
        "payload": payload,
    }


class RestartRotationAuthorityTests(unittest.TestCase):
    def setup_worker(self, td, authority, journal, sink, secret):
        permit = bind_sender_to_journal_generation(
            authority=authority,
            journal=journal,
            task_id="task",
            scope="read",
            target_pid=os.getpid(),
        )
        return permit, KernelAuthorizedBrokerWorker(
            authority=authority,
            permit=permit,
            journal=journal,
            sink=sink,
            secret=secret,
        )

    def test_fresh_current_permit_reconciles_historical_committed_request(self):
        with tempfile.TemporaryDirectory() as td:
            authority = CredentialBroker(b"identity-only", 1)
            journal = TransactionalJournal(Path(td) / "journal.db", 1)
            sink = IdempotentSink(Path(td) / "sink.db")
            try:
                permit1, worker1 = self.setup_worker(td, authority, journal, sink, b"secret-1")
                self.assertEqual(permit1.credential_generation, 1)
                received = ReceivedRequest(body(), os.getpid(), os.getuid(), os.getgid())
                first = worker1.process_received(received)
                self.assertEqual(first.outcome, "COMMITTED")
                self.assertEqual(journal.rotate(), 2)

                permit2, worker2 = self.setup_worker(td, authority, journal, sink, b"secret-2")
                self.assertEqual(permit2.credential_generation, 2)
                retry = worker2.process_received(received)
                self.assertEqual(retry.outcome, "ALREADY_COMMITTED")
                self.assertEqual(retry.receipt, first.receipt)
                self.assertEqual(sink.apply_count(), 1)
            finally:
                authority.close()

    def test_fresh_current_permit_rejects_new_old_generation_operation(self):
        with tempfile.TemporaryDirectory() as td:
            authority = CredentialBroker(b"identity-only", 1)
            journal = TransactionalJournal(Path(td) / "journal.db", 1)
            sink = IdempotentSink(Path(td) / "sink.db")
            try:
                _, worker1 = self.setup_worker(td, authority, journal, sink, b"secret-1")
                worker1.process_received(
                    ReceivedRequest(body(), os.getpid(), os.getuid(), os.getgid())
                )
                self.assertEqual(journal.rotate(), 2)
                _, worker2 = self.setup_worker(td, authority, journal, sink, b"secret-2")
                with self.assertRaises(StaleCredential):
                    worker2.process_received(
                        ReceivedRequest(
                            body("late", request_id="request-new-old", generation=1),
                            os.getpid(),
                            os.getuid(),
                            os.getgid(),
                        )
                    )
                self.assertEqual(sink.apply_count(), 1)
            finally:
                authority.close()


if __name__ == "__main__":
    unittest.main()
