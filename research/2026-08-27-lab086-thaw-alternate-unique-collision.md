# LAB-086 thaw alternate-UNIQUE collision

Date: 2026-08-27

## Finding

The published combined thaw hardening protects existing authenticated-history rows by their primary content identity. That is insufficient for `asymmetric_provider_generations`, whose real LAB-082 schema also declares `UNIQUE(provider_id,generation)`.

During LAB-086 transaction-scoped thaw the ordinary INSERT-deny for `asymmetric_provider_generations` is intentionally removed so the verified final writer can create the next provider generation. The permanent trigger `lab086_provider_generation_existing_key_no_replace` currently rejects NULL/existing `generation_id`, but it does not reject a new `generation_id` that collides with an existing `(provider_id,generation)` tuple.

With SQLite `PRAGMA recursive_triggers=OFF` (the default), `INSERT OR REPLACE` can resolve that alternate UNIQUE conflict by deleting the authenticated old row and inserting the new row without the expected DELETE trigger protecting the old row. This is a fail-closed durable-history corruption/DoS path inside the audited post-cutoff DML boundary.

## Executed counterexample

Using the exact LAB-082 table shape:

```sql
CREATE TABLE asymmetric_provider_generations(
  generation_id TEXT PRIMARY KEY,
  provider_id TEXT NOT NULL,
  generation INTEGER NOT NULL,
  public_key_hex TEXT NOT NULL,
  UNIQUE(provider_id,generation)
);
```

and the current PK-only collision trigger, the following succeeded:

```sql
INSERT OR REPLACE INTO asymmetric_provider_generations
VALUES('attacker-generation-id','anchor-A',1,'attacker-key');
```

The durable row changed from `('generation-1-id','anchor-A',1,'original-key')` to the attacker row.

A focused candidate trigger that additionally rejects an existing `(provider_id,generation)` collision blocked that REPLACE while still allowing a genuinely new successor `('generation-2-id','anchor-A',2,...)`.

## Scope audit

The other currently INSERT-thawed authenticated-history tables use only the primary key as a SQL UNIQUE identity in their pinned schemas. The additional alternate UNIQUE identity is specific to `asymmetric_provider_generations` in the current closure.

## Required fix

Keep the permanent primary-key/NULL collision fence, and for `asymmetric_provider_generations` additionally reject INSERT whenever a row already exists with:

```sql
provider_id IS NEW.provider_id AND generation IS NEW.generation
```

This semantic collision predicate must remain installed during transaction-scoped thaw. The ordinary final writer must still be able to insert a new non-NULL generation ID for the next, previously unused `(provider_id,generation)` pair.

Regression: `experiments/asymmetric_break_glass_history/tests/test_thaw_alternate_unique_collision_regression.py`.

PR #165 must remain draft until this RED regression is green on published exact bytes, the executable snapshot is repinned, and the full LAB-080→086 gate is executed.
