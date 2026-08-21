import sqlite3
import tempfile
import threading
import unittest
from dataclasses import replace
from pathlib import Path

from experiments.sink_capability_contract import protocol as cap
from experiments.transactional_broker_journal.capability import (
    CapabilityBindingError,
    CapabilityBoundJournal,
    CapabilityBrokerWorker,
    CapabilityExecutionBlocked,
)
from experiments.transactional_broker_journal.protocol import (
    IdempotentSink,
    Request,
    RequestConflict,
    TransactionalJournal,
    UnknownOutcome,
)


class Tests(unittest.TestCase):
    def authority(self):
        return cap.ProbeAuthority(issuer_id="probe", key=b"probe-key", generation=1)

    def capability(self, authority, *, generation=1, reconcile=True, retention=100, sink_id="sink-A"):
        claim = cap.CapabilityClaim(
            sink_id=sink_id,
            generation=generation,
            mutating=True,
            stable_idempotency_key=True,
            request_bound_key=True,
            reconcile_by_key=reconcile,
            retention_seconds=retention,
            source="behavioral-test-probe",
        )
        probe_sink = cap.SimulatedSink(
            idempotent=True, request_bound=True, reconcile=reconcile
        )
        return cap.VerifiedCapability(claim, authority.attest(claim, probe_sink))

    def setup(self, td):
        root = Path(td)
        journal = TransactionalJournal(root / "journal.db", 1)
        authority = self.authority()
        bound = CapabilityBoundJournal(journal, authority)
        sink = IdempotentSink(root / "sink.db")
        return journal, authority, bound, sink

    @staticmethod
    def worker(bound, sink, sink_id="sink-A"):
        return CapabilityBrokerWorker(
            bound, sink, b"secret", sink_id=sink_id
        )

    def test_same_generation_claim_mutation_blocks_existing_intent(self):
        with tempfile.TemporaryDirectory() as td:
            journal, authority, bound, sink = self.setup(td)
            request = Request("r", "task", "scope", 1, "payload")
            original = self.capability(authority, retention=10)
            bound.reserve(request, original, now=0)
            changed = self.capability(authority, retention=1000)
            with self.assertRaises(cap.StaleCapability):
                self.worker(bound, sink).process(request, changed, now=1)
            self.assertEqual(sink.apply_count(), 0)

    def test_capability_generation_rotation_blocks_new_execution(self):
        with tempfile.TemporaryDirectory() as td:
            journal, authority, bound, sink = self.setup(td)
            request = Request("r", "task", "scope", 1, "payload")
            bound.reserve(request, self.capability(authority, generation=1), now=0)
            with self.assertRaises(cap.StaleCapability):
                self.worker(bound, sink).process(
                    request, self.capability(authority, generation=2), now=1
                )
            self.assertEqual(sink.apply_count(), 0)

    def test_unknown_then_capability_rotation_reconciles_without_duplicate(self):
        with tempfile.TemporaryDirectory() as td:
            journal, authority, bound, sink = self.setup(td)
            request = Request("r", "task", "scope", 1, "payload")
            worker = self.worker(bound, sink)
            with self.assertRaises(UnknownOutcome):
                worker.process(
                    request,
                    self.capability(authority, generation=1),
                    now=0,
                    timeout_after_commit=True,
                )
            self.assertEqual(sink.apply_count(), 1)
            out = worker.process(
                request, self.capability(authority, generation=2), now=1
            )
            self.assertEqual(out.outcome, "RECONCILED")
            self.assertEqual(sink.apply_count(), 1)

    def test_unknown_idempotent_only_never_executes_second_effect(self):
        with tempfile.TemporaryDirectory() as td:
            journal, authority, bound, sink = self.setup(td)
            request = Request("r", "task", "scope", 1, "payload")
            capability = self.capability(authority, reconcile=False)
            worker = self.worker(bound, sink)
            with self.assertRaises(UnknownOutcome):
                worker.process(request, capability, now=0, timeout_after_commit=True)
            with self.assertRaises(CapabilityExecutionBlocked):
                worker.process(request, capability, now=1)
            self.assertEqual(sink.apply_count(), 1)

    def test_retention_expiry_blocks_pending_execution(self):
        with tempfile.TemporaryDirectory() as td:
            journal, authority, bound, sink = self.setup(td)
            request = Request("r", "task", "scope", 1, "payload")
            capability = self.capability(authority, retention=2)
            bound.reserve(request, capability, now=0)
            with self.assertRaises(CapabilityExecutionBlocked):
                self.worker(bound, sink).process(request, capability, now=2)
            self.assertEqual(sink.apply_count(), 0)

    def test_forged_attestation_creates_no_journal_row(self):
        with tempfile.TemporaryDirectory() as td:
            journal, authority, bound, sink = self.setup(td)
            request = Request("r", "task", "scope", 1, "payload")
            good = self.capability(authority)
            forged = cap.VerifiedCapability(
                good.claim, replace(good.attestation, signature="0" * 64)
            )
            with self.assertRaises(cap.UntrustedCapability):
                bound.reserve(request, forged, now=0)
            q = journal._con()
            try:
                self.assertEqual(
                    q.execute("SELECT COUNT(*) FROM broker_requests").fetchone()[0], 0
                )
            finally:
                q.close()

    def test_concurrent_workers_share_one_capability_bound_effect(self):
        with tempfile.TemporaryDirectory() as td:
            journal, authority, bound, sink = self.setup(td)
            request = Request("r", "task", "scope", 1, "payload")
            capability = self.capability(authority)
            wrappers = [
                CapabilityBoundJournal(
                    TransactionalJournal(Path(td) / "journal.db", 1), authority
                )
                for _ in range(2)
            ]
            gate = threading.Barrier(3)
            out, errors = [], []

            def run(wrapper):
                gate.wait()
                try:
                    out.append(
                        self.worker(wrapper, sink).process(
                            request, capability, now=0
                        )
                    )
                except Exception as exc:
                    errors.append(exc)

            threads = [threading.Thread(target=run, args=(w,)) for w in wrappers]
            [t.start() for t in threads]
            gate.wait()
            [t.join(5) for t in threads]
            self.assertFalse(errors)
            self.assertEqual(len(out), 2)
            self.assertEqual(sink.apply_count(), 1)
            self.assertEqual(out[0].receipt, out[1].receipt)

    def test_restart_recovers_exact_capability_binding_from_sql(self):
        with tempfile.TemporaryDirectory() as td:
            journal, authority, bound, sink = self.setup(td)
            request = Request("r", "task", "scope", 1, "payload")
            capability = self.capability(authority)
            bound.reserve(request, capability, now=17)
            reopened = CapabilityBoundJournal(
                TransactionalJournal(Path(td) / "journal.db", 1), authority
            )
            plan = reopened.binding("r")
            self.assertEqual(plan.claim_digest, capability.attestation.claim_digest)
            self.assertEqual(plan.capability_generation, 1)
            self.assertEqual(plan.probe_generation, 1)
            self.assertEqual(plan.key_created_at, 17)
            self.assertTrue(reopened.verify_durable())

    def test_confirmed_result_survives_later_capability_rotation(self):
        with tempfile.TemporaryDirectory() as td:
            journal, authority, bound, sink = self.setup(td)
            request = Request("r", "task", "scope", 1, "payload")
            first = self.worker(bound, sink).process(
                request, self.capability(authority, generation=1), now=0
            )
            replay = self.worker(bound, sink).process(
                request, self.capability(authority, generation=2), now=1
            )
            self.assertEqual(replay.outcome, "ALREADY_COMMITTED")
            self.assertEqual(replay.receipt, first.receipt)
            self.assertEqual(sink.apply_count(), 1)

    def test_configured_sink_identity_mismatch_blocks_external_action(self):
        with tempfile.TemporaryDirectory() as td:
            journal, authority, bound, sink = self.setup(td)
            request = Request("r", "task", "scope", 1, "payload")
            capability = self.capability(authority, sink_id="sink-A")
            with self.assertRaises(CapabilityBindingError):
                self.worker(bound, sink, sink_id="sink-B").process(
                    request, capability, now=0
                )
            self.assertEqual(sink.apply_count(), 0)

    def test_request_id_substitution_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            journal, authority, bound, sink = self.setup(td)
            capability = self.capability(authority)
            bound.reserve(
                Request("r", "task", "scope", 1, "one"), capability, now=0
            )
            with self.assertRaises(RequestConflict):
                bound.reserve(
                    Request("r", "task", "scope", 1, "two"), capability, now=0
                )

    def test_durable_verifier_detects_corrupt_capability_digest(self):
        with tempfile.TemporaryDirectory() as td:
            journal, authority, bound, sink = self.setup(td)
            request = Request("r", "task", "scope", 1, "payload")
            bound.reserve(request, self.capability(authority), now=0)
            q = sqlite3.connect(Path(td) / "journal.db")
            q.execute(
                "UPDATE broker_requests SET capability_claim_digest=? WHERE request_id='r'",
                ("z" * 64,),
            )
            q.commit()
            q.close()
            with self.assertRaises(CapabilityBindingError):
                bound.verify_durable()

    def test_newer_capability_head_makes_older_generation_stale(self):
        with tempfile.TemporaryDirectory() as td:
            journal, authority, bound, sink = self.setup(td)
            bound.observe_capability(self.capability(authority, generation=2))
            with self.assertRaises(cap.StaleCapability):
                bound.reserve(
                    Request("old", "task", "scope", 1, "payload"),
                    self.capability(authority, generation=1),
                    now=1,
                )

    def test_capability_head_survives_restart(self):
        with tempfile.TemporaryDirectory() as td:
            journal, authority, bound, sink = self.setup(td)
            bound.observe_capability(self.capability(authority, generation=2))
            reopened = CapabilityBoundJournal(
                TransactionalJournal(Path(td) / "journal.db", 1), authority
            )
            with self.assertRaises(cap.StaleCapability):
                reopened.observe_capability(
                    self.capability(authority, generation=1)
                )
            self.assertTrue(reopened.verify_durable())

    def test_same_generation_capability_head_substitution_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            journal, authority, bound, sink = self.setup(td)
            bound.observe_capability(
                self.capability(authority, generation=1, retention=10)
            )
            with self.assertRaises(cap.StaleCapability):
                bound.observe_capability(
                    self.capability(authority, generation=1, retention=1000)
                )


if __name__ == "__main__":
    unittest.main()
