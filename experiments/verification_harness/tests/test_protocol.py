import unittest

from experiments.verification_harness.protocol import Claim, Evidence, Task, Verifier


class VerificationHarnessTests(unittest.TestCase):
    def setUp(self):
        self.task = Task("sha:new", ("impl", "tests"))
        self.verifier = Verifier()

    def good_evidence(self):
        return [
            Evidence("diff", "artifact", "sha:new", True, "pass", ("impl",)),
            Evidence("test", "test", "sha:new", True, "pass", ("tests",)),
        ]

    def verdict(self, evidence, claim=None):
        claim = claim or Claim("claim", self.task.requirements, tuple(e.evidence_id for e in evidence))
        return self.verifier.verify(self.task, claim, evidence)

    def test_correct_trajectory_is_accepted(self):
        self.assertTrue(self.verdict(self.good_evidence()).accepted)

    def test_test_never_executed_is_rejected(self):
        evidence = self.good_evidence()
        evidence[1] = Evidence("test", "test", "sha:new", False, "pass", ("tests",))
        self.assertFalse(self.verdict(evidence).accepted)

    def test_failing_observed_test_is_rejected(self):
        evidence = self.good_evidence()
        evidence[1] = Evidence("test", "test", "sha:new", True, "fail", ("tests",))
        self.assertFalse(self.verdict(evidence).accepted)

    def test_stale_test_evidence_is_rejected(self):
        evidence = self.good_evidence()
        evidence[1] = Evidence("test", "test", "sha:old", True, "pass", ("tests",))
        self.assertFalse(self.verdict(evidence).accepted)

    def test_partial_completion_is_rejected(self):
        evidence = self.good_evidence()
        claim = Claim("claim", ("impl",), tuple(e.evidence_id for e in evidence))
        self.assertFalse(self.verdict(evidence, claim).accepted)

    def test_fabricated_reference_is_rejected(self):
        evidence = self.good_evidence()
        claim = Claim("claim", self.task.requirements, ("diff", "ghost"))
        self.assertFalse(self.verdict(evidence, claim).accepted)

    def test_mutation_invalidates_formerly_valid_trajectory(self):
        old_task = Task("sha:old", self.task.requirements)
        evidence = [
            Evidence("diff", "artifact", "sha:old", True, "pass", ("impl",)),
            Evidence("test", "test", "sha:old", True, "pass", ("tests",)),
        ]
        claim = Claim("claim", old_task.requirements, ("diff", "test"))
        self.assertTrue(self.verifier.verify(old_task, claim, evidence).accepted)
        self.assertFalse(self.verifier.verify(self.task, claim, evidence).accepted)


if __name__ == "__main__":
    unittest.main()
