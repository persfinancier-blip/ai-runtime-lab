# LAB-090 — atomic activation schema installation fix design

Date: 2026-08-31

## Context

`SupportedHistoricalSharedAnchorLedger._init_activation_schema()` currently installs/verifies `provider_generation_activations` and `block_intent_during_provider_activation` in two separate `executescript()` calls. SQLite `executescript()` introduces independent transaction boundaries here, so a restart with a missing trigger can expose a writer window after the activation table exists/has been verified but before the blocking trigger is installed.

The deterministic regression for this condition is already published on PR #175 as `experiments/provider_generation_history/tests/test_activation_schema_installation_race.py` at head `96d7ad17836174c94c668d00e8608e498b1c5254`.

## Fresh capability observations

- GitHub connector read/write is available.
- Direct git clone was attempted again and failed before repository execution with `Could not resolve host: github.com`.
- Therefore exact published-head behavioral/full-suite execution is still unavailable in this run and no branch GREEN is claimed.

## Candidate fix

Use one explicit writer transaction across the entire install+verify sequence:

1. `BEGIN IMMEDIATE`.
2. `CREATE TABLE IF NOT EXISTS ...` with single-statement `execute()`.
3. Read `sqlite_master` and require the exact canonical activation-table definition.
4. `CREATE TRIGGER IF NOT EXISTS ...` with single-statement `execute()`.
5. Read `sqlite_master` and require the exact canonical trigger definition.
6. Commit only after both verifications succeed; rollback on any exception.

Do not use `executescript()` in this path because its transaction behavior is exactly what creates the installation gap. Do not drop/recreate durable objects.

The exact minimal candidate diff is retained on the LAB-090 branch at `research/patches/lab090-activation-schema-installation-transaction.patch`, commit `98a1059e32d3927b661e873077acc070e2d22af7`. This is evidence/design only; the source file is not claimed fixed yet.

## Independent mechanism validation actually executed

A separate file-backed SQLite test was run with two threads/connections:

- installer opened `BEGIN IMMEDIATE`, created the activation table, inserted an unresolved `SQL_COMMITTED` activation, paused, installed the canonical trigger, and committed;
- a concurrent writer attempted to insert into `shared_anchor_intents` after table creation but before trigger installation had completed.

Observed result:

- concurrent writer did not pass through the gap;
- after installer commit, its insert failed with `sqlite3.IntegrityError: provider activation unresolved`;
- persisted shared-anchor intent count remained `0`.

Result: **atomic schema+trigger installation mechanism PASS**.

This validates the SQLite locking/ordering mechanism, but it is not a substitute for executing the exact PR branch regression and downstream suite.

## Safety / audit

The candidate is narrow and reversible. It does not alter schema definitions, durable row semantics, activation lifecycle, or recovery ordering. It only changes transaction scoping and replaces `executescript()` with `execute()` for two single DDL statements.

Remaining proof obligation: apply the minimal source patch to exact current PR head, re-fetch/diff-audit it, then execute `test_activation_schema_installation_race.py` and the activation restart/integration/downstream gates when exact repository execution becomes available.
