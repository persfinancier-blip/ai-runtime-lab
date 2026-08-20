# LAB-049 temporal compliance-policy lifecycle

Reference protocol that makes compliance policy itself an authenticated, versioned, time-bounded authority rather than a caller-selected object.

Core rule: for a new decision, derive the policy snapshot from `policy_time`; bind the result to the exact policy digest/version/generation/effective interval and the exact LAB-048 trust snapshot. Historical replay may use that recorded identity only to reproduce the old decision, never to govern a new later decision.

Run corrected tests:

```bash
python -m unittest discover -s experiments/ctv2_temporal_policy_lifecycle/tests -p 'test_protocol.py' -v
```

The unsafe seed is intentionally outside corrected discovery:

```bash
python -m unittest experiments.ctv2_temporal_policy_lifecycle.tests.unsafe_caller_policy_expected_failure
```

Non-goals: this is not Chrome's concrete CT threshold policy, a general policy language, or a metadata-signature implementation. `AuthenticatedPolicyHistory.add_accepted()` is the trust boundary supplied by an upstream authenticator, paralleling LAB-047/048.
