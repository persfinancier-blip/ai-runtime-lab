import hashlib
import tempfile
import unittest
from pathlib import Path

from experiments.anchor_threshold_root.protocol import RecoveryAuthority, RootState, key_id
from experiments.sink_capability_contract import protocol as cap
from experiments.sink_registry_binding import protocol as registry_base
from experiments.sink_registry_threshold_publication.protocol import (
    make_envelope,
    publication_entry,
    sign_publication,
)
from experiments.sink_registry_threshold_publication.supported import (
    DurableRegistryAuthority,
    RuntimeAdapter,
    ThresholdLifecycleRegistryBoundJournal,
    ThresholdLifecycleRegistryBrokerWorker,
)
from experiments.transactional_broker_journal.capability import CapabilityBoundJournal
from experiments.transactional_broker_journal.protocol import (
    IdempotentSink,
    Request,
    StaleCredential,
    TransactionalJournal,
)


def make_keys(prefix, count=3):
    raw = [f"{prefix}-{i}".encode() for i in range(count)]
    return raw, {key_id(k): k.hex() for k in raw}


def ad(label):
    return hashlib.sha256(label.encode()).hexdigest()


class FinalAuditTests(unittest.TestCase):
    def setUp(self):
        self.keys, root_map = make_keys("root", 3)
        self.root = RootState("sink-registry", 1, 1, 2, root_map)
        _, recovery_map = make_keys("recovery", 4)
        self.recovery = RecoveryAuthority(1, 3, recovery_map)
        self.probe = cap.ProbeAuthority(issuer_id="probe", key=b"probe", generation=1)

    def stack(self, td):
        path = Path(td) / "journal.db"
        journal = TransactionalJournal(path, 1)
        bound = CapabilityBoundJournal(journal, self.probe)
        lifecycle = DurableRegistryAuthority(path, self.root, self.recovery)
        registry = ThresholdLifecycleRegistryBoundJournal(bound, lifecycle)
        return journal, registry

    def capability(self, generation=1, sink_id="sink-A"):
        claim = cap.CapabilityClaim(
            sink_id, generation, True, True, True, True, 100, "lab077-final"
        )
        probe_sink = cap.SimulatedSink(idempotent=True, request_bound=True, reconcile=True)
        return cap.VerifiedCapability(claim, self.probe.attest(claim, probe_sink))

    def envelope(self):
        raw = publication_entry(
            self.root,
            sink_id="sink-A",
            generation=1,
            adapter_digest=ad("adapter"),
            endpoint_origin="https://a.example",
            operation_profile="charge-v1",
        )
        return make_envelope(
            self.root,
            raw,
            tuple(sign_publication(raw, key) for key in self.keys[:2]),
        )

    @staticmethod
    def runtime(entry, sink):
        return RuntimeAdapter(
            entry.adapter_digest, entry.endpoint_origin, entry.operation_profile, sink
        )

    def test_stale_credential_rolls_back_publication_and_intent_together(self):
        with tempfile.TemporaryDirectory() as td:
            journal, registry = self.stack(td)
            envelope = self.envelope()
            request = Request("r", "task", "scope", 2, "payload")
            with self.assertRaises(StaleCredential):
                registry.reserve(request, self.capability(), envelope, now=0)
            q = journal._con()
            try:
                self.assertEqual(q.execute("SELECT COUNT(*) FROM broker_requests").fetchone()[0], 0)
                self.assertEqual(q.execute("SELECT COUNT(*) FROM sink_registry_entries").fetchone()[0], 0)
                self.assertEqual(q.execute("SELECT COUNT(*) FROM sink_registry_heads").fetchone()[0], 0)
                self.assertEqual(q.execute("SELECT COUNT(*) FROM registry_threshold_publications").fetchone()[0], 0)
            finally:
                q.close()

    def test_capability_sink_mismatch_rolls_back_publication(self):
        with tempfile.TemporaryDirectory() as td:
            journal, registry = self.stack(td)
            envelope = self.envelope()
            request = Request("r", "task", "scope", 1, "payload")
            with self.assertRaises(registry_base.RegistryBindingError):
                registry.reserve(request, self.capability(sink_id="sink-B"), envelope, now=0)
            q = journal._con()
            try:
                self.assertEqual(q.execute("SELECT COUNT(*) FROM broker_requests").fetchone()[0], 0)
                self.assertEqual(q.execute("SELECT COUNT(*) FROM sink_registry_entries").fetchone()[0], 0)
                self.assertEqual(q.execute("SELECT COUNT(*) FROM registry_threshold_publications").fetchone()[0], 0)
            finally:
                q.close()

    def test_confirmed_retry_needs_no_current_capability_authority(self):
        with tempfile.TemporaryDirectory() as td:
            _, registry = self.stack(td)
            envelope = self.envelope()
            sink = IdempotentSink(Path(td) / "sink.db")
            request = Request("r", "task", "scope", 1, "payload")
            first = ThresholdLifecycleRegistryBrokerWorker(
                registry, self.runtime(envelope.entry, sink), b"secret"
            ).process(request, self.capability(), envelope, now=0)
            # A terminal receipt read must return before dereferencing this object.
            replay = ThresholdLifecycleRegistryBrokerWorker(
                registry,
                RuntimeAdapter(ad("wrong"), "https://evil.example", "evil", IdempotentSink(Path(td) / "evil.db")),
                b"wrong",
            ).process(request, object(), object(), now=50)
            self.assertEqual(replay, ("ALREADY_COMMITTED", first[1]))

    def test_pending_intent_cannot_inherit_rotated_capability(self):
        with tempfile.TemporaryDirectory() as td:
            _, registry = self.stack(td)
            envelope = self.envelope()
            request = Request("r", "task", "scope", 1, "payload")
            status, _, _, _ = registry.reserve(
                request, self.capability(generation=1), envelope, now=0
            )
            self.assertEqual(status, "INTENT")
            with self.assertRaises(cap.StaleCapability):
                registry.reserve(
                    request, self.capability(generation=2), envelope, now=1
                )


if __name__ == "__main__":
    unittest.main()
