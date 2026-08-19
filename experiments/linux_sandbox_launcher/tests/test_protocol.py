import dataclasses
import hashlib
import hmac
import json
import os
import unittest

from experiments.linux_sandbox_launcher.protocol import (
    AttestationError, CapabilityError, CapabilityReport, LinuxSandboxLauncher,
    SandboxRequest, UnsafeIntentOnlyLauncher,
)


class SandboxLauncherTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.caps = CapabilityReport.build(7)

    def req(self, **kw):
        base = dict(task_id="task-1", sandbox_generation=3, credential_generation=5,
                    capability_generation=self.caps.generation,
                    require_userns=self.caps.userns)
        base.update(kw)
        return SandboxRequest(**base)

    def test_real_child_enforcement_and_attestation(self):
        l = LinuxSandboxLauncher(b"k" * 32)
        r = l.launch(self.req(), self.caps)
        l.verify(r, self.req(), self.caps)
        self.assertIn("no_new_privs", r.backends)
        self.assertIn("seccomp-bpf", r.backends)

    def test_fd_default_deny_is_observed_in_child(self):
        l = LinuxSandboxLauncher(b"k" * 32)
        fd = os.open("/dev/null", os.O_RDONLY)
        try:
            os.set_inheritable(fd, True)
            r = l.launch(self.req(), self.caps, inherited_fd=fd)
            l.verify(r, self.req(), self.caps)
        finally:
            os.close(fd)

    def test_required_network_isolation_fails_closed(self):
        if self.caps.network_isolation:
            self.skipTest("runtime unexpectedly supports netns")
        with self.assertRaises(CapabilityError):
            LinuxSandboxLauncher().launch(self.req(require_network_isolation=True), self.caps)

    def test_required_filesystem_isolation_fails_closed(self):
        if self.caps.filesystem_isolation:
            self.skipTest("runtime unexpectedly supports mountns")
        with self.assertRaises(CapabilityError):
            LinuxSandboxLauncher().launch(self.req(require_filesystem_isolation=True), self.caps)

    def test_stale_capability_generation_rejected(self):
        with self.assertRaises(CapabilityError):
            LinuxSandboxLauncher().launch(self.req(capability_generation=6), self.caps)

    def test_forged_receipt_rejected(self):
        l = LinuxSandboxLauncher(b"k" * 32)
        r = l.launch(self.req(), self.caps)
        forged = dataclasses.replace(r, signature="0" * 64)
        with self.assertRaises(AttestationError):
            l.verify(forged, self.req(), self.caps)

    def test_backend_omission_rejected_even_with_valid_signature_shape(self):
        l = LinuxSandboxLauncher(b"k" * 32)
        r = l.launch(self.req(), self.caps)
        forged = dataclasses.replace(r, backends=tuple(x for x in r.backends if x != "seccomp-bpf"))
        with self.assertRaises(AttestationError):
            l.verify(forged, self.req(), self.caps)

    def test_properly_signed_backend_omission_still_rejected(self):
        key = b"k" * 32
        l = LinuxSandboxLauncher(key)
        req = self.req()
        r = l.launch(req, self.caps)
        changed = dataclasses.replace(r, backends=tuple(x for x in r.backends if x != "seccomp-bpf"), signature="")
        fields = dataclasses.asdict(changed)
        fields.pop("signature")
        sig = hmac.new(key, json.dumps(fields, sort_keys=True, separators=(",", ":")).encode(), hashlib.sha256).hexdigest()
        changed = dataclasses.replace(changed, signature=sig)
        with self.assertRaises(AttestationError):
            l.verify(changed, req, self.caps)

    def test_properly_signed_false_observation_still_rejected(self):
        key = b"k" * 32
        l = LinuxSandboxLauncher(key)
        req = self.req()
        r = l.launch(req, self.caps)
        changed = dataclasses.replace(r, observed_seccomp=False, signature="")
        fields = dataclasses.asdict(changed)
        fields.pop("signature")
        sig = hmac.new(key, json.dumps(fields, sort_keys=True, separators=(",", ":")).encode(), hashlib.sha256).hexdigest()
        changed = dataclasses.replace(changed, signature=sig)
        with self.assertRaises(AttestationError):
            l.verify(changed, req, self.caps)

    def test_generation_drift_rejected(self):
        l = LinuxSandboxLauncher(b"k" * 32)
        req = self.req()
        r = l.launch(req, self.caps)
        changed = dataclasses.replace(req, sandbox_generation=req.sandbox_generation + 1)
        with self.assertRaises(AttestationError):
            l.verify(r, changed, self.caps)

    def test_unsafe_intent_only_is_not_post_launch_evidence(self):
        claim = UnsafeIntentOnlyLauncher().launch(self.req(), self.caps)
        self.assertTrue(claim["claimed_enforced"])
        self.assertFalse(claim["observed_child"])


if __name__ == "__main__":
    unittest.main()
