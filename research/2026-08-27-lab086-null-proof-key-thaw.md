# LAB-086 NULL proof-key thaw bypass

Date: 2026-08-27

## Finding

The permanent post-cutoff proof collision trigger added after the thaw/`INSERT OR REPLACE` audit compares proof identity with SQL `=`:

```sql
EXISTS(SELECT 1 FROM proof_table WHERE key_column=NEW.key_column)
```

Both LAB-086 proof tables use ordinary SQLite rowid tables with `TEXT PRIMARY KEY` identity columns and no explicit `NOT NULL`:

- `provider_asymmetric_break_glass_proofs.new_rotation_authority_id`;
- `provider_asymmetric_recovery_public_root_proofs.new_public_authority_id`.

SQLite historically permits `NULL` in non-`INTEGER PRIMARY KEY` columns of ordinary rowid tables. `NULL = NULL` is not true, so the existing-key trigger does not identify an existing `NULL` key. During transaction-scoped proof-creation thaw, ordinary creation-deny triggers are intentionally removed. A direct `INSERT ... NULL` or `INSERT OR REPLACE ... NULL` can therefore create unexplained proof evidence that later verification rejects.

## Executed counterexample

A focused SQLite reproduction with `TEXT PRIMARY KEY` showed:

- first `NULL` key row accepted;
- `INSERT OR REPLACE` with another `NULL` key also accepted;
- two separate `NULL` identity rows remained durable in the table.

This is fail-closed durable-state damage / least-privilege-thaw bypass, not authority escalation.

## Required fix

The permanent collision trigger must both reject NULL identity and compare identity NULL-safely:

```sql
AND (
  NEW.key_column IS NULL
  OR EXISTS(SELECT 1 FROM proof_table WHERE key_column IS NEW.key_column)
)
```

This preserves legitimate creation of a new non-NULL proof key while denying:

- any NULL proof identity;
- `INSERT OR REPLACE` of an existing non-NULL identity;
- UPSERT-existing identity.

Focused SQLite execution of this condition confirmed:

- new NULL key: BLOCKED;
- new unique non-NULL key: ALLOWED;
- replace existing non-NULL key: BLOCKED.

## Regression

`experiments/asymmetric_break_glass_history/tests/test_thaw_null_proof_key_regression.py` is RED on the current runtime and covers both proof tables, including an out-of-band pre-existing NULL row followed by transaction-scoped thaw.

## Integration discipline

Do not hand-rewrite the ~872-line security-critical `strict_fence.py` without byte verification. Apply the minimal predicate change to the exact current blob, verify the resulting commit diff contains only the intended trigger predicate change, run the new regression together with thaw/strict-fence conflict-algorithm tests, then repin the LAB-086 executable snapshot before counting the full real-ledger gate.
