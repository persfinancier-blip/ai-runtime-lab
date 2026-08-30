# LAB-090 — post-provider-commit fence release race

Date: 2026-08-30
Issue: #169
Draft PR: #175 (`lab-090-provider-activation-fencing`, head observed `5f680da36733a54b6d79d554a083276a1643a0ce`)

## Observation

A fresh source audit found a concrete remaining race in the activation protocol.

Current `FencedActivationProvider.commit_activation()` records the ticket in `activation_state.committed` and immediately clears `activation_state.pending`. `increment()` fences only while `pending` is non-null. Coordinator `_commit_or_reconcile_activation()` then marks the SQLite `provider_generation_activations` row from `SQL_COMMITTED` to `COMMITTED` in a separate operation.

Therefore the provider-side fence is released before the coordinator has durably completed activation.

## Reachable schedule

Starting with candidate provider position `N` and a durable activation row already `SQL_COMMITTED`:

1. coordinator calls `provider.commit_activation(ticket)`;
2. provider validates `value == N`, records ticket COMMITTED, and clears `pending`;
3. before coordinator executes `_mark_activation_committed(ticket)`, an external actor calls `increment(expected=N, ...)`;
4. `increment()` is no longer fenced and advances provider to `N+1`;
5. coordinator updates SQLite activation row to `COMMITTED` without re-establishing the exact provider position.

Result: provider generation is durably activated while the external provider is already ahead of the shared-anchor tail. This reintroduces the freshness/correctness failure LAB-090 is intended to close, only in the later `provider commit -> SQL acknowledgement` window.

The existing SQLite trigger does not close this race: it blocks coordinator inserts into `shared_anchor_intents` while the SQL row is `SQL_COMMITTED`, but it cannot serialize or fence an external provider writer.

## Required protocol change

Provider commit must not release the external-write fence. The provider needs an explicit post-coordinator acknowledgement/finalization step, e.g.:

- `PREPARED`: reservation installed, increments fenced;
- `COMMITTED_FENCED`: provider commit is durable/idempotent, increments still fenced;
- coordinator durably marks the exact ticket `COMMITTED` in SQLite;
- coordinator calls an idempotent provider `release_activation(ticket)` / `finalize_activation(ticket)`;
- only then may ordinary increments proceed.

Crash/restart semantics must cover both unresolved directions:

- SQLite `SQL_COMMITTED` + provider `PREPARED` or `COMMITTED_FENCED`: finish provider commit, mark SQLite committed, then release;
- SQLite `COMMITTED` + provider still `COMMITTED_FENCED`: restart must release the exact ticket before normal provider writes proceed.

The release operation must verify the exact activation ticket/fence and must be idempotent. It must not permit a different activation or stale ticket to release the fence.

## Evidence / capability note

The exact PR #175 source was inspected through the GitHub connector in this run. Direct branch execution was probed with `git clone --depth 1 --branch lab-090-provider-activation-fencing ...` and failed before repository execution with `Could not resolve host: github.com`; therefore no whole-branch unittest result is claimed.

This note records a source-level concrete defect and the minimum protocol requirement for the next implementation slice. PR #175 should remain draft until this race is fixed and exact branch/downstream behavioral gates execute.
