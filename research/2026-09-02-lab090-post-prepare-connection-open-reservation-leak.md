# LAB-090 — post-prepare SQLite connection-open failure can strand provider reservation

Date: 2026-09-02
Scope: draft PR #175, head observed `d9a381dd4607a928cd1315adef6431e239995bc1`

## Finding

`SupportedHistoricalSharedAnchorLedger.rotate_provider()` successfully calls `provider.prepare_activation(...)`, validates the returned ticket, and verifies `activation_status(ticket) == "PREPARED"`. It then executes:

```python
sql_committed = False
q = self._con()
try:
    q.execute("BEGIN IMMEDIATE")
    ...
except:
    ...
    if not sql_committed:
        provider.abort_activation(ticket)
        raise
finally:
    q.close()
```

The SQLite connection acquisition `q = self._con()` is outside the cleanup `try`. If `_con()` raises after the provider reservation has been installed, control never reaches `provider.abort_activation(ticket)`. The provider therefore remains `PREPARED`/fenced even though no LAB-090 activation row or provider-generation rotation was committed in SQLite.

This is the same authority/cleanup boundary as the existing LAB-090 failed-prepare/ticket-validation reservation issue, so it strengthens #169 rather than creating a new issue.

## Why it matters

The external reservation is the provider-side serialization primitive. Leaving it behind on a local connection-open failure can indefinitely block ordinary provider increments and later rotations. Because no durable coordinator activation row exists, normal restart recovery has no ticket record from which to reconcile or release that reservation.

## Regression-first contract

Add a test ledger whose `_con()` succeeds during construction and the pre-prepare expected-position read, then raises exactly on the first connection acquisition after a valid `PREPARED` ticket has been installed.

Pre-fix assertions:

1. rotation raises the injected connection-open error;
2. provider `activation_state.pending` remains set;
3. durable generation head remains the predecessor;
4. no `provider_generation_activations` row exists for the candidate generation.

Post-fix assertions:

1. the same failure aborts only the exact reservation created by this attempt;
2. provider `activation_state.pending is None` afterward;
3. predecessor durable head and activation table remain unchanged;
4. cleanup must not abort an unrelated pre-existing reservation.

## Design constraint

The cleanup scope must begin immediately after a successful, validated `prepare_activation` that this attempt owns, before any fallible coordinator operation including connection acquisition. Cleanup provenance must distinguish a newly-created reservation from an idempotently returned pre-existing reservation so an error cannot abort someone else's activation.

## Execution status

Direct Git transport was probed in this run and failed before repository execution with `Could not resolve host: github.com`. This note is source/control-flow evidence from the exact PR diff, not a claimed exact-branch behavioral RED/PASS.
