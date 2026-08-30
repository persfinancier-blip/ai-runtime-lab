# LAB-090 — historical activation retry state-poisoning audit

Date: 2026-08-30

## Finding

The LAB-090 retry path for an existing `provider_generation_activations` row reconciled/released the ticket, then assigned `self.attested = new_attested`, and only afterwards called `_require_runtime_matches_durable_head()`.

That ordering is valid only when the existing activation belongs to the durable current generation. Once a later provider generation has become current, an activation row for an older generation remains as durable history. A caller could therefore submit that historical generation and a matching historical runtime. The final current-head check would reject it, but the live ledger object had already been mutated to the stale runtime.

This is fail-closed with respect to authority, but not state-safe. Subsequent operations can observe the poisoned runtime; in particular, a reserve path can create a durable PREPARED intent before a later effect path rejects the stale runtime, producing avoidable persistent availability failure.

## Fix

Draft PR #175 now checks the durable current provider generation before any existing-activation reconciliation or runtime mutation:

```python
durable = self.provider_history.current()
if new.generation_id != durable.generation_id:
    raise InvalidTransition("activation retry is not durable current generation")
```

Published implementation commit: `3eb49db6f732d21da34a8b783dd603a62aa38a41`.

Regression added in commit `50e85e2eaa37fc0787cde48721363e46578c3051`: `test_activation_historical_retry.py` performs G1→G2→G3, then retries historical G2 and requires failure before `ledger.attested` leaves G3.

## Validation actually executed

Direct git clone of the PR branch was attempted in this run and failed before repository-code execution with:

`Could not resolve host: github.com`

A narrow local reconstruction of the provider activation primitive and its focused test surface was executed and produced 8/8 PASS. That reconstruction was semantically equivalent but was not byte-verified against the published Git blobs, so it is evidence for the mechanism only and is **not** claimed as an exact-head branch gate.

The new historical-retry regression itself was not executed in this runtime. PR #175 therefore remains draft.

## Audit boundary

The fix does not change provider authority, transition proof semantics, activation ticket contents, fencing order, or durable SQL schema. It only prevents a historical existing-activation row from entering the retry/reconciliation path and mutating the live runtime.

## Next action

1. LAB-086 remains priority #1 if a byte-preserving publication path becomes available.
2. Otherwise execute exact-head PR #175 focused/integration/downstream tests, including the new historical retry regression.
3. If executable transport remains unavailable, continue only narrow restart/concurrency audits; do not merge based on source inspection alone.
