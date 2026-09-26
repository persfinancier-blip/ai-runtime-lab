# LAB-086 — pre-cutoff LAB-086 proof cardinality

## Finding

The migration guard already rejects unexplained lower LAB-082/LAB-083 root/provider/threshold evidence before signing the public-only cutoff. A fresh audit found the same reverse-cardinality requirement was not applied to LAB-086's own post-cutoff proof tables:

- `provider_asymmetric_break_glass_proofs`;
- `provider_asymmetric_recovery_public_root_proofs`.

`SupportedAsymmetricBreakGlassLedger` creates these schemas before any successful migration is required. Before the cutoff, the SQL mutation fence is intentionally inactive. Therefore an otherwise-authorized/raw SQL path can leave an orphan LAB-086 proof row before migration. The pre-cutoff LAB-085 verifier does not reference those tables, and `AuthenticatedBreakGlassMigrationGuard.verify_locked()` with no boundary only rejects orphan migration projection/root-proof singletons. Without an explicit reverse-cardinality check, `establish()` can sign/commit a cutoff while the unexplained LAB-086 proof row remains outside the migration projection. A later full LAB-086 verification/restart then fails closed.

This is a persistent correctness/availability defect, not privilege escalation. It is nevertheless a migration blocker because the purpose of the cutoff is to certify a complete, explainable pre-migration authority state.

## Required invariant

Immediately before producing or committing the cutoff, both LAB-086 post-cutoff proof tables must be empty. They have no legitimate pre-cutoff semantics. `provider_asymmetric_break_glass_proofs` may not exist yet during the earliest migration-guard constructor path, so absence of that table is equivalent to zero rows; if it exists, any row is unexplained evidence and must fail closed.

The new real-ledger regression `test_pre_cutoff_lab086_proof_cardinality.py` inserts one orphan row into each table before calling `migration_guard.payload()` and requires `MigrationGuardError`.

## Boundary

This does not replace LAB-087/LAB-091 writer authorization. It is a reverse-evidence completeness check at the irreversible migration boundary: even if pre-cutoff mutable SQL state was corrupted, LAB-086 must refuse to certify unexplained evidence.
