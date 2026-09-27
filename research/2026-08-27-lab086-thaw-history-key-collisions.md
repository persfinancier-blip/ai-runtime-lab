# LAB-086 thaw history key collision bypass

Date: 2026-08-27

## Finding

The post-cutoff final writer intentionally thaws INSERT guards for a small set of tables so a verified rotation can append one new authority/transition/proof row. UPDATE/DELETE immutability guards remain installed during that interval.

That is not sufficient for ordinary SQLite rowid tables. With the default `recursive_triggers=OFF`, `INSERT OR REPLACE` can delete a conflicting row internally and insert a replacement without traversing the ordinary DELETE trigger. In addition, non-`INTEGER PRIMARY KEY` columns such as `TEXT PRIMARY KEY` may contain NULL in ordinary SQLite rowid tables.

The current permanent existing-key collision guard covers the two LAB-086 post-cutoff proof tables, but the same least-privilege invariant is missing from other INSERT-thawed authenticated-history tables:

- `provider_recovery_public_authorities.authority_id`;
- `provider_recovery_public_transitions.new_authority_id`;
- `provider_rotation_authorities.authority_id`;
- `provider_rotation_authority_transitions.new_authority_id`;
- `provider_rotation_threshold_proofs.new_provider_generation_id`;
- `asymmetric_provider_generations.generation_id`;
- `asymmetric_provider_transitions.new_generation_id`.

## Executed counterexample

A focused SQLite reproduction matching the current thaw policy showed that, after the normal INSERT-deny is removed while UPDATE/DELETE guards remain:

- `INSERT OR REPLACE` of an existing public authority changed its payload from `original` to `tampered`;
- `INSERT OR REPLACE` of an existing public transition changed predecessor/root metadata to attacker values;
- the same REPLACE pattern was accepted for all seven INSERT-thawed history tables listed above;
- a NULL primary-key row was also accepted for every modeled `TEXT PRIMARY KEY` identity.

This is durable fail-closed history damage / violation of the least-privilege thaw contract. It is not an authority-escalation claim against a process that lacks access to the final-writer connection; it matters because LAB-086 explicitly claims that authenticated history remains immutable even while the final writer temporarily thaws only the capability needed to append the next row.

## Required invariant

Every table whose creation guard is removed by `remove_public_mutation_fence_locked()` must retain a permanent collision/NULL guard that is **not** removed by thaw:

```sql
BEFORE INSERT ON table
WHEN EXISTS(cutoff)
 AND (
   NEW.key IS NULL
   OR EXISTS(SELECT 1 FROM table WHERE key IS NEW.key)
 )
BEGIN
  SELECT RAISE(ABORT,'LAB-086 existing authenticated history key cannot be replaced');
END
```

This preserves legitimate insertion of a new non-NULL key while denying NULL identity, `INSERT OR REPLACE` of an existing key and UPSERT-existing identity.

The already-recorded NULL-proof-key patch must use the same NULL-safe `IS` predicate for the two post-cutoff proof tables.

## Regression

`experiments/asymmetric_break_glass_history/tests/test_thaw_history_key_collision_regression.py` is intentionally RED on the current runtime. It creates all seven affected history surfaces, installs the real LAB-086 fence, enters transaction-scoped thaw and requires for every table:

1. REPLACE-existing is rejected and the old row remains unchanged;
2. NULL identity is rejected;
3. a new unique non-NULL key remains insertable.

Keep the existing `test_thaw_null_proof_key_regression.py` as a separate proof-table regression.

## Integration discipline

Apply this together with the pending NULL-proof predicate correction to the exact current `strict_fence.py` blob. Do not remove the permanent collision triggers in `remove_public_mutation_fence_locked()`; only the full reinstall helper may drop/recreate them. `assert_public_mutation_fence_locked()` must require them whenever their table exists.

After publication, run both thaw regressions plus the existing strict-fence/conflict-algorithm/inherited-writer suites, repin the executable snapshot and only then resume the full 30+ module real-ledger gate.
