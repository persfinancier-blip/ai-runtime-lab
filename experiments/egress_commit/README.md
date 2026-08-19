# LAB-022 Commit-time Egress Binding

A deterministic prepare→commit authorization harness. A trusted control-plane authority issues an HMAC-authenticated permit bound to payload digest, canonical HTTPS destination, purpose, policy generation, authorization generation/id, nonce, expiry, and a stable LAB-005-style effect key. The commit executor revalidates all bindings immediately before the external effect and reconciles unknown outcomes by the same effect identity.

Run corrected tests (unsafe seed is intentionally excluded):

```bash
python -m unittest experiments.egress_commit.tests.test_protocol.CommitBindingTests -v
```

Run unsafe seed separately:

```bash
python -m unittest experiments.egress_commit.tests.test_protocol.UnsafeBaselineTests -v
```

The unsafe seed should fail because check-then-use allows a checked trusted destination to be changed to an attacker destination before use.
