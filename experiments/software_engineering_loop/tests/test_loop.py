import unittest

from experiments.software_engineering_loop.loop import EngineeringLoop, Failure, Phase, Route, Task, failure_taxonomy


PREFERRED = Route("preferred-test", True, True, 100)
FALLBACK = Route("safe-fallback", True, True, 50)
UNSAFE = Route("unsafe-fast", True, False, 1000)


class LoopTests(unittest.TestCase):
    def setUp(self):
        self.loop = EngineeringLoop()

    def task(self, name="t"):
        return Task(name, ("primary", "secondary"))

    def test_happy_path_accepts(self):
        t = self.task()
        self.loop.reproduce(t, observed=True)
        self.loop.patch(t, satisfies=("primary", "secondary"))
        self.loop.validate(t, routes=[PREFERRED], passed=True)
        self.loop.audit(t, regression_found=False)
        self.assertTrue(self.loop.decide(t))
        self.assertEqual(t.phase, Phase.COMPLETE)

    def test_patch_without_reproduction_rejects(self):
        t = self.task()
        self.loop.reproduce(t, observed=False)
        self.loop.patch(t, satisfies=("primary", "secondary"))
        self.assertFalse(self.loop.decide(t))
        self.assertIn(Failure.UNREPRODUCED, t.failures)

    def test_partial_fix_rejects_false_success(self):
        t = self.task()
        self.loop.reproduce(t, observed=True)
        self.loop.patch(t, satisfies=("primary",))
        self.loop.validate(t, routes=[PREFERRED], passed=True)
        self.assertFalse(self.loop.decide(t))
        self.assertIn(Failure.PARTIAL_FIX, t.failures)

    def test_stale_test_evidence_rejected(self):
        t = self.task()
        self.loop.reproduce(t, observed=True)
        self.loop.patch(t, satisfies=("primary", "secondary"))
        old_version = t.artifact_version - 1
        self.loop.validate(t, routes=[PREFERRED], passed=True, evidence_version=old_version)
        self.assertFalse(self.loop.decide(t))
        self.assertIn(Failure.STALE_EVIDENCE, t.failures)

    def test_audit_regression_returns_to_patch(self):
        t = self.task()
        self.loop.reproduce(t, observed=True)
        self.loop.patch(t, satisfies=("primary", "secondary"))
        self.loop.validate(t, routes=[PREFERRED], passed=True)
        self.loop.audit(t, regression_found=True)
        self.assertFalse(self.loop.decide(t))
        self.assertIn(Failure.AUDIT_REGRESSION, t.failures)
        self.assertEqual(t.phase, Phase.PATCHED)

    def test_safe_fallback_selected_when_preferred_unavailable(self):
        unavailable = Route("preferred-test", False, True, 100)
        t = self.task()
        self.loop.reproduce(t, observed=True)
        self.loop.patch(t, satisfies=("primary", "secondary"))
        self.loop.validate(t, routes=[unavailable, FALLBACK, UNSAFE], passed=True)
        self.assertEqual(t.selected_route, "safe-fallback")
        self.loop.audit(t, regression_found=False)
        self.assertTrue(self.loop.decide(t))

    def test_no_safe_validation_route_blocks(self):
        unavailable = Route("preferred-test", False, True, 100)
        t = self.task()
        self.loop.reproduce(t, observed=True)
        self.loop.patch(t, satisfies=("primary", "secondary"))
        self.loop.validate(t, routes=[unavailable, UNSAFE], passed=True)
        self.assertFalse(self.loop.decide(t))
        self.assertEqual(t.phase, Phase.BLOCKED)
        self.assertIn(Failure.NO_SAFE_ROUTE, t.failures)

    def test_observed_failing_validation_rejected(self):
        t = self.task()
        self.loop.reproduce(t, observed=True)
        self.loop.patch(t, satisfies=("primary", "secondary"))
        self.loop.validate(t, routes=[PREFERRED], passed=False)
        self.assertFalse(self.loop.decide(t))
        self.assertIn(Failure.VALIDATION_FAILED, t.failures)

    def test_failure_taxonomy_stable(self):
        tasks = []
        for failure in [Failure.UNREPRODUCED, Failure.PARTIAL_FIX, Failure.STALE_EVIDENCE, Failure.AUDIT_REGRESSION, Failure.NO_SAFE_ROUTE]:
            t = self.task(failure.value)
            t.failures.append(failure)
            tasks.append(t)
        self.assertEqual(failure_taxonomy(tasks), {
            "unreproduced_bug": 1,
            "partial_fix": 1,
            "stale_evidence": 1,
            "audit_regression": 1,
            "no_safe_validation_route": 1,
        })


if __name__ == "__main__":
    unittest.main()
