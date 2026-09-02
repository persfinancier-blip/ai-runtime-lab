# LAB-090 concurrent duplicate rotation after winner release

Date: 2026-09-03
Scope: draft PR #175, head `d9a381dd4607a928cd1315adef6431e239995bc1`
Issue: #169 / LAB-090

## Finding

`SupportedHistoricalSharedAnchorLedger.rotate_provider()` has an idempotency race when two coordinators begin the same provider-generation activation before either has inserted the activation row, but one coordinator completes the SQL rotation, provider commit, durable `COMMITTED` acknowledgement, and provider release before the second coordinator reaches its SQL insert.

This is not the previously recorded post-prepare cleanup leak and does not require a fake/subclass provider. It follows from the exact LAB-090 coordinator and exact `FencedActivationProvider` state machine.

## Source path

The coordinator checks for an existing activation row before preparing the provider ticket. If none exists, it prepares the ticket and later enters `BEGIN IMMEDIATE`.

Inside the SQL exception path, a failed insert is treated as already SQL-committed when `_activation_row(activation_id=ticket.activation_id)` finds a durable row in either `SQL_COMMITTED` or `COMMITTED`; in that case the original SQL exception is intentionally swallowed and execution falls through to `_commit_or_reconcile_activation(provider, ticket)`.

`FencedActivationProvider.commit_activation()` is idempotent and returns the current status when `activation_status(ticket)` is either `COMMITTED_FENCED` or `RELEASED`.

However `_commit_or_reconcile_activation()` accepts only `COMMITTED_FENCED`. A legitimate `RELEASED` result therefore raises `HistoricalVerificationError("provider activation must remain fenced until durable acknowledgement")`, even when the durable activation row is already `COMMITTED` and the same exact ticket was correctly released by the winning coordinator.

## Concrete interleaving

Start with durable generation g1, candidate g2, no g2 activation row, and one shared provider-owned `ActivationState`.

1. Coordinator A: preflight `_activation_row(g2)` -> absent.
2. Coordinator B: preflight `_activation_row(g2)` -> absent.
3. A: `prepare_activation()` installs ticket T / PREPARED.
4. B: `prepare_activation()` idempotently returns the same ticket T / PREPARED.
5. A: `BEGIN IMMEDIATE`; inserts T as `SQL_COMMITTED`; rotates durable head g1->g2; commits.
6. A: provider `commit_activation(T)` -> `COMMITTED_FENCED`.
7. A: marks durable activation `COMMITTED`.
8. A: `release_activation(T)` -> `RELEASED`.
9. B: reaches `BEGIN IMMEDIATE`; there is no unresolved `SQL_COMMITTED` row because T is already durable `COMMITTED`.
10. B: attempts the same activation INSERT and gets the uniqueness/primary-key conflict.
11. B exception path re-reads T, sees durable `COMMITTED`, sets `sql_committed=True`, and intentionally does not abort/re-raise the SQL conflict.
12. B falls through to `_commit_or_reconcile_activation(provider, T)`.
13. Exact provider `commit_activation(T)` returns `RELEASED` because T is committed and no longer pending.
14. `_commit_or_reconcile_activation()` rejects that valid terminal status and raises `HistoricalVerificationError`.

The durable/provider state is already correct, but the duplicate supported operation fails instead of converging idempotently on the completed rotation. A separate ledger instance participating in the race can remain runtime-stale even though the requested rotation succeeded durably.

## Why existing tests do not cover this schedule

`test_activation_overlapping_rotation.py` covers a different overlap: g2 remains `SQL_COMMITTED` after a provider commit failure and a subsequent g3 rotation must be blocked. It does not run two same-generation activations through the duplicate-insert-after-release schedule.

`test_activation_historical_retry.py` covers retry of g2 only after g3 is already durable current and correctly requires failure as historical. It does not cover a same-generation concurrent duplicate whose exact ticket is already terminally released.

## Regression-first contract

Add a deterministic two-coordinator/same-generation RED that pauses B after provider prepare and lets A finish through durable `COMMITTED` + provider `RELEASED` before B attempts its insert.

Pre-fix expected result:
- durable head is g2;
- durable activation T is `COMMITTED`;
- provider status for T is `RELEASED`;
- B nevertheless raises `HistoricalVerificationError` from `_commit_or_reconcile_activation()`.

Post-fix requirement:
- a duplicate attempt that re-reads the exact same durable ticket in `COMMITTED` and verifies provider status `RELEASED` must converge idempotently;
- do not accept `RELEASED` for a durable `SQL_COMMITTED` ticket, because that remains premature-release evidence;
- do not weaken exact-ticket equality or current-generation checks;
- a conflicting ticket/generation must still fail closed;
- preserve the existing rule that provider release is permitted only after durable acknowledgement.

## Design implication

The reconciliation decision needs both durable activation status and provider status. `RELEASED` is valid only when the exact durable ticket is already `COMMITTED`; it is invalid when durable state is still `SQL_COMMITTED`.

A minimal repair should therefore distinguish terminal duplicate reconciliation from the normal `commit -> durable acknowledge -> release` path rather than globally teaching `_commit_or_reconcile_activation()` that `RELEASED` is always acceptable.

## Execution status

Source reasoning was performed against GitHub-fetched PR #175 bytes. Direct Git transport was reprobed first in this run and failed before repository access with `Could not resolve host: github.com`, so no exact branch execution or behavioral PASS is claimed here.
