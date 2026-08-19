import unittest

from experiments.kernel_sandbox_adapter.protocol import (
    CapabilityReport, Enforcement, GenerationDrift, Mechanism, Requirement,
    SandboxAdapter, SandboxRequest, SandboxUnavailable, StaleCapabilityReport, UnsafeAdapter,
)


def report(*mechanisms, generation=1, observed_at=100.0, ttl=30.0):
    return CapabilityReport("linux", "test", generation, observed_at, ttl, tuple(mechanisms))


def mech(name, dimension, available=True, observed=True, enforcement=Enforcement.KERNEL):
    return Mechanism(name, dimension, enforcement, available, observed)


class SandboxAdapterTests(unittest.TestCase):
    def setUp(self):
        self.adapter = SandboxAdapter()
        self.req = SandboxRequest("task", 3, 7, {"filesystem": Requirement.REQUIRED})

    def test_required_dimension_binds_only_observed_backend(self):
        r = report(mech("landlock", "filesystem"))
        p = self.adapter.plan(self.req, r, now=110)
        self.assertEqual(p.bindings[0].mechanism, "landlock")

    def test_required_dimension_fails_closed_when_unavailable(self):
        r = report(mech("landlock", "filesystem", available=False))
        with self.assertRaises(SandboxUnavailable):
            self.adapter.plan(self.req, r, now=110)

    def test_declared_but_unobserved_is_not_enforcement(self):
        r = report(mech("landlock", "filesystem", observed=False))
        with self.assertRaises(SandboxUnavailable):
            self.adapter.plan(self.req, r, now=110)

    def test_audit_only_requires_explicit_non_security_critical(self):
        req = SandboxRequest("task", 3, 7, {"network": Requirement.AUDIT}, non_security_critical=True)
        p = self.adapter.plan(req, report(), now=110)
        self.assertEqual(p.bindings[0].enforcement, Enforcement.POLICY_ONLY)
        req2 = SandboxRequest("task", 3, 7, {"network": Requirement.AUDIT}, non_security_critical=False)
        with self.assertRaises(SandboxUnavailable):
            self.adapter.plan(req2, report(), now=110)

    def test_stale_report_rejected(self):
        with self.assertRaises(StaleCapabilityReport):
            self.adapter.plan(self.req, report(mech("landlock", "filesystem")), now=131)

    def test_partial_enforcement_rejected(self):
        req = SandboxRequest("task", 3, 7, {"filesystem": Requirement.REQUIRED, "network": Requirement.REQUIRED})
        with self.assertRaises(SandboxUnavailable):
            self.adapter.plan(req, report(mech("landlock", "filesystem")), now=110)

    def test_generation_drift_rejected_at_launch(self):
        r = report(mech("landlock", "filesystem"))
        p = self.adapter.plan(self.req, r, now=110)
        r2 = report(mech("landlock", "filesystem"), generation=2)
        with self.assertRaises(GenerationDrift):
            self.adapter.validate_launch(p, r2, sandbox_generation=3, credential_generation=7, now=110)

    def test_sandbox_generation_drift_rejected(self):
        r = report(mech("landlock", "filesystem"))
        p = self.adapter.plan(self.req, r, now=110)
        with self.assertRaises(GenerationDrift):
            self.adapter.validate_launch(p, r, sandbox_generation=4, credential_generation=7, now=110)

    def test_credential_generation_drift_rejected(self):
        r = report(mech("landlock", "filesystem"))
        p = self.adapter.plan(self.req, r, now=110)
        with self.assertRaises(GenerationDrift):
            self.adapter.validate_launch(p, r, sandbox_generation=3, credential_generation=8, now=110)

    def test_kernel_preferred_over_process_mechanism(self):
        r = report(mech("userspace", "filesystem", enforcement=Enforcement.PROCESS), mech("landlock", "filesystem"))
        p = self.adapter.plan(self.req, r, now=110)
        self.assertEqual(p.bindings[0].mechanism, "landlock")

    def test_unsafe_adapter_false_success_is_exposed(self):
        r = report(mech("landlock", "filesystem", available=False, observed=True))
        unsafe = UnsafeAdapter().plan(self.req, r)
        self.assertEqual(unsafe.bindings[0].enforcement, Enforcement.KERNEL)
        with self.assertRaises(SandboxUnavailable):
            self.adapter.plan(self.req, r, now=110)

    def test_forged_kernel_binding_rejected_at_launch(self):
        from experiments.kernel_sandbox_adapter.protocol import BoundDimension, SandboxPlan
        r = report(mech("landlock", "filesystem", available=False))
        forged = SandboxPlan("task", 3, 7, r.generation, r.digest(), False, (
            BoundDimension("filesystem", Requirement.REQUIRED, "landlock", Enforcement.KERNEL),
        ))
        with self.assertRaises(SandboxUnavailable):
            self.adapter.validate_launch(forged, r, sandbox_generation=3, credential_generation=7, now=110)

    def test_forged_policy_only_for_required_dimension_rejected(self):
        from experiments.kernel_sandbox_adapter.protocol import BoundDimension, SandboxPlan
        r = report()
        forged = SandboxPlan("task", 3, 7, r.generation, r.digest(), True, (
            BoundDimension("filesystem", Requirement.REQUIRED, "policy-audit-only", Enforcement.POLICY_ONLY),
        ))
        with self.assertRaises(SandboxUnavailable):
            self.adapter.validate_launch(forged, r, sandbox_generation=3, credential_generation=7, now=110)


if __name__ == "__main__":
    unittest.main()
