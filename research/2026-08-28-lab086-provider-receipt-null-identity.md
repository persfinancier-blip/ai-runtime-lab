# LAB-086 — provider receipt NULL identity blocker

## Finding

Pinned executable snapshot: `05d8e75a636818afcb32e085d464c9fa9171dea5`.

LAB-082 creates `asymmetric_provider_receipts.request_id` as `TEXT PRIMARY KEY` without an explicit `NOT NULL`. In an ordinary SQLite rowid table this does not provide the domain invariant LAB-082's verifier assumes. The current LAB-086 receipt collision trigger also compares `request_id=NEW.request_id`, so a post-cutoff `NULL` request identity is not rejected by that trigger.

A focused SQLite reproduction using the exact table shape and current trigger predicate accepted multiple `NULL` request IDs. The staged predicate `NEW.request_id IS NULL OR EXISTS(... WHERE request_id IS NEW.request_id)` rejected the malformed identity while still allowing a genuinely new non-NULL request ID.

## Why this blocks LAB-086 merge

This is not only LAB-091 arbitrary-writer authorization. Exact pinned LAB-082 `IntegratedAsymmetricProviderHistory._verify_durable_locked()` enumerates every row from `asymmetric_provider_receipts`, constructs `SignedReceipt`, and verifies it. `SignedReceipt.validate()` requires `request_id`, `kind`, and `challenge` to be non-empty strings. Therefore a post-cutoff `NULL` receipt accepted by the current fence deterministically turns the next durable verification/restart into fail-closed failure.

Pre-cutoff malformed receipts do not create a separate migration escape: LAB-086 migration verifies inherited LAB-082 history before establishing the cutoff, so LAB-082 rejects the malformed receipt before migration can complete.

## Minimal fix

Keep new legitimate LAB-082 receipts appendable, but make the existing collision trigger enforce a canonical non-NULL identity and compare existing keys NULL-safely:

```sql
AND (
  NEW.request_id IS NULL
  OR EXISTS(
    SELECT 1 FROM asymmetric_provider_receipts
    WHERE request_id IS NEW.request_id
  )
)
```

The exact staged diff is saved in `research/2026-08-28-lab086-provider-receipt-null-identity.patch`.

## Regression

`experiments/asymmetric_break_glass_history/tests/test_provider_receipt_null_identity_regression.py` is committed RED against the current runtime. It requires post-cutoff `NULL request_id` insertion to fail while preserving insertion of a genuinely new non-NULL request ID.

## Evidence status

- current-predicate focused counterexample: NULL insert ALLOWED;
- staged-predicate focused check: NULL insert BLOCKED, distinct non-NULL insert ALLOWED;
- exact pinned LAB-082 source audit confirms every receipt is reverified on durable verification/restart and NULL request identity is invalid;
- runtime `strict_fence.py` is not yet modified in this note's commit; no post-fix exact-suite PASS is claimed.
