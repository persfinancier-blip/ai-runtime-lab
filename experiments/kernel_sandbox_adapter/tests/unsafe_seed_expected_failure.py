import unittest
from experiments.kernel_sandbox_adapter.protocol import CapabilityReport, Enforcement, Mechanism, Requirement, SandboxRequest, UnsafeAdapter


class UnsafeAdapterExpectedFailure(unittest.TestCase):
    def test_unavailable_backend_must_not_be_reported_enforced(self):
        report = CapabilityReport("linux", "test", 1, 100, 30, (
            Mechanism("landlock", "filesystem", Enforcement.KERNEL, False, True, "ENOSYS"),
        ))
        request = SandboxRequest("task", 1, 1, {"filesystem": Requirement.REQUIRED})
        plan = UnsafeAdapter().plan(request, report)
        self.assertNotEqual(plan.bindings[0].enforcement, Enforcement.KERNEL, "unsafe adapter falsely claimed kernel enforcement")


if __name__ == "__main__": unittest.main()
