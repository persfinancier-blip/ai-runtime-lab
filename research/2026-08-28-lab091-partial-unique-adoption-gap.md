# LAB-091 — partial UNIQUE indexes are not identity constraints

Date: 2026-08-28

## Finding

`validate_existing_mutable_state_locked()` previously treated every SQLite UNIQUE index returned by `PRAGMA index_list` as a table-wide identity guarantee. That is incorrect for partial UNIQUE indexes: `PRAGMA index_list(...)[4] == 1` means the index is partial and its uniqueness applies only to rows satisfying the index predicate.

A weakened legacy schema can therefore present a clean adoption snapshot with, for example, `UNIQUE(intent_id) WHERE status='CONFIRMED'`. The old schema check reports `('intent_id',)` as present even though future PREPARED rows can duplicate that identity. This recreates the same future-ambiguity class that LAB-091's schema-contract hardening is intended to prevent.

## Fix

Branch `lab/091-mutable-shared-anchor-writer`:

- validator commit `7198487c306077724d3d8721e1d1e2b28004288c`, blob `bab8366438f266342ab461307c9191c9328653bd`;
- regression introduced at `ed6713a3f7d42251ed66d504e6474fb8d993dc5f`, then syntax-corrected at `affb299bf9810c2bffcde0d6060ebf3e49b9975a`, final test blob `e77521d839510490a2bea4d92d68d9071241ff35`.

`_unique_key_sets()` now ignores partial UNIQUE indexes when establishing canonical identity constraints. The regression covers partial substitutes for intent ID, position, request ID, watermark component ID and provider-receipt request ID.

## Executed mechanism evidence

A local SQLite probe created:

```sql
CREATE TABLE x(id TEXT, status TEXT NOT NULL);
CREATE UNIQUE INDEX x_id_partial ON x(id) WHERE status='CONFIRMED';
INSERT INTO x VALUES('same','PREPARED');
INSERT INTO x VALUES('same','PREPARED');
```

Observed:

- both duplicate PREPARED rows were accepted;
- `PRAGMA index_list(x)` returned the partial flag `1`;
- the pre-fix key collector returned `{('id',)}`;
- the corrected collector returned `set()`;
- probe assertion PASS.

This is mechanism evidence only. The complete PR #173 real-stack gate remains required before readiness/merge.

## DDL audit disposition

The remaining `NOT NULL` / `CHECK` concern is materially different. Current admission revalidates existing row domains, and the supported writer/one-shot guards construct bounded canonical transitions; losing a CHECK constraint alone has not yet been shown to recreate future ambiguity under a supported transition. Continue auditing, but do not broaden the schema contract without a reproduced failure.
