import hashlib
import json
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
from experiments.sink_registry_authority_lifecycle.audit_fixes import (
    ConsistentDurableRegistryAuthority,
)
from experiments.sink_registry_binding.supported import RegistryEntry, RuntimeAdapter
from experiments.sink_registry_threshold_publication.integration import (
    ThresholdLifecycleRegistryBoundJournal,
    ThresholdLifecycleRegistryBrokerWorker,
)
from experiments.sink_registry_threshold_publication.protocol import (
    AuthorityMismatch,
    InvalidSignatureSet,
    ProofSubstitution,
    ThresholdEnvelope,
    ThresholdProof,
    make_envelope,
    publication_entry,
    sign_publication,
)
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


def signatures(keys, payload, count):
    return tuple(Signature(key_id(k), sign(k, payload)) for k in keys[:count])


class ThresholdLifecycleIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.root1_keys, root1_map = make_keys("root1", 3)
        self.root1 = RootState("sink-registry", 1, 1, 2, root1_map)
        self.root2_keys, root2_map = make_keys("root2", 4)
        self.root2 = RootState("sink-registry", 2, 1, 3, root2_map)
        recovery_keys, recovery_map = make_keys("recovery", 4)
        self.recovery = RecoveryAuthority(1, 3, recovery_map)
        self.recovery_keys = recovery_keys
        self.probe = cap.ProbeAuthority(
            issuer_id="probe", key=b"probe-key", generation=1
        )

    def stack(self, td):
        path = Path(td) / "journal.db"
        journal = TransactionalJournal(path, 1)
        bound = CapabilityBoundJournal(journal, self.probe)
        lifecycle = ConsistentDurableRegistryAuthority(
            path, self.root1, self.recovery
        )
        registry = ThresholdLifecycleRegistryBoundJournal(bound, lifecycle)
        sink = IdempotentSink(Path(td) / "sink.db")
        return journal, lifecycle, registry, sink

    def capability(self, generation=1):
        claim = cap.CapabilityClaim(
            sink_id="sink-A",
            generation=generation,
            mutating=True,
            stable_idempotency_key=True,
            request_bound_key=True,
            reconcile_by_key=True,
            retention_seconds=100,
            source="lab077-integration",
        )
        probe_sink = cap.SimulatedSink(
            idempotent=True, request_bound=True, reconcile=True
        )
        return cap.VerifiedCapability(claim, self.probe.attest(claim, probe_sink))

    def envelope(
        self,
        root,
        keys,
        *,
        generation=1,
        predecessor=None,
        endpoint="https://a.example",
        signature_count=None,
    ):
        raw = publication_entry(
            root,
            sink_id="sink-A",
            generation=generation,
            adapter_digest=adapter_digest(f"adapter-{generation}"),
            endpoint_origin=endpoint,
            operation_profile="charge-v1",
            predecessor_entry_digest=predecessor,
        )
        count = root.threshold if signature_count is None else signature_count
        sigs = tuple(sign_publication(raw, key) for key in keys[:count])
        return make_envelope(root, raw, sigs)

    def rotate_root(self, lifecycle):
        payload = rotation_payload(self.root1, self.root2)
        lifecycle.rotate(
            self.root2,
            signatures(self.root1_keys, payload, self.root1.threshold),
            signatures(self.root2_keys, payload, self.root2.threshold),
        )

    @staticmethod
    def runtime(entry, sink):
        return RuntimeAdapter(
            entry.adapter_digest,
            entry.endpoint_origin,
            entry.operation_profile,
            sink,
        )

    def test_threshold_envelope_publishes_and_executes(self):
        with tempfile.TemporaryDirectory() as td:
            _, _, registry, sink = self.stack(td)
            envelope = self.envelope(self.root1, self.root1_keys)
            request = Request("r", "task", "scope", 1, "payload")
            result = ThresholdLifecycleRegistryBrokerWorker(
                registry, self.runtime(envelope.entry, sink), b"secret"
            ).process(request, self.capability(), envelope, now=0)
            self.assertEqual(result[0], "COMMITTED")
            self.assertEqual(sink.apply_count(), 1)
            self.assertTrue(registry.verify_durable())

    def test_bare_single_signature_entry_cannot_create_publication(self):
        with tempfile.TemporaryDirectory() as td:
            _, lifecycle, registry, _ = self.stack(td)
            signer = self.root1_keys[0]
            bare = RegistryEntry(
                "sink-A",
                1,
                adapter_digest("single"),
                "https://evil.example",
                "charge-v1",
                None,
                key_id(signer),
                self.root1.version,
            )
            signed = lifecycle.issue(bare, signer)
            with self.assertRaises(ProofSubstitution):
                registry.observe(signed)

    def test_rotation_after_proof_collection_blocks_old_root_publication(self):
        with tempfile.TemporaryDirectory() as td:
            _, lifecycle, registry, _ = self.stack(td)
            stale = self.envelope(self.root1, self.root1_keys)
            self.rotate_root(lifecycle)
            with self.assertRaises(AuthorityMismatch):
                registry.observe(stale)

    def test_unpublished_old_root_proof_cannot_activate_after_rotation(self):
        with tempfile.TemporaryDirectory() as td:
            journal, lifecycle, registry, _ = self.stack(td)
            stale = self.envelope(self.root1, self.root1_keys)
            q = journal._con()
            try:
                q.execute("BEGIN IMMEDIATE")
                q.execute(
                    "INSERT INTO registry_threshold_publications VALUES(?,?,?,?,?)",
                    (
                        stale.entry_digest,
                        registry._proof_json(stale.proof),
                        stale.proof.proof_digest,
                        stale.proof.authority_id,
                        stale.proof.authority_version,
                    ),
                )
                q.commit()
            finally:
                q.close()
            self.rotate_root(lifecycle)
            with self.assertRaises(ProofSubstitution):
                registry.observe(stale)

    def test_new_root_threshold_is_enforced_after_rotation(self):
        with tempfile.TemporaryDirectory() as td:
            _, lifecycle, registry, _ = self.stack(td)
            e1 = self.envelope(self.root1, self.root1_keys)
            registry.observe(e1)
            self.rotate_root(lifecycle)
            raw = publication_entry(
                self.root2,
                sink_id="sink-A",
                generation=2,
                adapter_digest=adapter_digest("adapter-2"),
                endpoint_origin="https://b.example",
                operation_profile="charge-v1",
                predecessor_entry_digest=e1.entry_digest,
            )
            weak_proof = ThresholdProof(
                e1.proof.authority_id,
                self.root2.version,
                tuple(sign_publication(raw, key) for key in self.root2_keys[:2]),
            )
            # Construct directly so make_envelope cannot pre-reject the intentionally
            # weak proof. Publication must fail at the supported boundary.
            weak_entry = RegistryEntry(
                **raw.unsigned, signature=weak_proof.proof_digest
            )
            weak = ThresholdEnvelope(weak_entry, weak_proof)
            with self.assertRaises((AuthorityMismatch, InvalidSignatureSet)):
                registry.observe(weak)

            strong = self.envelope(
                self.root2,
                self.root2_keys,
                generation=2,
                predecessor=e1.entry_digest,
                endpoint="https://b.example",
            )
            registry.observe(strong)
            self.assertEqual(registry.head("sink-A"), strong.entry)

    def test_threshold_proof_corruption_fails_restart_audit(self):
        with tempfile.TemporaryDirectory() as td:
            journal, _, registry, _ = self.stack(td)
            envelope = self.envelope(self.root1, self.root1_keys)
            registry.observe(envelope)
            q = journal._con()
            try:
                row = q.execute(
                    "SELECT proof_json FROM registry_threshold_publications "
                    "WHERE entry_digest=?",
                    (envelope.entry_digest,),
                ).fetchone()
                proof = json.loads(row[0])
                proof["signatures"][0]["signature"] = "0" * 64
                q.execute(
                    "UPDATE registry_threshold_publications SET proof_json=? "
                    "WHERE entry_digest=?",
                    (
                        json.dumps(proof, sort_keys=True, separators=(",", ":")),
                        envelope.entry_digest,
                    ),
                )
                q.commit()
            finally:
                q.close()
            with self.assertRaises((ProofSubstitution, InvalidSignatureSet)):
                registry.verify_durable()

    def test_root_rotation_does_not_invalidate_published_historical_proof(self):
        with tempfile.TemporaryDirectory() as td:
            _, lifecycle, registry, sink = self.stack(td)
            envelope = self.envelope(self.root1, self.root1_keys)
            registry.observe(envelope)
            self.rotate_root(lifecycle)
            request = Request("after", "task", "scope", 1, "payload")
            result = ThresholdLifecycleRegistryBrokerWorker(
                registry, self.runtime(envelope.entry, sink), b"secret"
            ).process(request, self.capability(), envelope, now=1)
            self.assertEqual(result[0], "COMMITTED")
            self.assertEqual(registry.verify_historical_entry(envelope.entry_digest), envelope.entry)

    def test_confirmed_receipt_survives_root_and_registry_rotation(self):
        with tempfile.TemporaryDirectory() as td:
            _, lifecycle, registry, sink = self.stack(td)
            e1 = self.envelope(self.root1, self.root1_keys)
            request = Request("same", "task", "scope", 1, "payload")
            first = ThresholdLifecycleRegistryBrokerWorker(
                registry, self.runtime(e1.entry, sink), b"secret"
            ).process(request, self.capability(generation=1), e1, now=0)
            self.rotate_root(lifecycle)
            e2 = self.envelope(
                self.root2,
                self.root2_keys,
                generation=2,
                predecessor=e1.entry_digest,
                endpoint="https://b.example",
            )
            registry.observe(e2)
            attacker = IdempotentSink(Path(td) / "attacker.db")
            replay = ThresholdLifecycleRegistryBrokerWorker(
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

    def test_supported_worker_rejects_old_lab076_journal(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "journal.db"
            journal = TransactionalJournal(path, 1)
            bound = CapabilityBoundJournal(journal, self.probe)
            lifecycle = ConsistentDurableRegistryAuthority(
                path, self.root1, self.recovery
            )
            from experiments.sink_registry_authority_lifecycle.audit_fixes import (
                CorrectedLifecycleRegistryBoundJournal,
            )
            old = CorrectedLifecycleRegistryBoundJournal(bound, lifecycle)
            sink = IdempotentSink(Path(td) / "sink.db")
            envelope = self.envelope(self.root1, self.root1_keys)
            with self.assertRaises(Exception):
                ThresholdLifecycleRegistryBrokerWorker(
                    old, self.runtime(envelope.entry, sink), b"secret"
                )


if __name__ == "__main__":
    unittest.main()
