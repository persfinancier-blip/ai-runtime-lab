# LAB-086 — asymmetric break-glass history

LAB-086 migrates break-glass verification from legacy HMAC rows to an authenticated cutoff plus an Ed25519-only suffix on the existing LAB-084/LAB-085 SQLite authority.

Current draft layers:

- `protocol.py` — standalone reference semantics proving that legacy HMAC rows are never auto-promoted into asymmetric history.
- `migration_guard.py` — real-schema cutoff over the actual LAB-084/LAB-085 history. The cutoff commits the exact legacy HMAC/custody prefix and installs a SQL trigger that prevents any new HMAC break-glass row after migration.
- `suffix.py` — real-schema supported surface for post-cutoff Ed25519-only break-glass edges. New proofs bind the exact predecessor/successor root, migration boundary, symmetric recovery lifecycle identity and historically-bound public recovery authority. Root head advancement and proof persistence occur in one `BEGIN IMMEDIATE` transaction.

Historical recovery-generation authority is checked with LAB-085 lifecycle windows. Old Ed25519 public keys remain usable to verify historical proofs, but stale generations cannot authorize a new break-glass edge after recovery-authority rotation.

The final exact-source regression gate has not yet been executed for the current PR head. Do not treat the earlier standalone 12/12 result as evidence for the new real-schema suffix.

This is an HSM/KMS-compatible interface boundary; no live HSM/KMS is claimed.
