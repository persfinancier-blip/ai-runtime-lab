import json
import multiprocessing as mp
import os
import socket
import tempfile
import time
import unittest
from pathlib import Path

from experiments.brokered_credential_use.protocol import (
    CredentialBroker,
    ReceivedRequest,
    UnauthorizedSender,
    credential_socketpair,
    recv_kernel_request,
)
from experiments.transactional_broker_journal.authorized import (
    KernelAuthorizedBrokerWorker,
    bind_sender_to_journal_generation,
)
from experiments.transactional_broker_journal.protocol import (
    IdempotentSink,
    RequestConflict,
    TransactionalJournal,
)


def _sender(fd: int, bodies: list[dict], ready_fd: int) -> None:
    sock = socket.socket(fileno=fd)
    try:
        for body in bodies:
            sock.send(json.dumps(body, sort_keys=True, separators=(",", ":")).encode())
        os.write(ready_fd, b"1")
        time.sleep(10)
    finally:
        sock.close()
        os.close(ready_fd)


def _broker_worker(broker_fd: int, sender_pid: int, journal_path: str, sink_path: str, out) -> None:
    sock = socket.socket(fileno=os.dup(broker_fd))
    authority = CredentialBroker(b"identity-only", 1)
    journal = TransactionalJournal(journal_path, 1)
    try:
        permit = bind_sender_to_journal_generation(
            authority=authority,
            journal=journal,
            task_id="task",
            scope="read",
            target_pid=sender_pid,
        )
        received = recv_kernel_request(sock)
        worker = KernelAuthorizedBrokerWorker(
            authority=authority,
            permit=permit,
            journal=journal,
            sink=IdempotentSink(sink_path),
            secret=b"effect-secret",
        )
        result = worker.process_received(received)
        out.put(("ok", result.outcome, result.receipt))
    except Exception as exc:
        out.put(("error", type(exc).__name__, str(exc)))
    finally:
        authority.close()
        sock.close()


