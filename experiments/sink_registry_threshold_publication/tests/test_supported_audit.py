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
    TransactionalJournal,
)


def make_keys(prefix, count=3):
    raw = [f"{prefix}-{i}".encode() for i in range(count)]
    return raw, {key_id(k): k.hex() for k in raw}


def root_sigs(keys, payload, count):
    return tuple(Signature(key_id(k), sign(k, payload)) for k in keys[:count])


def ad(label):
    return hashlib.sha256(label.encode()).hexdigest()


class SupportedAuditTests(unittest.TestCase):
    def setUp(self):
        self.k1, m1 = make_keys("root1", 3)
        self.r1 = RootState("sink-registry", 1, 1, 2, m1)
        self.k2, m2 = make_keys("root2", 3)
        self.r2 = RootState("sink-registry", 2, 1, 2, m2)
        _, rm = make_keys("recovery", 4)
        self.recovery = RecoveryAuthority(1, 3, rm)
        self.probe = cap.ProbeAuthority(issuer_id="probe", key=b"probe", generation=1)

    def stack(self, td):
        path = Path(td) / "journal.db"
        journal = TransactionalJournal(path, 1)
        bound = CapabilityBoundJournal(journal, self.probe)
        lifecycle = DurableRegistryAuthority(path, self.r1, self.recovery)
        registry = ThresholdLifecycleRegistryBoundJournal(bound, lifecycle)
        return journal, lifecycle, registry

    def capability(self, generation=1):
        claim = cap.CapabilityClaim(
            "sink-A", generation, True, True, True, True, 100, "lab077-audit"
        )
        sink = cap.SimulatedSink(idempotent=True, request_bound=True, reconcile=True)
        return cap.VerifiedCapability(claim, self.probe.attest(claim, sink))

    def envelope(self, root, keys, generation=1, predecessor=None, endpoint="https://a.example"):
        raw = publication_entry(
            root,
            sink_id="sink-A",
            generation=generation,
            adapter_digest=ad(f"adapter-{generation}"),
            endpoint_origin=endpoint,
            operation_profile="charge-v1",
            predecessor_entry_digest=predecessor,
        )
        return make_envelope(
            root,
            raw,
            tuple(sign_publication(raw, key) for key in keys[: root.threshold]),
        )

    @staticmethod
    def runtime(entry, sink):
        return RuntimeAdapter(
            entry.adapter_digest, entry.endpoint_origin, entry.operation_profile, sink
        )

    def rotate(self, lifecycle):
        p = rotation_payload(self.r1, self.r2)
        lifecycle.rotate(
            self.r2,
            root_sigs(self.k1, p, self.r1.threshold),
            root_sigs(self.k2, p, self.r2.threshold),
        )

    def test_confirmed_retry_does_not_publish_unseen_successor(self):
        with tempfile.TemporaryDirectory() as td:
            journal, lifecycle, registry = self.stack(td)
            sink = IdempotentSink(Path(td) / "sink.db")
            e1 = self.envelope(self.r1, self.k1)
            request = Request("r", "task", "scope", 1, "payload")
            first = ThresholdLifecycleRegistryBrokerWorker(
                registry, self.runtime(e1.entry, sink), b"secret"
            ).process(request, self.capability(), e1, now=0)
            self.rotate(lifecycle)

            # Construct a valid current successor but do NOT publish it.
            e2 = self.envelope(
                self.r2,
                self.k2,
                generation=2,
                predecessor=e1.entry_digest,
                endpoint="https://b.example",
            )
            attacker = IdempotentSink(Path(td) / "attacker.db")
            replay = ThresholdLifecycleRegistryBrokerWorker(
                registry,
                RuntimeAdapter(ad("attacker"), "https://attacker.example", "evil", attacker),
                b"wrong",
            ).process(request, self.capability(generation=2), e2, now=2)

            self.assertEqual(replay, ("ALREADY_COMMITTED", first[1]))
            self.assertEqual(attacker.apply_count(), 0)
            self.assertEqual(registry.head("sink-A"), e1.entry)
            q = journal._con()
            try:
                self.assertIsNone(
                    q.execute(
                        "SELECT 1 FROM sink_registry_entries WHERE entry_digest=?",
                        (e2.entry_digest,),
                    ).fetchone()
                )
                self.assertIsNone(
                    q.execute(
                        "SELECT 1 FROM registry_threshold_publications WHERE entry_digest=?",
                        (e2.entry_digest,),
                    ).fetchone()
                )
            finally:
                q.close()


if __name__ == "__main__":
    unittest.main()
