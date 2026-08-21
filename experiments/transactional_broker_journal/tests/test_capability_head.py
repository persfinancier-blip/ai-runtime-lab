import tempfile
import unittest
from pathlib import Path

from experiments.sink_capability_contract import protocol as cap
from experiments.transactional_broker_journal.capability import CapabilityBoundJournal
from experiments.transactional_broker_journal.protocol import Request, TransactionalJournal


class CapabilityHeadTests(unittest.TestCase):
    def authority(self):
        return cap.ProbeAuthority(issuer_id="probe", key=b"probe-key", generation=1)

    def capability(self, authority, *, generation, retention=100):
        claim = cap.CapabilityClaim(
            sink_id="sink-A",
            generation=generation,
            mutating=True,
            stable_idempotency_key=True,
            request_bound_key=True,
            reconcile_by_key=True,
            retention_seconds=retention,
            source="behavioral-test-probe",
        )
        probe_sink = cap.SimulatedSink(
            idempotent=True,
            request_bound=True,
            reconcile=True,
        )
        return cap.VerifiedCapability(claim, authority.attest(claim, probe_sink))

    def test_once_newer_generation_observed_old_generation_is_stale(self):
        with tempfile.TemporaryDirectory() as td:
            authority = self.authority()
            bound = CapabilityBoundJournal(
                TransactionalJournal(Path(td) / "journal.db", 1), authority
            )
            bound.observe_capability(self.capability(authority, generation=2))
            with self.assertRaises(cap.StaleCapability):
                bound.reserve(
                    Request("old", "task", "scope", 1, "payload"),
                    self.capability(authority, generation=1),
                    now=1,
                )

    def test_capability_head_survives_restart(self):
        with tempfile.TemporaryDirectory() as td:
            authority = self.authority()
            path = Path(td) / "journal.db"
            first = CapabilityBoundJournal(TransactionalJournal(path, 1), authority)
            first.observe_capability(self.capability(authority, generation=2))
            reopened = CapabilityBoundJournal(TransactionalJournal(path, 1), authority)
            with self.assertRaises(cap.StaleCapability):
                reopened.observe_capability(self.capability(authority, generation=1))
            self.assertTrue(reopened.verify_durable())

    def test_same_generation_claim_substitution_rejected_at_head(self):
        with tempfile.TemporaryDirectory() as td:
            authority = self.authority()
            bound = CapabilityBoundJournal(
                TransactionalJournal(Path(td) / "journal.db", 1), authority
            )
            bound.observe_capability(self.capability(authority, generation=1, retention=10))
            with self.assertRaises(cap.StaleCapability):
                bound.observe_capability(
                    self.capability(authority, generation=1, retention=1000)
                )


if __name__ == "__main__":
    unittest.main()
