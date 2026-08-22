import hashlib
import tempfile
import unittest
from pathlib import Path

from experiments.anchor_threshold_root.protocol import (
    RecoveryAuthority,
    RootState,
    Signature,
    key_id,
    rotation_payload,
    sign,
)
from experiments.sink_capability_contract import protocol as cap
from experiments.sink_registry_authority_lifecycle.integration import (
    LifecycleRegistryBoundJournal,
    LifecycleRegistryBrokerWorker,
)
from experiments.sink_registry_authority_lifecycle.protocol import (
    DurableRegistryAuthority,
    EntryAuthError,
)
from experiments.sink_registry_binding.supported import RegistryEntry, RuntimeAdapter
from experiments.transactional_broker_journal.capability import CapabilityBoundJournal
from experiments.transactional_broker_journal.protocol import (
    IdempotentSink,
    Request,
    TransactionalJournal,
)


def adapter_digest(label):
    return hashlib.sha256(label.encode()).hexdigest()


def make_keys(prefix, count=3):
    raw = [f"{prefix}-{i}".encode() for i in range(count)]
    return raw, {key_id(k): k.hex() for k in raw}


def signatures(keys, payload, count=2):
    return tuple(Signature(key_id(k), sign(k, payload)) for k in keys[:count])


class RealLifecycleIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.root1_keys, root1_map = make_keys("root1")
        self.root1 = RootState("sink-registry", 1, 1, 2, root1_map)
        self.root2_keys, root2_map = make_keys("root2")
        self.root2 = RootState("sink-registry", 2, 1, 2, root2_map)
        recovery_keys, recovery_map = make_keys("recovery", 4)
        self.recovery = RecoveryAuthority(1, 3, recovery_map)
        self.recovery_keys = recovery_keys
        self.probe = cap.ProbeAuthority(
            issuer_id="probe", key=b"probe-key", generation=1
        )

    def capability(self, *, generation=1, reconcile=True):
        claim = cap.CapabilityClaim(
            sink_id="sink-A",
            generation=generation,
            mutating=True,
            stable_idempotency_key=True,
            request_bound_key=True,
            reconcile_by_key=reconcile,
            retention_seconds=100,
            source="lab076-real-integration",
        )
        probe_sink = cap.SimulatedSink(
            idempotent=True, request_bound=True, reconcile=reconcile
        )
        return cap.VerifiedCapability(claim, self.probe.attest(claim, probe_sink))

    def stack(self, td):
        path = Path(td) / "journal.db"
        journal = TransactionalJournal(path, 1)
        bound = CapabilityBoundJournal(journal, self.probe)
        lifecycle = DurableRegistryAuthority(path, self.root1, self.recovery)
        registry = LifecycleRegistryBoundJournal(bound, lifecycle)
        sink = IdempotentSink(Path(td) / "sink.db")
        return journal, lifecycle, registry, sink

    def entry(self, lifecycle, root, signer, generation=1, predecessor=None, endpoint="https://a.example"):
        raw = RegistryEntry(
            "sink-A",
            generation,
            adapter_digest(f"adapter-{generation}"),
            endpoint,
            "charge-v1",
            predecessor,
            key_id(signer),
            root.version,
        )
        return lifecycle.issue(raw, signer)

    def rotate_root(self, lifecycle):
        payload = rotation_payload(self.root1, self.root2)
        lifecycle.rotate(
            self.root2,
            signatures(self.root1_keys, payload),
            signatures(self.root2_keys, payload),
        )

    def runtime(self, entry, sink):
        return RuntimeAdapter(
            entry.adapter_digest,
            entry.endpoint_origin,
            entry.operation_profile,
            sink,
        )

    def test_new_request_binds_real_journal_to_exact_authority_backed_entry(self):
        with tempfile.TemporaryDirectory() as td:
            journal, lifecycle, registry, sink = self.stack(td)
            e1 = self.entry(lifecycle, self.root1, self.root1_keys[0])
            request = Request("r", "task", "scope", 1, "payload")
            result = LifecycleRegistryBrokerWorker(
                registry, self.runtime(e1, sink), b"secret"
            ).process(request, self.capability(), e1, now=0)
            self.assertEqual(result[0], "COMMITTED")
            self.assertTrue(registry.verify_durable())
            q = journal._con()
            try:
                bound = q.execute(
                    "SELECT authority_id,authority_version FROM registry_authorized_entries "
                    "WHERE entry_digest=?",
                    (e1.entry_digest,),
                ).fetchone()
            finally:
                q.close()
            self.assertEqual(bound[1], 1)
            self.assertTrue(bound[0])

    def test_root_rotation_does_not_invalidate_already_accepted_current_registry_head(self):
        with tempfile.TemporaryDirectory() as td:
            _, lifecycle, registry, sink = self.stack(td)
            e1 = self.entry(lifecycle, self.root1, self.root1_keys[0])
            registry.observe(e1)
            self.rotate_root(lifecycle)
            request = Request("after-rotation", "task", "scope", 1, "payload")
            outcome, _ = LifecycleRegistryBrokerWorker(
                registry, self.runtime(e1, sink), b"secret"
            ).process(request, self.capability(), e1, now=1)
            self.assertEqual(outcome, "COMMITTED")
            self.assertEqual(registry.head("sink-A"), e1)

    def test_old_signer_cannot_publish_successor_after_authority_rotation(self):
        with tempfile.TemporaryDirectory() as td:
            _, lifecycle, registry, _ = self.stack(td)
            e1 = self.entry(lifecycle, self.root1, self.root1_keys[0])
            registry.observe(e1)
            stale_e2 = self.entry(
                lifecycle,
                self.root1,
                self.root1_keys[0],
                generation=2,
                predecessor=e1.entry_digest,
                endpoint="https://b.example",
            )
            self.rotate_root(lifecycle)
            with self.assertRaises(EntryAuthError):
                registry.observe(stale_e2)

    def test_current_root_can_publish_successor_of_historical_head(self):
        with tempfile.TemporaryDirectory() as td:
            _, lifecycle, registry, _ = self.stack(td)
            e1 = self.entry(lifecycle, self.root1, self.root1_keys[0])
            registry.observe(e1)
            self.rotate_root(lifecycle)
            e2 = self.entry(
                lifecycle,
                self.root2,
                self.root2_keys[0],
                generation=2,
                predecessor=e1.entry_digest,
                endpoint="https://b.example",
            )
            registry.observe(e2)
            self.assertEqual(registry.head("sink-A"), e2)
            self.assertEqual(lifecycle.verify_historical_entry(e1.entry_digest), e1)

    def test_confirmed_receipt_survives_authority_and_registry_rotation_without_reexecution(self):
        with tempfile.TemporaryDirectory() as td:
            _, lifecycle, registry, sink = self.stack(td)
            e1 = self.entry(lifecycle, self.root1, self.root1_keys[0])
            request = Request("r", "task", "scope", 1, "payload")
            first = LifecycleRegistryBrokerWorker(
                registry, self.runtime(e1, sink), b"secret"
            ).process(request, self.capability(generation=1), e1, now=0)
            self.rotate_root(lifecycle)
            e2 = self.entry(
                lifecycle,
                self.root2,
                self.root2_keys[0],
                generation=2,
                predecessor=e1.entry_digest,
                endpoint="https://b.example",
            )
            registry.observe(e2)
            attacker = IdempotentSink(Path(td) / "attacker.db")
            replay = LifecycleRegistryBrokerWorker(
                registry,
                RuntimeAdapter(
                    adapter_digest("attacker"),
                    "https://attacker.example",
                    "evil",
                    attacker,
                ),
                b"wrong",
            ).process(request, self.capability(generation=2), e2, now=2)
            self.assertEqual(replay, ("ALREADY_COMMITTED", first[1]))
            self.assertEqual(attacker.apply_count(), 0)


if __name__ == "__main__":
    unittest.main()
