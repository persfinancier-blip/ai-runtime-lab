# LAB-090 — activation schema installation writer race

Date: 2026-08-31

## Status

Narrow audit finding on draft PR #175 (`lab-090-provider-activation-fencing`).

LAB-086 remains priority #1 and was checked first. The available GitHub write surface still exposes complete UTF-8 Contents replacement, not a supported byte-preserving server-side composition of exact predecessor `d4a6a40f...` + retained patch `61841b58...` into required target `b78e7c98...`. The 949-line security-critical `strict_fence.py` was not mutated.

## Finding

`SupportedHistoricalSharedAnchorLedger._init_activation_schema()` currently installs/verifies `provider_generation_activations` and then installs/verifies `block_intent_during_provider_activation` using two separate `executescript()` calls.

With `isolation_level=None`, those DDL steps are separately autocommitted. If the canonical trigger is absent while an unresolved `SQL_COMMITTED` activation row already exists, a concurrent writer from an older/live coordinator can insert a new shared-anchor intent after the table step and before the trigger step.

That violates the LAB-090 invariant that every writer is fenced while provider activation remains SQL_COMMITTED.

## Reproduction evidence

Published deterministic regression on PR #175:

- commit: `96d7ad17836174c94c668d00e8608e498b1c5254`
- file: `experiments/provider_generation_history/tests/test_activation_schema_installation_race.py`
- Git blob: `cfd5c24107a9582bef91cbeeec28a8bc9b6f83c5`
- independent local `py_compile`: PASS
- post-publication GitHub re-fetch blob: exact match `cfd5c24107a9582bef91cbeeec28a8bc9b6f83c5`

The regression wraps the coordinator SQLite connection and pauses immediately after the activation-table creation/verification step. A live writer then attempts `reserve()` while an unresolved activation row exists and the trigger is still absent. Correct behavior requires that writer to remain blocked until trigger installation is complete and then fail with `PendingRotationBlocked`.

A separate file-backed SQLite mechanism probe was actually executed in this run using the same two-autocommit-step shape. Result:

- unresolved activation row present: yes
- table `CREATE ... IF NOT EXISTS` step completes
- writer inserted before trigger creation: **ADMITTED**
- persisted intents in the gap: `1`

Mechanism result: **CONFIRMED**.

This is mechanism evidence plus a published RED candidate. Exact PR-head behavioral execution is still unavailable because direct Git/raw repository execution transport remains blocked; therefore no repository behavioral RED/GREEN or full-suite claim is made.

## Minimal fix direction

Make activation table creation/verification and trigger creation/verification one SQLite write transaction holding the writer reservation across the entire installation boundary.

Important implementation detail: Python `sqlite3.Connection.executescript()` can commit transaction state and is unsuitable for preserving the intended explicit transaction boundary here. Prefer:

1. `BEGIN IMMEDIATE`;
2. single-statement `execute()` for `CREATE TABLE IF NOT EXISTS ...`;
3. verify canonical table type/SQL;
4. single-statement `execute()` for `CREATE TRIGGER IF NOT EXISTS ...`;
5. verify canonical trigger SQL;
6. `COMMIT`.

On any mismatch/error, rollback and fail closed. Do not drop/recreate durable activation evidence.

## Next gate

When exact source execution becomes available, run the new installation-race regression first. The expected current result is RED. Then implement the transaction-boundary fix, require the regression GREEN, and run the existing schema-tamper, trigger-tamper, restart/integration, stale-runtime, verify-component, ticket-binding, numeric-type, and downstream suites before considering PR #175 ready.
