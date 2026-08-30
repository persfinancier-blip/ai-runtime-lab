# LAB-091 — expression/partial secondary-index adoption gap

Date: 2026-08-30

## Finding

A legacy protected LAB-091 table can carry a non-UNIQUE expression or partial index that depends on a deterministic application-defined SQLite function. The index is not an identity/UNIQUE constraint, but SQLite still evaluates its expression/predicate while maintaining the index on ordinary INSERT/UPDATE.

If the legacy database is reopened by the supported LAB-091 connection without that legacy-only function registered, an otherwise-valid supported write fails with `sqlite3.OperationalError: unknown function: legacy_only()`.

Reproduced forms:

```sql
CREATE INDEX intents_component_expr
ON shared_anchor_intents(legacy_only(component_id));
```

and

```sql
CREATE INDEX intents_component_partial
ON shared_anchor_intents(component_id)
WHERE legacy_only(component_id) > 0;
```

Both were created while `legacy_only` was registered as deterministic, committed, closed, then reopened without the function. A canonical-shape INSERT failed while SQLite attempted index maintenance.

## Decision

Fail closed during first adoption for non-UNIQUE secondary indexes on protected mutable tables when either:

- any key term is an expression (`PRAGMA index_xinfo` key term with no column name); or
- `PRAGMA index_list(...).partial` is true.

Existing rejection of non-BINARY secondary-index collations remains. Ordinary column-only, non-partial, BINARY secondary indexes remain accepted.

This deliberately does not attempt to parse or reconstruct arbitrary legacy SQL expression dependencies. The supported LAB-091 connection does not own those functions/semantics, so accepting them would claim a write-compatibility guarantee it cannot enforce.

## Published changes

PR #173 branch `lab/091-mutable-shared-anchor-writer`:

- `7971901b949884e5218a91f0ce4472584f432822` — extend `adoption_secondary_indexes.py` to reject expression and partial non-UNIQUE indexes;
- `ff6abe5893b203ebdc978b3db08a1dc8bd950c26` — add expression/partial regression coverage.

Published validator blob: `593a018da8471070e6b0c7606a32623c585b00d4`.
Published regression blob: `b50a92555a0df86c7b589a2123d9d94fd7c411a1`.

## Executed evidence

The published validator text was reconstructed locally and its Git blob identity recomputed as exactly `593a018da8471070e6b0c7606a32623c585b00d4` before execution.

Focused mechanism gate:

- expression index: pre-fix supported-shape INSERT -> `OperationalError: unknown function: legacy_only()`; adoption validator -> rejected;
- partial index: pre-fix supported-shape INSERT -> `OperationalError: unknown function: legacy_only()`; adoption validator -> rejected;
- ordinary BINARY column-only secondary index -> accepted.

This is focused exact-validator/mechanism evidence, not whole-branch/full-stack execution.
