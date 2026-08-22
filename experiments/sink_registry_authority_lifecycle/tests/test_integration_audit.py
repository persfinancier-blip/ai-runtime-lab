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
from experiments.sink_registry_authority_lifecycle.integration import LifecycleRegistryBoundJournal
from experiments.sink_registry_authority_lifecycle.protocol import DurableRegistryAuthority, EntryAuthError
from experiments.sink_registry_binding.supported import RegistryEntry
from experiments.transactional_broker_journal.capability import CapabilityBoundJournal
from experiments.transactional_broker_journal.protocol import TransactionalJournal


def keys(prefix, n=3):
    raw = [f"{prefix}-{i}".encode() for i in range(n)]
    return raw, {key_id(k): k.hex() for k in raw}


def sigs(raw, payload, n=2):
    return tuple(Signature(key_id(k), sign(k, payload)) for k in raw[:n])


class IntegrationAuditTests(unittest.TestCase):
    def test_pre_authorized_but_unpublished_old_entry_cannot_publish_after_rotation(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "journal.db"
            probe = cap.ProbeAuthority(issuer_id="probe", key=b"probe", generation=1)
            journal = TransactionalJournal(path, 1)
            bound = CapabilityBoundJournal(journal, probe)
            r1keys, r1map = keys("r1")
            r2keys, r2map = keys("r2")
            reckeys, recmap = keys("recovery", 4)
            r1 = RootState("sink-registry", 1, 1, 2, r1map)
            r2 = RootState("sink-registry", 2, 1, 2, r2map)
            recovery = RecoveryAuthority(1, 3, recmap)
            lifecycle = DurableRegistryAuthority(path, r1, recovery)
            registry = LifecycleRegistryBoundJournal(bound, lifecycle)

            raw = RegistryEntry(
                "sink-A",
                1,
                "a" * 64,
                "https://sink.example",
                "charge-v1",
                None,
                key_id(r1keys[0]),
                1,
            )
            candidate = lifecycle.issue(raw, r1keys[0])
            # Deliberately bind it in the lifecycle table without publishing it
            # into the LAB-075 registry. This must not become a future authority.
            lifecycle.accept_entry(candidate)

            payload = rotation_payload(r1, r2)
            lifecycle.rotate(r2, sigs(r1keys, payload), sigs(r2keys, payload))
            with self.assertRaises(EntryAuthError):
                registry.observe(candidate)

            q = journal._con()
            try:
                self.assertIsNone(
                    q.execute(
                        "SELECT entry_digest FROM sink_registry_heads WHERE sink_id='sink-A'"
                    ).fetchone()
                )
            finally:
                q.close()


if __name__ == "__main__":
    unittest.main()
