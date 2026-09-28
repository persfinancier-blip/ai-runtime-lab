import hashlib
import hmac
import json
import multiprocessing
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path

from experiments.anchor_attestation.protocol import (
    AnchorMismatch,
    AttestationVerifier,
    AttestedCatchup,
    ProviderIdentity,
    SignedObservation,
)
from experiments.asymmetric_provider_history.protocol import GenerationSigner
from experiments.mutable_shared_anchor_writer.history_bound_operation_scoped import (
    SupportedHistoryBoundOperationScopedAsymmetricSharedAnchorLedger,
)
from experiments.shared_anchor_intent_ledger.protocol import Intent


class SharedSQLiteAnchorProvider:
    """Process-shareable LAB-080 provider fixture with real signed observations.

    The provider state is intentionally separate from the ledger DB, matching the
    external-anchor boundary. SQLite BEGIN IMMEDIATE serializes provider effects
    across worker processes while request_id persistence preserves idempotency.
    """

    def __init__(self, path, provider_id="anchor-A", generation=1, key=b"shared-hmac"):
        self.path = str(path)
        self.provider_id = provider_id
        self.generation = int(generation)
        self.key = key
        q = sqlite3.connect(self.path, timeout=5)
        try:
            q.execute("PRAGMA busy_timeout=5000")
            q.executescript(
                """
                CREATE TABLE IF NOT EXISTS provider_state(
                  singleton INTEGER PRIMARY KEY CHECK(singleton=1),
                  value INTEGER NOT NULL,
                  increment_calls INTEGER NOT NULL
                );
                CREATE TABLE IF NOT EXISTS provider_requests(
                  request_id TEXT PRIMARY KEY,
                  position INTEGER NOT NULL
                );
                """
            )
            q.execute(
                "INSERT OR IGNORE INTO provider_state VALUES(1,0,0)"
            )
            q.commit()
        finally:
            q.close()

    @staticmethod
    def _canonical(provider_id, generation, position, challenge, kind, request_id):
        return json.dumps(
            {
                "challenge": str(challenge),
                "generation": int(generation),
                "kind": str(kind),
                "position": int(position),
                "provider_id": str(provider_id),
                "request_id": str(request_id),
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode()

    def _obs(self, *, challenge, kind, request_id, position):
        payload = self._canonical(
            self.provider_id,
            self.generation,
            position,
            challenge,
            kind,
            request_id,
        )
        mac = hmac.new(self.key, payload, hashlib.sha256).hexdigest()
        return SignedObservation(
            self.provider_id,
            self.generation,
            int(position),
            challenge,
            kind,
            request_id,
            mac,
        )

    @property
    def value(self):
        q = sqlite3.connect(self.path)
        try:
            return q.execute(
                "SELECT value FROM provider_state WHERE singleton=1"
            ).fetchone()[0]
        finally:
            q.close()

    @property
    def increment_calls(self):
        q = sqlite3.connect(self.path)
        try:
            return q.execute(
                "SELECT increment_calls FROM provider_state WHERE singleton=1"
            ).fetchone()[0]
        finally:
            q.close()

    def read(self, *, challenge, request_id):
        return self._obs(
            challenge=challenge,
            kind="READ",
            request_id=request_id,
            position=self.value,
        )

    def increment(self, *, expected, challenge, request_id, timeout_after_commit=False):
        q = sqlite3.connect(self.path, timeout=5, isolation_level=None)
        q.execute("PRAGMA busy_timeout=5000")
        try:
            q.execute("BEGIN IMMEDIATE")
            q.execute(
                "UPDATE provider_state SET increment_calls=increment_calls+1 "
                "WHERE singleton=1"
            )
            previous = q.execute(
                "SELECT position FROM provider_requests WHERE request_id=?",
                (request_id,),
            ).fetchone()
            if previous is not None:
                position = previous[0]
                q.commit()
                return self._obs(
                    challenge=challenge,
                    kind="INCREMENT",
                    request_id=request_id,
                    position=position,
                )

            current = q.execute(
                "SELECT value FROM provider_state WHERE singleton=1"
            ).fetchone()[0]
            if current != int(expected):
                q.rollback()
                raise AnchorMismatch(f"expected={expected} current={current}")
            position = current + 1
            q.execute(
                "UPDATE provider_state SET value=? WHERE singleton=1",
                (position,),
            )
            q.execute(
                "INSERT INTO provider_requests(request_id,position) VALUES(?,?)",
                (request_id, position),
            )
            q.commit()
            return self._obs(
                challenge=challenge,
                kind="INCREMENT",
                request_id=request_id,
                position=position,
            )
        finally:
            if q.in_transaction:
                q.rollback()
            q.close()

    def reconcile_increment(self, *, challenge, request_id):
        q = sqlite3.connect(self.path)
        try:
            row = q.execute(
                "SELECT position FROM provider_requests WHERE request_id=?",
                (request_id,),
            ).fetchone()
        finally:
            q.close()
        if row is None:
            return None
        return self._obs(
            challenge=challenge,
            kind="RECONCILE",
            request_id=request_id,
            position=row[0],
        )


class CrashBeforeConfirmationLedger(
    SupportedHistoryBoundOperationScopedAsymmetricSharedAnchorLedger
):
    def _commit_confirmation(self, intent_id, entry, receipt):
        os._exit(17)


def _runtime(provider):
    attested = AttestedCatchup(
        provider,
        AttestationVerifier(
            {(provider.provider_id, provider.generation): provider.key},
            ProviderIdentity(provider.provider_id, provider.generation),
        ),
    )
    signer = GenerationSigner.from_seed(
        provider.provider_id,
        provider.generation,
        b"\x51" * 32,
    )
    return attested, signer


def _ledger(path, provider, ledger_type=SupportedHistoryBoundOperationScopedAsymmetricSharedAnchorLedger):
    attested, signer = _runtime(provider)
    return ledger_type(path, attested, signer.public, signer)


def _same_intent():
    return Intent(
        "real-process-convergence",
        "component-A",
        "migration",
        {"v": 1},
    )


def _execute_worker(ledger_path, provider_path, barrier, output):
    provider = SharedSQLiteAnchorProvider(provider_path)
    ledger = _ledger(ledger_path, provider)
    barrier.wait()
    try:
        result = ledger.execute(_same_intent())
        output.put(("ok", result.status, result.receipt_binding))
    except Exception as exc:
        output.put(("err", type(exc).__name__, str(exc)))


def _crash_worker(ledger_path, provider_path):
    provider = SharedSQLiteAnchorProvider(provider_path)
    ledger = _ledger(ledger_path, provider, CrashBeforeConfirmationLedger)
    ledger.execute(_same_intent())
    os._exit(99)


class RealStackProcessConcurrencyAndCrashTests(unittest.TestCase):
    def make_paths(self, td):
        ledger_path = Path(td) / "shared.db"
        provider_path = Path(td) / "provider.db"
        provider = SharedSQLiteAnchorProvider(provider_path)
        _ledger(ledger_path, provider)
        return ledger_path, provider_path, provider

    def test_two_processes_converge_through_final_supported_surface(self):
        if "fork" not in multiprocessing.get_all_start_methods():
            self.skipTest("fork start method required")
        ctx = multiprocessing.get_context("fork")
        with tempfile.TemporaryDirectory() as td:
            ledger_path, provider_path, provider = self.make_paths(td)
            barrier = ctx.Barrier(2)
            output = ctx.Queue()
            workers = [
                ctx.Process(
                    target=_execute_worker,
                    args=(ledger_path, provider_path, barrier, output),
                )
                for _ in range(2)
            ]
            for worker in workers:
                worker.start()
            for worker in workers:
                worker.join(15)
            self.assertTrue(all(not worker.is_alive() for worker in workers))
            results = [output.get(timeout=2) for _ in workers]
            self.assertTrue(all(result[0] == "ok" for result in results), results)
            self.assertTrue(all(result[1] == "CONFIRMED" for result in results), results)
            bindings = {result[2] for result in results}
            self.assertEqual(len(bindings), 1)
            self.assertEqual(provider.value, 1)

            restarted = _ledger(
                ledger_path,
                SharedSQLiteAnchorProvider(provider_path),
            )
            confirmed = restarted.execute(_same_intent())
            self.assertEqual(confirmed.status, "CONFIRMED")
            self.assertIn(confirmed.receipt_binding, bindings)
            self.assertTrue(restarted.verify_durable())

            q = sqlite3.connect(ledger_path)
            try:
                self.assertEqual(
                    q.execute(
                        "SELECT COUNT(*) FROM asymmetric_provider_receipts"
                    ).fetchone()[0],
                    1,
                )
            finally:
                q.close()

    def test_process_death_after_receipt_before_confirmation_recovers_without_second_effect(self):
        if "fork" not in multiprocessing.get_all_start_methods():
            self.skipTest("fork start method required")
        ctx = multiprocessing.get_context("fork")
        with tempfile.TemporaryDirectory() as td:
            ledger_path, provider_path, provider = self.make_paths(td)
            worker = ctx.Process(
                target=_crash_worker,
                args=(ledger_path, provider_path),
            )
            worker.start()
            worker.join(15)
            self.assertEqual(worker.exitcode, 17)
            self.assertEqual(provider.value, 1)

            q = sqlite3.connect(ledger_path)
            try:
                row = q.execute(
                    "SELECT status,receipt_binding,request_id FROM shared_anchor_intents "
                    "WHERE intent_id=?",
                    (_same_intent().intent_id,),
                ).fetchone()
                self.assertEqual(row[:2], ("PREPARED", None))
                self.assertEqual(
                    q.execute(
                        "SELECT COUNT(*) FROM asymmetric_provider_receipts WHERE request_id=?",
                        (row[2],),
                    ).fetchone()[0],
                    1,
                )
            finally:
                q.close()

            restarted = _ledger(
                ledger_path,
                SharedSQLiteAnchorProvider(provider_path),
            )
            confirmed = restarted.execute(_same_intent())
            self.assertEqual(confirmed.status, "CONFIRMED")
            self.assertEqual(provider.value, 1)
            self.assertTrue(restarted.verify_durable())


if __name__ == "__main__":
    unittest.main()
