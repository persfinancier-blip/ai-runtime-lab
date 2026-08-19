# Linux sandbox launcher + post-launch attestation

LAB-030 reference prototype. It exercises only mechanisms freshly observed available in the current Linux runtime.

The launcher treats setup intent as insufficient. A child must attest observable enforcement: `NoNewPrivs: 1`, seccomp filter mode, a deterministically denied syscall, user namespace separation when required, and default-deny FD inheritance. The parent then issues an HMAC-bound launch receipt tied to task/sandbox/credential/capability generations and the capability-report digest.

REQUIRED network/filesystem isolation is fail-closed when fresh probes cannot supply it.

Run:

```bash
python -m unittest discover -s experiments/linux_sandbox_launcher/tests -p 'test_*.py' -v
python -m unittest experiments.linux_sandbox_launcher.tests.unsafe_seed_expected_failure
```

The second command is expected to fail: it demonstrates the unsafe parent-intent-only design.
