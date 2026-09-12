# LAB-091 first-adoption lock envelope

Date: 2026-08-28

## Finding

The previously proposed LAB-082 refactor is not required to close the LAB-091 first-adoption TOCTOU.

`SupportedHistoryBoundOperationScopedAsymmetricSharedAnchorLedger._install_guards()` can acquire `BEGIN IMMEDIATE` first, then run the existing complete inherited `verify_durable()` before any LAB-091 guard DDL. The inherited verifier opens a sibling read-only transaction. SQLite's writer reservation prevents any competing legacy/lower writer from changing the committed database until the guard-install transaction commits or rolls back, while the sibling reader can still inspect committed state.

This gives the needed ordering:

1. acquire SQLite writer reservation;
2. re-run the complete LAB-082 durable verification contract;
3. install LAB-091 operation/cross-table/history-binding guards;
4. validate preexisting mutable state;
5. commit all guards atomically.

If corruption occurred after the constructor's earlier verification but before step 1, the locked re-verification rejects it before any guard is persisted. If a lower writer attempts corruption after step 1, SQLite serialization blocks that writer until adoption completes.

## Change

`experiments/mutable_shared_anchor_writer/history_bound_operation_scoped.py` now calls `self.verify_durable()` immediately after `BEGIN IMMEDIATE` and before guard installation.

Published commit: `1d1a4586832a9cf660c14637a279ce1342641a69`

Published blob: `931bd4ad0585607866ae27fabf5d6fd4af3dc35e`

The local reconstruction used for syntax checking hashed to the same Git blob `931bd4ad0585607866ae27fabf5d6fd4af3dc35e`; `python -m py_compile` passed.

## Test status

The existing deterministic regression `tests/test_adoption_toctou_guard_persistence_regression.py` models corruption after the constructor's first full verification. Under the new ordering, the second full verification occurs under the writer reservation and must reject that already-committed corruption before guard DDL.

A full real-stack unittest execution was not available in this run because the executor has no GitHub DNS/network checkout path. Therefore this note records **syntax/hash evidence only, not a unittest PASS**. The regression remains part of the next executable gate.

## Security interpretation

This is a serialization fix, not an authorization expansion. It does not grant a new mutation capability, weaken LAB-082 verification, or replace the verifier with a partial local approximation. Same-privilege direct file manipulation remains outside LAB-091's standalone claim and is owned by the LAB-087 broker/process/filesystem boundary.
