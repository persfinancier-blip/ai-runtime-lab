# LAB-091 — function-valued extra-column DEFAULT adoption gap

Date: 2026-08-30
Issue: #170
PR: #173 (`lab/091-mutable-shared-anchor-writer`)

## Finding

The first-adoption extra-column validator accepted ordinary additive columns whenever they were nullable or had a DEFAULT. That is not sufficient for SQLite compatibility: a DEFAULT expression is evaluated when the supported LAB-091 writer omits the extra column.

A legacy application can create a protected table with an additive column such as:

```sql
legacy_note TEXT DEFAULT (legacy_only())
```

while registering `legacy_only()` on its connection. SQLite persists the schema expression. After reopen through the supported LAB-091 connection, which does not register that legacy-only UDF, an otherwise canonical INSERT that omits `legacy_note` fails with:

```text
sqlite3.OperationalError: unknown function: legacy_only()
```

This is a reachable adoption compatibility defect: adoption could succeed even though the next supported write was not executable under the supported connection contract.

## Reproduction

A file-backed SQLite probe created the schema while a deterministic zero-argument `legacy_only()` function was registered, inserted successfully on that legacy connection, closed it, reopened without the function, and reproduced `OperationalError: unknown function: legacy_only()` on an omitted-column INSERT.

## Fix

`experiments/mutable_shared_anchor_writer/adoption_extra_columns.py` now detects function-call syntax in DEFAULT text returned by `PRAGMA table_xinfo` for non-canonical ordinary columns and rejects such legacy schemas fail-closed.

The change intentionally preserves already-supported literal/default-keyword extras, including string literals, numeric literals, and `CURRENT_TIMESTAMP`. Generated extras and NOT NULL/no-default extras remain rejected by the existing rules.

Published runtime commit: `5b9ce523611193120212a0d335edf33054bf8ece`
Published validator blob: `c5e6617bd7abf73864e31ec191451af0c281842b`
Regression commit / current PR head at publication: `7551a6e80c677512da0093bd7ddd083f5189a516`
Regression blob: `3c613366fdcb2f626d4d1c39af8060fb58bca760`

## Validation actually executed

Focused local unittest using the same candidate validator/test bytes: **2/2 PASS**.

Coverage:
- literal string DEFAULT accepted;
- numeric DEFAULT accepted;
- `CURRENT_TIMESTAMP` accepted;
- legacy-only function DEFAULT reproduces the pre-fix supported-write failure;
- adoption validator rejects that function-valued default before supported use.

The Git object hashes recomputed locally for both published files exactly match the fetched published blob SHAs above.

An unrelated spreadsheet-runtime warmup printed a timeout during Python startup, but the unittest process returned exit code 0 and both LAB-091 tests completed successfully. This is not whole-branch/full-stack execution.

## Audit boundary

This patch does not claim to parse arbitrary SQLite expressions or make LAB-091 a same-privilege SQLite sandbox. It closes the reproduced persisted-default/UDF failure while retaining simple ordinary defaults. Future hardening remains reproduction-driven per repository policy.

## LAB-086 capability observation

This run also confirmed the GitHub connector can return PR #165's complete 949-line `strict_fence.py` per-file patch. However, there is still no supported operation in the observed runtime that composes that exact fetched payload with the retained hidden-rowid unified patch and feeds the result into a normal Contents API write without model/manual whole-file reserialization. Therefore no LAB-086 branch mutation was attempted.
