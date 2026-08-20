# CT v2 Policy + Trust Bundle Prototype

A signed bundle manifest binds the exact policy digest and exact CT trust digest under one release identity/version/generation. SQLite activates manifest, policy, trust and the active pointer in one transaction.

```bash
python -m unittest discover -s experiments/ctv2_policy_trust_bundle/tests -p 'test_protocol.py' -v
python -m unittest experiments.ctv2_policy_trust_bundle.tests.unsafe_mix_and_match_expected_failure -v
```

The unsafe test is expected to fail because independently advanced histories accept policy release 2 with trust release 1.

This is a reference correctness protocol, not a general configuration service or production key-management system.
