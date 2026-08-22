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
from experiments.transactional_broker_journal.protocol import TransactionalJournal


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
        return path, lifecycle, registry, root, r1keys, recovery

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

    def test_published_row_missing_historical_binding_fails_closed_even_before_rotation(self):
        with tempfile.TemporaryDirectory() as td:
            path, lifecycle, registry, root, r1keys, _ = self.stack(td)
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

    def test_standalone_durable_verification_excludes_concurrent_rotation_commit(self):
        with tempfile.TemporaryDirectory() as td:
            _, lifecycle, _, root, r1keys, _ = self.stack(td)
            r2keys, r2map = keys("r2")
            r2 = RootState("sink-registry", 2, 1, 2, r2map)
            payload = rotation_payload(root, r2)

            guard = lifecycle._con()
            guard.execute("BEGIN IMMEDIATE")
            finished = threading.Event()
            errors = []

            def rotate():
                try:
                    lifecycle.rotate(r2, sigs(r1keys, payload), sigs(r2keys, payload))
                except Exception as exc:
                    errors.append(exc)
                finally:
                    finished.set()

            thread = threading.Thread(target=rotate)
            thread.start()
            time.sleep(0.05)
            self.assertFalse(finished.is_set())
            # A consistent verifier must be able to inspect the pre-rotation state
            # while the competing writer is fenced by the same SQLite boundary.
            from experiments.sink_registry_authority_lifecycle import protocol as raw
            self.assertTrue(raw.DurableRegistryAuthority.verify_durable(lifecycle))
            guard.commit()
            guard.close()
            thread.join(2)
            self.assertTrue(finished.is_set())
            self.assertFalse(errors)
            self.assertEqual(lifecycle.current().version, 2)


if __name__ == "__main__":
    unittest.main()
