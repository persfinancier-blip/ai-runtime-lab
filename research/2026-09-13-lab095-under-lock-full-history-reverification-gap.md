# LAB-095 — under-lock full provider-history reverification gap

Date: 2026-09-13

## Finding

`prepare_database_identity()` currently performs a full `history.verify_durable()` before opening its writer transaction, then calls `history.current()` / `ledger._provider()`. After `BEGIN IMMEDIATE`, it rechecks only a subset of provider-history state: bootstrap generation id, head generation number, and head provider id.

That subset is not equivalent to full provider-history verification. A concurrent or otherwise external writer can corrupt a historical transition proof or current descriptor verification material after the pre-lock `verify_durable()` but before LAB-095 obtains its writer lock while leaving the superficially checked bootstrap/head provider/generation fields unchanged. The current migration code could then reserve logical database identity custody against provider history that would fail `IntegratedProviderHistory._verify_durable_locked()`.

This is the same class of trust-boundary mistake that LAB-095's DB-A/DB-B acceptance criterion is intended to exclude: `_current_locked()` / shallow current-head agreement is not a replacement for complete durable-history continuity verification.

## Required behavior

Immediately after `BEGIN IMMEDIATE`, before CSPRNG nonce generation or any custody/shared-anchor mutation, the supported migration path must execute the full provider-history durable verifier on the same SQLite connection/lock used for the reservation. It must then cross-check the locked verified current descriptor against the pre-lock/runtime provider identity. Any transition/history corruption must roll back with no PREPARED identity row and no shared-anchor tail advance.

Do not replace this with another set of hand-maintained shallow column checks; reuse the existing integrated durable-history verifier so LAB-095 cannot drift from LAB-081/LAB-090 verification semantics.

## RED intent

Draft PR #187 now contains:

`experiments/provider_generation_history/tests/red_intent_lab095_under_lock_history_verification.py`

Published blob: `42f7ea0c8d00ce01d68db27f2d93b7d50ddc31cd`.

The contract supplies a history object whose pre-lock view is valid but whose `_verify_durable_locked(q)` reports a corrupt transition under the writer lock. Expected behavior is fail-closed and zero identity/shared-anchor mutation.

The exact RED test has been committed but is not claimed as behaviorally executed in this runtime because the complete exact repository dependency closure remains unavailable through shell Git transport. Source audit of current production shows `prepare_database_identity()` does not call `_verify_durable_locked`, so the production fix is required before this regression can become GREEN.

## Next implementation

Replace the manual under-lock bootstrap/head subset with the inherited supported full-history verifier on the same transaction connection, compare the locked verified current descriptor with runtime/pre-lock current authority, then run the RED and existing migration regressions. Keep PR #187 draft until this and retained downstream gates execute.
