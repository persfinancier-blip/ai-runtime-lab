# LAB-091 — expression UNIQUE adoption gap

Date: 2026-08-28
Issue: #170
Draft PR: #173

## Finding

The current LAB-091 `_unique_key_sets()` rejects partial UNIQUE indexes, but still reads index columns with `PRAGMA index_info()` and drops rows whose column name is `NULL`.

SQLite reports expression-index terms as `cid=-2, name=NULL`. Therefore a legacy index such as:

```sql
CREATE UNIQUE INDEX ux ON t(id, lower(scope));
```

is incorrectly collapsed by the current collector to `('id',)`, even though the index does **not** enforce table-wide uniqueness of `id`.

## Executed reproduction

A fresh in-memory SQLite database was created with `t(id TEXT, scope TEXT)` and `UNIQUE(id, lower(scope))`.

Observed:

- `PRAGMA index_list(t)` identifies the index as UNIQUE and non-partial;
- `PRAGMA index_info('ux')` returns `(id)` plus an expression term with `cid=-2/name=NULL`;
- the current collector returns `{('id',)}`;
- SQLite accepts both `('same','A')` and `('same','B')`.

Assertions proving the false identity guarantee passed. This is mechanism evidence from the current run, not a complete PR #173 acceptance run.

## Durable regression / staged fix

Branch `lab/091-mutable-shared-anchor-writer` now contains:

- red regression `experiments/mutable_shared_anchor_writer/tests/test_adoption_expression_unique_regression.py`, commit `db5b81375f19c7d0e06cc4cc98e992a0f849f1c0`;
- minimal staged patch `research/2026-08-28-lab091-expression-unique-adoption.patch`, commit `b93eb4b733d2cdf6a6f4b644c0186215f607135c`.

The fix keeps a UNIQUE index eligible only when **every** index term is a real named table column. If any `PRAGMA index_info()` term has `name=NULL`, the index is ignored as evidence for a canonical single/compound identity key instead of silently dropping the expression term.

## Adjacent index semantics audit

- `DESC/ASC` order on the same named identity column does not weaken equality uniqueness, so no rejection is justified from this finding.
- a built-in collation such as `NOCASE` on the same named column is at least as strict for exact duplicate strings and does not reproduce this ambiguity class; no broader collation rejection is justified without a counterexample.
- partial UNIQUE remains separately rejected by the prior LAB-091 fix.
- NOT NULL/CHECK structural equivalence should still not be broadened merely for schema similarity; only constraints whose absence permits a reproduced future ambiguity under otherwise supported transitions should become adoption requirements.

## Status

PR #173 remains DRAFT. The runtime validator itself has not yet been rewritten in this run because the available high-level GitHub writer requires whole-file replacement; the current source was exact-read through the connector, but direct shell/raw GitHub transport remains unavailable. The small staged patch and red regression preserve the exact intended change without manually reserializing the security-sensitive validator.

## Exact next action

Apply the staged patch byte-safely to the exact current `adoption_validation.py` blob `bab8366438f266342ab461307c9191c9328653bd`; execute the expression regression together with the earlier weakened-schema/partial-UNIQUE regressions; then continue the full LAB-080/LAB-082 supported-surface gate.
