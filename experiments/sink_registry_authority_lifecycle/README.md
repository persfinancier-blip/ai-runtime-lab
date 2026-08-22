# Sink registry authority lifecycle (LAB-076)

This experiment replaces LAB-075's ambient single registry-verifier key with a durable, versioned threshold root lifecycle.

Two verification authorities are intentionally separate:

- **publication authority**: only the current root version can authorize a new registry entry;
- **historical verification authority**: a previously accepted entry is verified against the exact historical root snapshot to which it was durably bound.

Normal root rotation requires both the old-root and new-root thresholds over the same transition. Break-glass recovery uses the separate recovery quorum and advances the authority epoch. Historical roots remain available for verification only; they are never reactivated as current signing authority.

Run:

```bash
python -m unittest experiments.sink_registry_authority_lifecycle.tests.test_protocol -v
```

Unsafe seed (expected failure):

```bash
python -m unittest experiments.sink_registry_authority_lifecycle.tests.unsafe_self_swap_expected_failure -v
```

This is a local trust-lifecycle model, not distributed PKI, consensus, service discovery, transport security, or whole-store rollback protection.
