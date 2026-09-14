# LAB-091 persisted-trigger restart constructor failure

## Finding

The final LAB-091 trigger set is durable across SQLite reopen. That exposed an incompatibility with the historical LAB-080 constructor path: `SharedAnchorLedger._init()` unconditionally executes `INSERT OR IGNORE INTO shared_anchor_meta VALUES(1,0)` on every startup.

SQLite runs a `BEFORE INSERT` trigger before uniqueness conflict resolution. Once `lab091_v2_meta_no_insert` is persisted, the historical `INSERT OR IGNORE` therefore raises before `OR IGNORE` can suppress the existing singleton conflict. A normal restart fails before durable-state verification.

## Executed counterexample

File-backed SQLite reproduction:

1. create the LAB-080 shared-anchor schema and singleton `(1,0)`;
2. persist `lab091_v2_meta_no_insert`;
3. close and reopen the database;
4. replay the historical `INSERT OR IGNORE` initializer.

Observed result: `sqlite3.IntegrityError: LAB-091 meta singleton already initialized`.

## Fix

The final `SupportedHistoryBoundOperationScopedAsymmetricSharedAnchorLedger` now overrides `_init()` and calls `initialize_shared_anchor_schema()`.

The restart-safe initializer:

- acquires `BEGIN IMMEDIATE`;
- creates the three LAB-080 tables with `CREATE TABLE IF NOT EXISTS`;
- reads the metadata singleton first;
- inserts `(1,0)` only for a genuinely fresh database;
- leaves persistent LAB-091 guards untouched;
- if a guarded database is missing the singleton, the attempted insert is rejected by the persisted guard and startup fails closed.

This avoids a startup trigger bypass such as temporarily dropping the guard and avoids weakening `lab091_v2_meta_no_insert` merely to accommodate `INSERT OR IGNORE`.

## Exact published-source evidence

Published blobs:

- `restart_safe_schema.py`: `975610219c710a42c4a8377bd38f9593a8bb23f5`;
- `test_restart_safe_schema.py`: `3112877432a3f575e5624537d4c5180cf0b379d7`;
- `history_bound_operation_scoped.py`: `8d2d511b2ea895c2f680ac495e26c4d694fd047d`.

The first two files were reconstructed locally and verified with `git hash-object` before execution. Result: **4/4 PASS + compileall PASS**.

The published final supported class was separately reconstructed and its local hash matched `8d2d511b...`, confirming the `_init()` override is wired into the actual candidate rather than existing only as helper/test code.

## Remaining boundary

This closes the constructor/restart incompatibility only. PR #173 remains draft until the final supported object is executed end-to-end against exact real LAB-080/LAB-082 dependencies for two-worker convergence, crash rollback, timeout/UNKNOWN reconciliation, and LAB-087 composition.
