import unittest
from experiments.linux_sandbox_launcher.protocol import CapabilityReport, SandboxRequest, UnsafeIntentOnlyLauncher


class UnsafeSeed(unittest.TestCase):
    def test_parent_intent_is_not_enforcement(self):
        caps = CapabilityReport.build(1)
        req = SandboxRequest("t", 1, 1, 1, require_userns=False)
        result = UnsafeIntentOnlyLauncher().launch(req, caps)
        self.assertTrue(result["observed_child"], "unsafe launcher claimed success without post-launch evidence")


if __name__ == "__main__":
    unittest.main()
