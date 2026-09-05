# LAB-086 — proof REPLACE bypass during transaction-scoped thaw

Date: 2026-08-27

## Finding

The post-cutoff proof tables are normally protected by three triggers: deny creation, deny UPDATE, deny DELETE. The final LAB-086 writer temporarily removes only the creation trigger so it can append a new authenticated proof key while keeping historical rows immutable.

With SQLite's default `PRAGMA recursive_triggers=OFF`, `INSERT OR REPLACE` on an existing primary key can delete the conflicting row internally without running the table's DELETE trigger. During the thaw window the creation trigger is absent, so an existing authenticated proof row can be replaced even though direct UPDATE and DELETE remain blocked.

Affected tables:

- `provider_asymmetric_break_glass_proofs`
- `provider_asymmetric_recovery_public_root_proofs`

A focused executable SQLite counterexample observed:

- direct UPDATE: blocked;
- direct DELETE: blocked;
- `INSERT OR REPLACE` existing proof key: **allowed**, row changed from `original` to `tampered`;
- UPSERT existing key: blocked by the UPDATE trigger.

This violates the stated least-privilege thaw contract that old authenticated proof history remains immutable while only creation of a new proof key is granted.

## Required invariant

After cutoff, and also while the final writer's transaction-scoped thaw is active:

1. inserting a genuinely new proof key is permitted to the verified final writer;
2. inserting/replacing an already existing proof key is always denied;
3. UPDATE and DELETE of existing proof rows remain denied;
4. outside the thaw, all proof creation remains denied.

## Minimal fix design

Keep a permanent collision/no-replace `BEFORE INSERT` trigger for each proof table. It fires only when the incoming primary key already exists. The ordinary post-cutoff creation-deny trigger remains separate and is the only proof INSERT trigger removed during thaw.

Conceptually:

```sql
CREATE TRIGGER <proof>_existing_key_no_replace
BEFORE INSERT ON <proof_table>
WHEN EXISTS(SELECT 1 FROM provider_asymmetric_break_glass_boundary WHERE singleton=1)
 AND EXISTS(SELECT 1 FROM <proof_table> WHERE <key_column>=NEW.<key_column>)
BEGIN
  SELECT RAISE(ABORT,'LAB-086 existing proof key cannot be replaced');
END;
```

`remove_public_mutation_fence_locked()` must never remove this collision trigger. `assert_public_mutation_fence_locked()` must require it.

## Regression

`test_thaw_proof_replace_regression.py` is committed RED against the current runtime. It enters the same transaction-scoped thaw used by the final writer and requires, for both proof tables:

- `INSERT OR REPLACE` of the existing key => `sqlite3.IntegrityError` and original row unchanged;
- plain INSERT of a new key => succeeds during thaw.

## Scope

This is not the arbitrary same-privilege DDL threat already assigned to LAB-087. It is a defect in the capabilities intentionally granted by LAB-086's own thaw helper under normal SQLite conflict semantics, so it is a LAB-086 merge blocker.
