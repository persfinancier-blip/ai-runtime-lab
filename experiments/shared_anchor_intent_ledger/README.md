# LAB-080 — shared monotonic-anchor intent ledger

A signed monotonic position is not enough to explain *why* the anchor advanced. This experiment records a canonical intent before each increment and binds the LAB-036 request ID to the exact position, intent ID, component, intent type, and payload digest.

A component may accept an observed anchor position above its own watermark only after every intervening position is present as a contiguous CONFIRMED ledger entry and each entry is freshly reauthenticated through the provider's exact request reconciliation surface. The verified ledger slice is re-read under a SQL write lock before the component watermark advances.

Only one PREPARED intent is allowed at a time in this reference model. That keeps provider ordering deterministic; increasing concurrency is a separate optimization problem.

This is shared-anchor verification and rollback detection, not distributed consensus, a general event bus, provider availability, or a remote transparency service.

Run:

```bash
python -m unittest experiments.shared_anchor_intent_ledger.tests.test_protocol -v
```

Unsafe seed (expected failure):

```bash
python -m unittest experiments.shared_anchor_intent_ledger.tests.unsafe_monotonic_expected_failure -v
```
