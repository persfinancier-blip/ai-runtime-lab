# LAB-091 — enforce the single-PREPARED reservation invariant in SQL

Date: 2026-08-27

## Finding

The operation-scoped LAB-091 guard stack already required a new intent to be the exact next shared-anchor position and to bind to the current provider generation. However, the v3 `lab091_v3_intent_requires_current_tail_and_provider` trigger did not enforce the LAB-080 invariant that only one unresolved `PREPARED` intent may exist at a time.

The supported `reserve()` method explicitly checks `SELECT COUNT(*) FROM shared_anchor_intents WHERE status='PREPARED'` and raises `PendingIntent` when any unresolved request exists. The SQL state-machine layer should independently preserve the same invariant so that an accidentally over-broad broker permit cannot create durable state the supported API itself would reject.

## Executable counterexample

A focused SQLite model using the published v3 conditions accepted:

1. `intent-1`, PREPARED, predecessor 0, position 1;
2. durable tail advance 0 -> 1;
3. `intent-2`, PREPARED, predecessor 1, position 2, while `intent-1` was still PREPARED.

Both rows used contiguous positions and the current provider generation. Before the fix the second insert committed successfully, leaving two unresolved intents.

## Fix

`cross_table_guards.py` now adds an independent condition to the v3 intent INSERT trigger:

- reject the insert if any existing `shared_anchor_intents.status='PREPARED'` row exists.

This preserves the supported LAB-080 reservation state machine at SQL level. Once the prior intent is resolved to CONFIRMED, the next exact contiguous reservation is allowed.

Published artifacts:

- `cross_table_guards.py` blob `fe7696e27ba29a1f1fd090279ebd1082810de78b`;
- `test_single_prepared_guard.py` blob `78fc440552855c900a6aa633e7bcdb16546ea154`.

Exact published-source reconstruction matched both blobs and `operation_permit.py` blob `637784a5cb61a024a1df3e0e983887b6d0a838be`. Regression result: **2/2 PASS**; compileall PASS.

## Boundary

This remains broker-bug containment, not a replacement for LAB-087. An arbitrary same-privilege SQL/schema actor remains outside the LAB-091 standalone claim.
