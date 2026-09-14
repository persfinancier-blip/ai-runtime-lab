# LAB-086 — full lower-history guard for consequential writers

## Finding

The post-cutoff final writer was stronger than lower retained writers for LAB-086-specific root/recovery evidence, but it still had two cross-layer gaps:

1. `rotate_rotation_authority`, `rotate_provider`, and `rotate_public_recovery_authority` could begin from durable state whose LAB-080/082 shared-anchor/provider history was already corrupt. `_verify_lab086_locked()` does not replace the lower durable verifier. A new successor could therefore commit and the pre-existing corruption would only be surfaced by a later full restart.
2. A caller retaining the direct `SupportedAsymmetricBreakGlassLedger` could call `recover_rotation_authority_asymmetric()`. That method updates `provider_rotation_authority_head` before inserting its asymmetric proof, while the previous SQL fence did not cover that head update.

Neither path grants an attacker a valid cryptographic proof from invalid signatures. The failure mode is persistent fail-closed corruption/availability: consequential state can advance on top of a durable history that the complete supported verifier already considers invalid.

## Candidate fix

The final writer now acquires `BEGIN IMMEDIATE` before invoking the lower `SupportedAsymmetricHistoricalSharedAnchorLedger.verify_durable()` precondition. The separate lower read connection observes committed state while the outer transaction owns the single SQLite writer slot, so another writer cannot mutate that committed history between verification and the consequential transaction.

All final consequential writers then run LAB-086 verification before mutation. Provider generation rotation additionally runs `provider_history._verify_durable_locked(q)` after its uncommitted provider transition is written and before commit.

For asymmetric break-glass recovery, the cutoff SQL fence now denies `UPDATE provider_rotation_authority_head` to retained direct suffix writers. The final surface owns the supported asymmetric-recovery operation: verify lower history + LAB-086 history, verify the public quorum, transactionally remove the fence, write root head/proof, restore and assert the fence, re-verify LAB-086 history, commit.

## Executed focused evidence

Exact published bytes were reconstructed for the updated SQL fence. Existing strict/conflict tests, inherited-writer tests, and the new root-head fence tests passed 14/14; focused compileall passed. The real-stack lower-history/final-recovery regression is published but remains part of the pending full connector-reconstructed LAB-085/086 gate.

## Boundary

The SQL fence is protection against stale/alternate supported mutation paths, not against an arbitrary same-privilege process with unrestricted SQLite DDL authority. That broader schema-control boundary remains LAB-087 / Issue #166.
