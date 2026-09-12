# LAB-086 — asymmetric break-glass history

LAB-086 migrates break-glass verification from legacy HMAC recovery authority to an authenticated cutoff plus a public-only Ed25519 recovery suffix on the existing LAB-084/LAB-085 SQLite authority.

Current draft layers:

- `protocol.py` — standalone reference semantics proving that legacy HMAC rows are never auto-promoted into asymmetric history.
- `migration_guard.py` — real-schema cutoff over the actual LAB-084/LAB-085 history. Immediately before the cutoff is signed, the complete legacy compatibility history is re-verified. The cutoff stores a canonical non-secret projection of the verified legacy recovery semantics and recovery-generation windows. Boundary insertion, projection persistence and scrubbing of durable recovery HMAC key maps / recovery-HMAC proof bytes occur in one `BEGIN IMMEDIATE` transaction.
- `suffix.py` — post-cutoff restart no longer constructs LAB-084/LAB-085 symmetric recovery controllers. It loads LAB-083 root/provider state, Ed25519 public recovery history and the signed LAB-086 projection. New break-glass root edges are Ed25519-threshold authorized.
- post-cutoff recovery-authority rotation is also public-only: old-public + new-public Ed25519 thresholds authorize the public successor and the current normal/root threshold co-authorizes the same canonical transition. Historical public keys remain verification-only after rotation.
- persistent SQL triggers prevent old LAB-085 writers from appending new HMAC recovery/lifecycle state after migration.

The main acceptance test now restarts the LAB-086 surface with `recovery_authority=None` after verifying that `provider_rotation_recovery_authorities.keys_json` and `provider_recovery_lifecycle_authorities.keys_json` are canonical `{}`, and that historical recovery/lifecycle MAC proof fields are canonical `[]`.

This is logical durable-state scrubbing, **not forensic erasure**: SQLite/WAL/filesystem remnants are outside this experiment's guarantee. No live HSM/KMS is claimed.

## Evidence gate

The public-only real-schema rewrite is newer than the previous standalone 12/12 evidence. It must not be marked DONE until the exact current PR head is executed against LAB-086 plus LAB-085/084/083/082/080 regressions, unsafe seed and compileall, followed by a fresh patch audit.

Whole-store rollback freshness remains delegated to the external monotonic-anchor work.
