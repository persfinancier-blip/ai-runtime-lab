# Credential Scope and Redirect Leakage Conformance

Deterministic standard-library prototype for LAB-025.

The harness keeps five identities separate:

1. **origin credential** — scoped to scheme/host/port plus optional path and request identity;
2. **cookie/session material** — host/path/secure scope with generation tracking;
3. **proxy credential** — scoped to one proxy identity and proxy generation;
4. **transport route identity** — inherited as `route_fingerprint` from LAB-024-style transport binding;
5. **effect identity** — stable `effect_id`, payload digest, purpose and request generation.

The core rule is: credentials are selected again for the current authority and route; they are never copied forward merely because a prior request had them.

Run corrected tests:

```bash
python -m unittest discover -s experiments/credential_scope/tests -p 'test_*.py' -v
```

Run the deliberately unsafe baseline separately (expected failure):

```bash
python -m unittest experiments.credential_scope.tests.unsafe_seed_expected_failure -v
```

Non-goals: full browser cookie semantics, OAuth server, secret manager, real HTTP stack, real proxy implementation.
