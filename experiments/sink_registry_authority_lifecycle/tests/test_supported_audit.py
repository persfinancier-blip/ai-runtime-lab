import json
import sqlite3
import tempfile
import threading
import time
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
from experiments.sink_registry_authority_lifecycle.supported import (
    DurableRegistryAuthority,
    LifecycleRegistryBoundJournal,
    RegistryEntry,
)
from experiments.transactional_broker_journal.capability import CapabilityBoundJournal
from experiments.transactional_broker_journal.protocol import Request, TransactionalJournal


def keys(prefix, n=3):
    raw = [f"{prefix}-{i}".encode() for i in range(n)]
    return raw, {key_id(k): k.hex() for k in raw}


def sigs(raw, payload, n=2):
    return tuple(Signature(key_id(k), sign(k, payload)) for k in raw[:n])


class SupportedAuditTests(unittest.TestCase):
    def stack(self, td):
        path = Path(td) / "journal.db"
        probe = cap.ProbeAuthority(issuer_id="probe", key=b"probe", generation=1)
        journal = TransactionalJournal(path, 1)
        bound = CapabilityBoundJournal(journal, probe)
        r1keys, r1map = keys("r1")
        reckeys, recmap = keys("recovery", 4)
        root = RootState("sink-registry", 1, 1, 2, r1map)
        recovery = RecoveryAuthority(1, 3, recmap)
        lifecycle = DurableRegistryAuthority(path, root, recovery)
        registry = LifecycleRegistryBoundJournal(bound, lifecycle)
        return path, probe, lifecycle, registry, root, r1keys, recovery

    def signed_entry(self, lifecycle, root, signer):
        raw = RegistryEntry(
            "sink-A",
            1,
            "a" * 64,
            "https://sink.example",
            "charge-v1",
            None,
            key_id(signer),
            root.version,
        )
        return lifecycle.issue(raw, signer)

    def capability(self, probe):
        claim = cap.CapabilityClaim(
            sink_id="sink-A",
            generation=1,
            mutating=True,
            stable_idempotency_key=True,
            request_bound_key=True,
            reconcile_by_key=True,
            retention_seconds=100,
            source="lab076-supported-audit",
        )
        sink = cap.SimulatedSink(idempotent=True, request_bound=True, reconcile=True)
        return cap.VerifiedCapability(claim, probe.attest(claim, sink))

    def test_supported_reserve_can_atomically_publish_first_entry(self):
        with tempfile.TemporaryDirectory() as td:
            _, probe, lifecycle, registry, root, r1keys, _ = self.stack(td)
            entry = self.signed_entry(lifecycle, root, r1keys[0])
            request = Request("r", "task", "scope", 1, "payload")
            status, _, plan, _ = registry.reserve(
                request, self.capability(probe), entry, now=0
            )
            self.assertEqual(status, "INTENT")
            self.assertEqual(plan.entry_digest, entry.entry_digest)
            self.assertEqual(registry.head("sink-A"), entry)

    def test_published_row_missing_historical_binding_fails_closed_even_before_rotation(self):
        with tempfile.TemporaryDirectory() as td:
            path, _, lifecycle, registry, root, r1keys, _ = self.stack(td)
            entry = self.signed_entry(lifecycle, root, r1keys[0])
            registry.observe(entry)
            q = sqlite3.connect(path)
            q.execute(
                "DELETE FROM registry_authorized_entries WHERE entry_digest=?",
                (entry.entry_digest,),
            )
            q.commit()
            q.close()
            with self.assertRaises(Exception):
                registry.head("sink-A")

    def test_supported_durable_verifier_fences_concurrent_rotation_commit(self):
        with tempfile.TemporaryDirectory() as td:
            _, _, lifecycle, _, root, r1keys, _ = self.stack(td)
            r2keys, r2map = keys("r2")
            r2 = RootState("sink-registry", 2, 1, 2, r2map)
            payload = rotation_payload(root, r2)

            from experiments.sink_registry_authority_lifecycle import protocol as raw

            original = raw.DurableRegistryAuthority.verify_durable
            entered = threading.Event()
            release = threading.Event()
            audit_finished = threading.Event()
            rotation_finished = threading.Event()
            errors = []

            def slow_raw_verify(self, *args, **kwargs):
                entered.set()
                if not release.wait(2):
                    raise RuntimeError("test verifier release timeout")
                return original(self, *args, **kwargs)

            def audit():
                try:
                    lifecycle.verify_durable()
                except Exception as exc:
                    errors.append(exc)
                finally:
                    audit_finished.set()

            def rotate():
                try:
                    lifecycle.rotate(r2, sigs(r1keys, payload), sigs(r2keys, payload))
                except Exception as exc:
                    errors.append(exc)
                finally:
                    rotation_finished.set()

            raw.DurableRegistryAuthority.verify_durable = slow_raw_verify
            try:
                audit_thread = threading.Thread(target=audit)
                audit_thread.start()
                self.assertTrue(entered.wait(1))

                rotation_thread = threading.Thread(target=rotate)
                rotation_thread.start()
                time.sleep(0.05)
                self.assertFalse(rotation_finished.is_set())

                release.set()
                audit_thread.join(2)
                rotation_thread.join(2)
                self.assertTrue(audit_finished.is_set())
                self.assertTrue(rotation_finished.is_set())
                self.assertFalse(errors)
                self.assertEqual(lifecycle.current().version, 2)
            finally:
                raw.DurableRegistryAuthority.verify_durable = original
                release.set()


if __name__ == "__main__":
    unittest.main()
