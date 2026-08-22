import hashlib
import tempfile
import unittest
from pathlib import Path

from experiments.sink_capability_contract import protocol as cap
from experiments.sink_registry_binding.supported import (
    HistoricalExecutionBlocked,
    RegistryAuthority,
    RegistryBoundJournal,
    RegistryBrokerWorker,
    RegistryEntry,
    RuntimeAdapter,
)
from experiments.transactional_broker_journal.capability import CapabilityBoundJournal
from experiments.transactional_broker_journal.protocol import (
    IdempotentSink,
    Request,
    TransactionalJournal,
    UnknownOutcome,
)


def adapter_digest(label: str) -> str:
    return hashlib.sha256(label.encode()).hexdigest()


class RealJournalIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.probe = cap.ProbeAuthority(
            issuer_id="probe", key=b"probe-key", generation=1
        )
        self.registry_auth = RegistryAuthority("registry", b"registry-key", 1)

    def capability(self, *, generation=1, reconcile=True):
        claim = cap.CapabilityClaim(
            sink_id="sink-A",
            generation=generation,
            mutating=True,
            stable_idempotency_key=True,
            request_bound_key=True,
            reconcile_by_key=reconcile,
            retention_seconds=100,
            source="lab075-real-integration",
        )
        probe_sink = cap.SimulatedSink(
            idempotent=True, request_bound=True, reconcile=reconcile
        )
        return cap.VerifiedCapability(claim, self.probe.attest(claim, probe_sink))

    def entry(self, generation=1, *, predecessor=None, endpoint="https://a.example"):
        raw = RegistryEntry(
            "sink-A",
            generation,
            adapter_digest(f"adapter-{generation}"),
            endpoint,
            "charge-v1",
            predecessor,
            "registry",
            1,
        )
        return self.registry_auth.issue(raw)

    def setup_stack(self, td):
        root = Path(td)
        journal = TransactionalJournal(root / "journal.db", 1)
        bound = CapabilityBoundJournal(journal, self.probe)
        registry = RegistryBoundJournal(bound, self.registry_auth)
        sink = IdempotentSink(root / "sink.db")
        return journal, bound, registry, sink

    def runtime(self, entry, sink):
        return RuntimeAdapter(
            entry.adapter_digest,
            entry.endpoint_origin,
            entry.operation_profile,
            sink,
        )

    def test_real_journal_new_request_is_atomically_capability_and_registry_bound(self):
        with tempfile.TemporaryDirectory() as td:
            journal, _, registry, sink = self.setup_stack(td)
            entry = self.entry()
            request = Request("r", "task", "scope", 1, "payload")
            worker = RegistryBrokerWorker(
                registry, self.runtime(entry, sink), b"secret"
            )
            outcome, receipt = worker.process(
                request, self.capability(), entry, now=0
            )
            self.assertEqual(outcome, "COMMITTED")
            self.assertTrue(receipt)
            q = journal._con()
            try:
                row = q.execute(
                    "SELECT capability_sink_id,capability_generation,registry_entry_digest,"
                    "registry_generation,status FROM broker_requests WHERE request_id='r'"
                ).fetchone()
            finally:
                q.close()
            self.assertEqual(row, ("sink-A", 1, entry.entry_digest, 1, "CONFIRMED"))
            self.assertTrue(registry.verify_durable())

    def test_confirmed_receipt_survives_registry_and_capability_rotation_without_adapter_use(self):
        with tempfile.TemporaryDirectory() as td:
            _, _, registry, sink = self.setup_stack(td)
            e1 = self.entry()
            request = Request("r", "task", "scope", 1, "payload")
            first = RegistryBrokerWorker(
                registry, self.runtime(e1, sink), b"secret"
            ).process(request, self.capability(generation=1), e1, now=0)
            e2 = self.entry(
                2, predecessor=e1.entry_digest, endpoint="https://b.example"
            )
            registry.observe(e2)
            attacker_sink = IdempotentSink(Path(td) / "attacker.db")
            replay = RegistryBrokerWorker(
                registry,
                RuntimeAdapter(
                    adapter_digest("attacker"),
                    "https://attacker.example",
                    "evil",
                    attacker_sink,
                ),
                b"wrong-secret",
            ).process(request, self.capability(generation=2), e2, now=1)
            self.assertEqual(replay[0], "ALREADY_COMMITTED")
            self.assertEqual(replay[1], first[1])
            self.assertEqual(attacker_sink.apply_count(), 0)

    def test_unknown_after_direct_successor_is_reconciliation_only(self):
        with tempfile.TemporaryDirectory() as td:
            _, _, registry, sink = self.setup_stack(td)
            e1 = self.entry()
            request = Request("r", "task", "scope", 1, "payload")
            w1 = RegistryBrokerWorker(registry, self.runtime(e1, sink), b"secret")
            with self.assertRaises(UnknownOutcome):
                w1.process(
                    request,
                    self.capability(generation=1),
                    e1,
                    now=0,
                    timeout_after_commit=True,
                )
            self.assertEqual(sink.apply_count(), 1)
            e2 = self.entry(
                2, predecessor=e1.entry_digest, endpoint="https://b.example"
            )
            registry.observe(e2)
            w2 = RegistryBrokerWorker(registry, self.runtime(e2, sink), b"secret")
            outcome, _ = w2.process(
                request, self.capability(generation=2), e2, now=1
            )
            self.assertEqual(outcome, "RECONCILED")
            self.assertEqual(sink.apply_count(), 1)

    def test_unknown_direct_successor_still_requires_current_reconcile_capability(self):
        with tempfile.TemporaryDirectory() as td:
            _, _, registry, sink = self.setup_stack(td)
            e1 = self.entry()
            request = Request("r", "task", "scope", 1, "payload")
            with self.assertRaises(UnknownOutcome):
                RegistryBrokerWorker(
                    registry, self.runtime(e1, sink), b"secret"
                ).process(
                    request,
                    self.capability(generation=1),
                    e1,
                    now=0,
                    timeout_after_commit=True,
                )
            e2 = self.entry(
                2, predecessor=e1.entry_digest, endpoint="https://b.example"
            )
            registry.observe(e2)
            with self.assertRaises(HistoricalExecutionBlocked):
                RegistryBrokerWorker(
                    registry, self.runtime(e2, sink), b"secret"
                ).process(
                    request,
                    self.capability(generation=2, reconcile=False),
                    e2,
                    now=1,
                )
            self.assertEqual(sink.apply_count(), 1)


if __name__ == "__main__":
    unittest.main()
