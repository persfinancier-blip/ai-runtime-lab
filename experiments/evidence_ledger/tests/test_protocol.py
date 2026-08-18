import tempfile, unittest
from pathlib import Path
from experiments.evidence_ledger.protocol import Ledger, Observation, TamperError, Verifier

class EvidenceLedgerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.path = Path(self.temp.name) / "ledger.jsonl"; self.ledger = Ledger(self.path)
    def tearDown(self): self.temp.cleanup()
    def observation(self, artifact="artifact-a", trusted=True, result="PASS"):
        return Observation("test", artifact, "independent-verifier", trusted, result)
    def test_restart_reload(self):
        evidence = self.ledger.observe(self.observation()); self.assertEqual(Ledger(self.path).resolve(evidence)[0]["result"], "PASS")
    def test_duplicate_is_idempotent(self):
        observation = self.observation(); self.assertEqual(self.ledger.observe(observation), self.ledger.observe(observation)); self.assertEqual(len(self.ledger.records), 1)
    def test_tamper_is_detected(self):
        self.ledger.observe(self.observation()); self.path.write_text(self.path.read_text().replace("PASS", "FAIL"))
        with self.assertRaises(TamperError): Ledger(self.path)
    def test_stale_artifact_is_rejected(self):
        evidence = self.ledger.observe(self.observation("old")); self.assertFalse(Verifier(self.ledger).verify("new", [evidence]))
    def test_dangling_reference_is_rejected(self): self.assertFalse(Verifier(self.ledger).verify("artifact-a", ["missing"]))
    def test_invalidation_is_append_only_and_rejected(self):
        evidence = self.ledger.observe(self.observation()); self.ledger.invalidate(evidence, "observer compromised"); self.assertFalse(Verifier(self.ledger).verify("artifact-a", [evidence]))
    def test_superseded_evidence_is_rejected(self):
        old = self.ledger.observe(self.observation()); new = self.ledger.observe(self.observation(result="FAIL")); self.ledger.supersede(old, new); self.assertFalse(Verifier(self.ledger).verify("artifact-a", [old]))
    def test_worker_assertion_is_not_independent_evidence(self):
        evidence = self.ledger.observe(self.observation(trusted=False)); self.assertFalse(Verifier(self.ledger).verify("artifact-a", [evidence]))
    def test_valid_current_observation_is_accepted(self):
        evidence = self.ledger.observe(self.observation()); self.assertTrue(Verifier(self.ledger).verify("artifact-a", [evidence]))
