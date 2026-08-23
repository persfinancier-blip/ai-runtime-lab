# LAB-086 — asymmetric break-glass history

LAB-086 migrates break-glass verification from legacy HMAC recovery proofs to an authenticated cutoff plus an Ed25519-only suffix on the existing LAB-084/LAB-085 SQLite authority.

Current draft layers:

- `protocol.py` — standalone reference semantics proving that legacy HMAC rows are never auto-promoted into asymmetric history.
- `migration_guard.py` — real-schema cutoff over the actual LAB-084/LAB-085 history. Immediately before the cutoff is signed, the complete legacy compatibility history is re-verified. The signed cutoff then commits a canonical semantic projection of the legacy recovery edges plus their public-custody evidence, while deliberately excluding the HMAC proof bytes. Boundary insertion and replacement of legacy `signatures_json` with canonical `[]` happen in one `BEGIN IMMEDIATE` transaction.
- `suffix.py` — real-schema supported surface for post-cutoff Ed25519-only break-glass edges. New proofs bind the exact predecessor/successor root, migration boundary and historically-authorized public recovery generation. Root head advancement and proof persistence occur in one `BEGIN IMMEDIATE` transaction.
- the persistent SQL trigger prevents any new HMAC break-glass row after migration; the post-cutoff verifier additionally rejects reintroduced legacy HMAC proof bytes.

Historical HMAC proof bytes are therefore no longer required after a successful cutoff. The signed boundary commits the exact legacy edge identities that were fully verified immediately before migration, while LAB-085 public-custody proofs remain independently Ed25519-verifiable where public custody was enabled.

## Remaining acceptance gap

The current branch is **not yet fully public-only recovery history**. LAB-084/LAB-085 still persist symmetric recovery key maps in `provider_rotation_recovery_authorities` / `provider_recovery_lifecycle_authorities`, and the current lifecycle/window helpers still load those symmetric authorities. Removing MAC proof bytes is useful but is not equivalent to removing durable symmetric signing material.

Before LAB-086 can be marked DONE, the real supported post-cutoff verifier must stop depending on those HMAC key maps (using an authenticated public/cutoff projection for historical recovery identity/windows instead), and a regression must prove restart/verification after the obsolete symmetric recovery signing material is scrubbed. Do not claim public-only historical recovery until that test passes.

The final exact-source regression gate has not yet been executed for the current PR head. Earlier standalone results are historical evidence only and do not cover the new proof-scrubbing changes.

This is an HSM/KMS-compatible interface boundary; no live HSM/KMS is claimed. Whole-store rollback freshness remains delegated to the external monotonic-anchor work.
