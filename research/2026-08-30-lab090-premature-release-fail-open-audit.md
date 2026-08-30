# LAB-090 premature provider release fail-open audit

Date: 2026-08-30

## Scope

Fresh source-level audit of draft PR #175 (`lab-090-provider-activation-fencing`, observed head `348b279d979600e4a03333bc6ed729922705ff5b`) after the `COMMITTED_FENCED -> RELEASED` correction.

## Finding

The current coordinator still accepts a provider-side `RELEASED` status while the durable SQLite activation row is only `SQL_COMMITTED`.

Two paths do this:

1. `_commit_or_reconcile_activation()` accepts both `COMMITTED_FENCED` and `RELEASED`, then calls `_mark_activation_committed()`.
2. `_recover_pending_activation()` handles durable `SQL_COMMITTED` and provider status in `{COMMITTED_FENCED, RELEASED}` by marking the SQLite row `COMMITTED` and then calling `_release_committed_activation()`; that helper treats `RELEASED` as an idempotent success.

This contradicts the intended ordering invariant documented in the same source: provider commit must retain the external fence; the coordinator must durably acknowledge the exact ticket as `COMMITTED`; only then may exact-ticket release remove the fence.

Therefore `SQLite=SQL_COMMITTED + provider=RELEASED` is not a normal idempotent state. It proves that the fence was removed before durable coordinator acknowledgement (or provider state was otherwise mutated out of protocol). Accepting it converts a protocol violation into a committed activation and creates an interval in which external provider increments are no longer fenced while the SQL state still advertises unresolved activation.

## Minimal state-machine reproduction

The current acceptance predicate was independently modeled at the state level. For `SQL_COMMITTED`, provider states resolve as:

- `PREPARED` -> recovery/commit path;
- `COMMITTED_FENCED` -> legitimate durable acknowledgement then release;
- `RELEASED` -> **currently accepted**, but must fail closed;
- `ABSENT` -> fail closed.

No whole-branch execution is claimed in this run; exact branch transport remains unavailable through direct git in the observed runtime. The finding is source-level and follows directly from the published branch control flow.

## Required correction

Make the boundary fail closed:

- `_commit_or_reconcile_activation()` must accept only `COMMITTED_FENCED` after `commit_activation()` / UNKNOWN reconciliation. A returned `RELEASED` before `_mark_activation_committed()` is a `HistoricalVerificationError`.
- `_recover_pending_activation()` with durable `SQL_COMMITTED` must accept `PREPARED` or `COMMITTED_FENCED`; `RELEASED` must raise `HistoricalVerificationError` rather than advance SQLite.
- Keep `RELEASED` idempotency only when the durable SQLite row is already `COMMITTED`.

Add a regression that constructs/persists an `SQL_COMMITTED` activation row, externally releases the exact provider ticket before coordinator acknowledgement, and proves restart refuses to mark the activation committed.

## Merge/base observation

The explicit GitHub compare observed PR #175 as `diverged`, 13 commits ahead and 8 behind `main`, with merge-base `6cc7a04496187075db1c02f3e27c1d394da53026`. This establishes stale base divergence but is not by itself evidence of a semantic/file conflict. Do not mark ready or merge until the branch is rebased/updated through a safe supported path and executable gates are clean.

## Decision

PR #175 stays draft. This defect must be corrected before readiness. No speculative adjacent changes are justified by this audit.
