# LAB-086 — post-cutoff evidence DML immutability

## Finding

The current `strict_fence.py` treats `provider_asymmetric_break_glass_proofs` and `provider_asymmetric_recovery_public_root_proofs` as post-cutoff-only evidence for the pre-cutoff orphan check, but it does not install ordinary-DML immutability triggers for already committed rows in either table.

Both tables are authenticated restart evidence. A stale/raw ordinary-DML path can therefore UPDATE, DELETE, `INSERT OR REPLACE`, or UPSERT an existing proof after cutoff. The next verifier fails closed, but the malformed row is already durable, creating the same persistent fail-closed DoS class that LAB-086 already fences for root/provider/public transition history and migration metadata.

This does not grant a forged proof authority: cryptographic verification still rejects modified evidence. The blocker is durable-authority integrity/availability before restart.

## Regression

`test_post_cutoff_evidence_dml_fence.py` requires both existing evidence rows to reject UPDATE, DELETE, REPLACE, and UPSERT while preserving the original digest.

## Correct fence shape

New proof insertion must remain possible for the final supported writer, so the evidence tables should not receive an unconditional `BEFORE INSERT` deny trigger. Instead:

1. `BEFORE INSERT` after cutoff rejects only when a row with the same primary key already exists. This blocks `INSERT OR REPLACE` and UPSERT against committed evidence while allowing a new proof key.
2. `BEFORE UPDATE` after cutoff always rejects.
3. `BEFORE DELETE` after cutoff always rejects.
4. These evidence-history triggers are never removed by `remove_public_mutation_fence_locked()`. Final writers only need to insert a previously absent proof key.
5. `assert_public_mutation_fence_locked()` must require the six new triggers when the corresponding tables exist.

This remains an ordinary-DML guarantee only. Same-privilege schema/DDL authority remains LAB-087 / #166.