@unittest.skipUnless(
    os.name == "posix" and hasattr(os, "pidfd_open") and hasattr(socket, "SCM_CREDENTIALS"),
    "requires Linux pidfd + SCM_CREDENTIALS",
)
class ProcessIntegrationTests(unittest.TestCase):
    def _run_two(self, bodies: list[dict]):
        ctx = mp.get_context("fork")
        with tempfile.TemporaryDirectory() as td:
            journal_path = str(Path(td) / "journal.db")
            sink_path = str(Path(td) / "sink.db")
            journal = TransactionalJournal(journal_path, 1)
            sink = IdempotentSink(sink_path)
            broker, sender = credential_socketpair()
            ready_r, ready_w = os.pipe()
            sender_fd = sender.detach()
            target = ctx.Process(target=_sender, args=(sender_fd, bodies, ready_w))
            target.start()
            os.close(sender_fd)
            os.close(ready_w)
            self.assertEqual(os.read(ready_r, 1), b"1")
            os.close(ready_r)

            out = ctx.Queue()
            workers = [
                ctx.Process(
                    target=_broker_worker,
                    args=(broker.fileno(), target.pid, journal_path, sink_path, out),
                )
                for _ in range(2)
            ]
            for proc in workers:
                proc.start()
            for proc in workers:
                proc.join(8)
                self.assertFalse(proc.is_alive(), "broker worker hung")
            results = [out.get(timeout=2) for _ in workers]
            target.terminate()
            target.join(5)
            broker.close()
            record = journal.record("request-1")
            sink_count = sink.apply_count()
            durable_ok = journal.verify_durable()
            return results, record, sink_count, durable_ok

    @staticmethod
    def body(payload: str = "payload", *, request_id: str = "request-1", generation: int = 1) -> dict:
        return {
            "request_id": request_id,
            "task_id": "task",
            "scope": "read",
            "credential_generation": generation,
            "payload": payload,
        }

    def _self_worker(self, td):
        authority = CredentialBroker(b"identity-only", 1)
        journal = TransactionalJournal(Path(td) / "journal.db", 1)
        sink = IdempotentSink(Path(td) / "sink.db")
        permit = bind_sender_to_journal_generation(
            authority=authority,
            journal=journal,
            task_id="task",
            scope="read",
            target_pid=os.getpid(),
        )
        worker = KernelAuthorizedBrokerWorker(
            authority=authority,
            permit=permit,
            journal=journal,
            sink=sink,
            secret=b"effect-secret",
        )
        return authority, journal, sink, worker

    def test_two_real_broker_processes_same_authorized_request_apply_once(self):
        results, record, sink_count, durable_ok = self._run_two([self.body(), self.body()])
        self.assertTrue(all(item[0] == "ok" for item in results), results)
        self.assertEqual(sink_count, 1)
        self.assertEqual(results[0][2], results[1][2])
        self.assertEqual(record[1], "CONFIRMED")
        self.assertTrue(durable_ok)

    def test_two_real_broker_processes_substitution_has_one_winner(self):
        results, record, sink_count, durable_ok = self._run_two([self.body("alpha"), self.body("beta")])
        oks = [item for item in results if item[0] == "ok"]
        errors = [item for item in results if item[0] == "error"]
        self.assertEqual(len(oks), 1, results)
        self.assertEqual(len(errors), 1, results)
        self.assertEqual(errors[0][1], RequestConflict.__name__)
        self.assertEqual(sink_count, 1)
        self.assertEqual(record[1], "CONFIRMED")
        self.assertTrue(durable_ok)

    def test_failed_kernel_sender_authority_creates_no_reservation(self):
        ctx = mp.get_context("fork")
        with tempfile.TemporaryDirectory() as td:
            journal = TransactionalJournal(Path(td) / "journal.db", 1)
            sink = IdempotentSink(Path(td) / "sink.db")
            sleeper = ctx.Process(target=time.sleep, args=(5,))
            sleeper.start()
            authority = CredentialBroker(b"identity-only", 1)
            try:
                permit = bind_sender_to_journal_generation(
                    authority=authority,
                    journal=journal,
                    task_id="task",
                    scope="read",
                    target_pid=sleeper.pid,
                )
                forged = ReceivedRequest(self.body(), os.getpid(), os.getuid(), os.getgid())
                worker = KernelAuthorizedBrokerWorker(
                    authority=authority,
                    permit=permit,
                    journal=journal,
                    sink=sink,
                    secret=b"effect-secret",
                )
                with self.assertRaises(UnauthorizedSender):
                    worker.process_received(forged)
                self.assertIsNone(journal.record("request-1"))
                self.assertEqual(sink.apply_count(), 0)
            finally:
                authority.close()
                sleeper.terminate()
                sleeper.join(5)

    def test_exact_committed_retry_survives_journal_rotation(self):
        with tempfile.TemporaryDirectory() as td:
            authority, journal, sink, worker = self._self_worker(td)
            try:
                received = ReceivedRequest(self.body(), os.getpid(), os.getuid(), os.getgid())
                first = worker.process_received(received)
                self.assertEqual(first.outcome, "COMMITTED")
                self.assertEqual(journal.rotate(), 2)
                retry = worker.process_received(received)
                self.assertEqual(retry.outcome, "ALREADY_COMMITTED")
                self.assertEqual(retry.receipt, first.receipt)
                self.assertEqual(sink.apply_count(), 1)
            finally:
                authority.close()

    def test_new_operation_after_rotation_uses_new_journal_bound_permit(self):
        with tempfile.TemporaryDirectory() as td:
            authority, journal, sink, worker = self._self_worker(td)
            try:
                worker.process_received(
                    ReceivedRequest(self.body(), os.getpid(), os.getuid(), os.getgid())
                )
                self.assertEqual(journal.rotate(), 2)
                permit2 = bind_sender_to_journal_generation(
                    authority=authority,
                    journal=journal,
                    task_id="task",
                    scope="read",
                    target_pid=os.getpid(),
                )
                worker2 = KernelAuthorizedBrokerWorker(
                    authority=authority,
                    permit=permit2,
                    journal=journal,
                    sink=sink,
                    secret=b"effect-secret-generation-2",
                )
                result = worker2.process_received(
                    ReceivedRequest(
                        self.body("next", request_id="request-2", generation=2),
                        os.getpid(), os.getuid(), os.getgid(),
                    )
                )
                self.assertEqual(result.outcome, "COMMITTED")
                self.assertEqual(sink.apply_count(), 2)
            finally:
                authority.close()

    def test_substitution_after_rotation_still_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            authority, journal, sink, worker = self._self_worker(td)
            try:
                worker.process_received(
                    ReceivedRequest(self.body("alpha"), os.getpid(), os.getuid(), os.getgid())
                )
                self.assertEqual(journal.rotate(), 2)
                with self.assertRaises(RequestConflict):
                    worker.process_received(
                        ReceivedRequest(self.body("beta"), os.getpid(), os.getuid(), os.getgid())
                    )
                self.assertEqual(sink.apply_count(), 1)
            finally:
                authority.close()


if __name__ == "__main__":
    unittest.main()
