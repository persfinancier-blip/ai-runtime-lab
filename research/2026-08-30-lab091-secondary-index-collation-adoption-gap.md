# LAB-091 secondary-index collation adoption gap

Date: 2026-08-30
Issue: #170
PR: #173

## Finding

A legacy protected table can carry a non-UNIQUE secondary index whose indexed term uses a custom collation. Such an index does not establish identity, so the earlier LAB-091 schema-domain validation did not inspect it. However, SQLite maintains secondary indexes during INSERT/UPDATE. If the legacy-only collation is not registered on the LAB-091 connection after restart, an otherwise-valid supported write fails with `sqlite3.OperationalError: no such collation sequence`.

This is reachable without unsupported raw-DML assumptions: the legacy database may have been created by a prior application/runtime that registered the collation, then later adopted by LAB-091 on a connection that does not register it.

## Reproduction

1. Create canonical protected tables.
2. Register `LEGACY_ONLY` on the legacy connection.
3. Add `CREATE INDEX ... ON shared_anchor_intents(component_id COLLATE LEGACY_ONLY)`.
4. Close the legacy connection and reopen without registering `LEGACY_ONLY`.
5. Execute an otherwise-valid INSERT into `shared_anchor_intents`.

Observed result: `sqlite3.OperationalError: no such collation sequence: LEGACY_ONLY`.

## Fix

Published on `lab/091-mutable-shared-anchor-writer` / draft PR #173:

- `7e575ec5c14d9184661f4acdba9fdb6b9161bd8e` — add `adoption_secondary_indexes.py`;
- `b909c6ff52014f65d797fde19d6aa0ce55ae7004` — wire the validator into the final adoption/restart envelope;
- `7c815210730c7d04be039eea9766115821e68781` — add regression test; current branch head at publication time.

The new validator checks non-UNIQUE secondary index terms on all protected mutable tables and rejects inherited non-BINARY collations. Canonical/ordinary BINARY secondary indexes remain allowed. UNIQUE/PK indexes continue to be validated by the existing schema-domain gate.

## Validation

Re-fetched published files and verified their exact Git blob identities before execution:

- `adoption_secondary_indexes.py`: `fa74904a6264a5eb3d888b02d398b27959321fff`;
- regression test: `1924e25bde8c20e502686b9e5b309c45327287e6`.

Focused exact-content unittest: **2/2 PASS**.

- canonical schema + ordinary BINARY secondary index: accepted;
- custom-collation secondary index: pre-fix supported-write failure reproduced and adoption now rejects the schema.

Python startup emitted the known unrelated spreadsheet-runtime warmup timeout, but unittest returned exit code 0 and both tests were `ok`.

This is focused exact-content evidence, not a whole-branch/full-stack execution claim.

## Scope / non-claims

This fix addresses the reproduced non-BINARY secondary-index collation failure only. It does not yet claim that every possible expression/partial non-UNIQUE index is safe; those should be hardened only if a reachable supported-write failure is reproduced.
