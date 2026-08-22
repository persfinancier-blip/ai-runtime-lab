import tempfile
import threading
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
from experiments.sink_registry_threshold_publication.integration import (
    ThresholdLifecycleRegistryBoundJournal,
)
from experiments.sink_registry_threshold_publication.protocol import (
    AuthorityMismatch,
    InvalidSignatureSet,
    ThresholdEnvelope,
    ThresholdProof,
    authority_id,
    publication_entry,
    sign_publication,
)
from experiments.transactional_broker_journal.capability import CapabilityBoundJournal
from experiments.transactional_broker_journal.protocol import TransactionalJournal


def make_keys(prefix, count):
    raw = [f"{prefix}-{i}".encode() for i in range(count)]
    return raw, {key_id(k): k.hex() for k in raw}


def root_sigs(keys, payload, count):
    return tuple(Signature(key_id(k), sign(k, payload)) for k in keys[:count])


def adapter_digest(label):
    import hashlib
    return hashlib.sha256(label.encode()).hexdigest()


class IntegrationAuditTests(unittest.TestCase):
    def setUp(self):
        self.k1, m1 = make_keys("r1", 3)
        self.r1 = RootState("sink-registry", 1, 1, 2, m1)
        self.k2, m2 = make_keys("r2", 4)
        self.r2 = RootState("sink-registry", 2, 1, 3, m2)
        rk, rm = make_keys("recovery", 4)
        self.recovery = RecoveryAuthority(1, 3, rm)
        self.probe = cap.ProbeAuthority(
            issuer_id="probe", key=b"probe", generation=1
        )

    def stack(self, td):
        path = Path(td) / "journal.db"
        journal = TransactionalJournal(path, 1)
        bound = CapabilityBoundJournal(journal, self.probe)
        lifecycle = ConsistentDurableRegistryAuthority(path, self.r1, self.recovery)
        return lifecycle, ThresholdLifecycleRegistryBoundJournal(bound, lifecycle)

    def rotate(self, lifecycle):
        payload = rotation_payload(self.r1, self.r2)
        lifecycle.rotate(
            self.r2,
            root_sigs(self.k1, payload, 2),
            root_sigs(self.k2, payload, 3),
        )

    @staticmethod
    def raw(root, generation=1, predecessor=None):
        return publication_entry(
            root,
            sink_id="sink-A",
            generation=generation,
            adapter_digest=adapter_digest(f"a-{generation}"),
            endpoint_origin=f"https://{generation}.example",
            operation_profile="charge-v1",
            predecessor_entry_digest=predecessor,
        )

    def test_new_root_really_requires_three_signers(self):
        with tempfile.TemporaryDirectory() as td:
            lifecycle, registry = self.stack(td)
            first_raw = self.raw(self.r1)
            first_proof = ThresholdProof(
                authority_id(self.r1),
                1,
                tuple(sign_publication(first_raw, k) for k in self.k1[:2]),
            )
            from experiments.sink_registry_binding.protocol import RegistryEntry
            first_entry = RegistryEntry(
                **first_raw.unsigned, signature=first_proof.proof_digest
            )
            registry.observe(ThresholdEnvelope(first_entry, first_proof))
            self.rotate(lifecycle)

            raw = self.raw(self.r2, 2, first_entry.entry_digest)
            weak_proof = ThresholdProof(
                authority_id(self.r2),
                2,
                tuple(sign_publication(raw, k) for k in self.k2[:2]),
            )
            weak_entry = RegistryEntry(
                **raw.unsigned, signature=weak_proof.proof_digest
            )
            with self.assertRaises(InvalidSignatureSet):
                registry.observe(ThresholdEnvelope(weak_entry, weak_proof))

    def test_rotation_and_publication_share_one_serialization_boundary(self):
        # Every run must have exactly one legal serialization:
        # publication(root1) -> rotation, or rotation -> stale publication reject.
        for i in range(20):
            with self.subTest(i=i), tempfile.TemporaryDirectory() as td:
                lifecycle, registry = self.stack(td)
                raw = self.raw(self.r1)
                proof = ThresholdProof(
                    authority_id(self.r1),
                    1,
                    tuple(sign_publication(raw, k) for k in self.k1[:2]),
                )
                from experiments.sink_registry_binding.protocol import RegistryEntry
                entry = RegistryEntry(**raw.unsigned, signature=proof.proof_digest)
                envelope = ThresholdEnvelope(entry, proof)
                gate = threading.Barrier(3)
                results = []
                lock = threading.Lock()

                def publish():
                    gate.wait()
                    try:
                        registry.observe(envelope)
                        value = "published"
                    except AuthorityMismatch:
                        value = "stale"
                    with lock:
                        results.append(value)

                def rotate():
                    gate.wait()
                    self.rotate(lifecycle)
                    with lock:
                        results.append("rotated")

                a = threading.Thread(target=publish)
                b = threading.Thread(target=rotate)
                a.start(); b.start(); gate.wait(); a.join(5); b.join(5)
                self.assertFalse(a.is_alive() or b.is_alive())
                self.assertIn("rotated", results)
                self.assertEqual(
                    sum(x in {"published", "stale"} for x in results), 1
                )
                self.assertTrue(registry.verify_durable())


if __name__ == "__main__":
    unittest.main()
