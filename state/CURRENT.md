# Current Lab State

Last updated: 2026-08-22

## Active objective

LAB-079 — compose the authenticated LAB-078 migration checkpoint with the existing LAB-034–037 external monotonic-anchor boundary so whole-store rollback cannot erase/rewind a completed migration, and prove that the exact checkpoint—not merely the same numeric counter position—was externally anchored.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-078.
- Active: Issue #149 / LAB-079 — IN_PROGRESS.
- Active branch: `lab/079-migration-anchor-binding`.
- Active draft PR: #150 `[LAB-079] Bind migration checkpoint to authenticated monotonic anchor`.
- Current PR HEAD: `ef853897f94aa644de02913258b21d6b8d5212f1`.

## Last completed step

Resumed PR #150 and audited the actual LAB-036 `AttestedCatchup` semantics. Found a cross-layer authority defect in the first LAB-079 supported surface: LAB-036 may return an authenticated READ when the external counter is already at the requested sequence. Therefore an unrelated operation could pre-advance the counter to N and LAB-079 would incorrectly mark migration N `CONFIRMED` without evidence that `migration-anchor:<sequence>:<checkpoint_id>` caused/owned that position.

Published a supported-surface fix requiring fresh authenticated provider reconciliation for the exact migration request ID before confirmation and again on restart. Focused execution immediately found a second defect in that first fix: LAB-036 `receipt_ref()` includes the fresh challenge, so the hash necessarily changes on every reauthentication and legitimate restart failed. Corrected this by persisting a stable digest of `(provider_id, generation, position, request_id)` only after verifying a fresh signed reconciliation observation. The digest is never treated as authentication by itself; restart must reauthenticate the external request result and then recompute/compare the stable binding.

A new regression file covers unrelated pre-existing anchor position, restart reauthentication, tampered local receipt, and timeout-after-commit exact-request recovery.

## Evidence produced

- Fix commit `e7a105810e04f2a1a3b69a59ace5abea67c69db8`: require exact request-specific reconciliation.
- Audit-fix commit / current PR HEAD `ef853897f94aa644de02913258b21d6b8d5212f1`: replace challenge-dependent receipt hash with stable authenticated request binding.
- New regression: `experiments/migration_anchor_binding/tests/test_supported_binding.py`.
- Current published `supported.py` Git blob: `8896a8b5d3dcf0a91e11f4063bcb27f6c38e3503`.
- Exact published `supported.py` was reconstructed locally and matched `git hash-object`.
- Focused request-binding execution: PASS after the stable-binding fix.
- The immediately prior focused execution failed on restart with `MigrationAnchorSubstitution`, reproducing the challenge-dependent receipt bug before it was corrected.
- Initial LAB-079 reference matrix remains 11/11; unsafe local-only rollback seed previously failed as expected; compileall previously passed for the initial package.
- PR #150 is open, mergeable, and intentionally draft.

## Known blockers / constraints

- No owner/product blocker.
- PR #150 is not merge-ready yet: the new current HEAD has not yet completed the full exact-source real integration/regression gate against the actual merged LAB-077/LAB-078 SQL stack.
- Direct shell GitHub DNS has historically been unavailable; GitHub connector reconstruction is the supported exact-source fallback.
- A numeric monotonic position alone is not checkpoint identity. Consequential migration requires request-specific authenticated provider evidence.
- A migration checkpoint that exists locally but lacks confirmed external binding is intentionally non-consequential.
- This model assumes the external provider preserves/reconciles stable request IDs durably; if a production anchor cannot do that, it cannot provide the stronger checkpoint-binding contract and must fail closed or use a content-aware anchor protocol.
- Do not conflate rollback detection with distributed consensus, backup durability, or a new anchor trust root.

## Exact next action

Close the remaining real-integration gate on current PR HEAD `ef853897f94aa644de02913258b21d6b8d5212f1`: reconstruct the exact merged LAB-077/LAB-078 dependency stack and LAB-036 AttestedCatchup through the GitHub connector, verify executable blobs with `git hash-object`, and run the supported composition against the actual SQLite journal. Required scenarios: real LAB-078 migration → exact-request anchor confirmation → restart; external counter already at the target position from an unrelated request must remain PENDING; restore a pre-migration SQLite snapshot while leaving the external provider ahead and require rollback detection; timeout-after-commit exact request reconciliation; tampered stored stable binding; provider/key-generation mismatch; anchor unavailable; first post-migration LAB-077 threshold successor followed by mixed-history + anchored restart verification. Then run LAB-079 + LAB-078 + LAB-077 + LAB-036 regressions and compileall, perform a fresh full PR patch audit, fix anything found, and only then mark PR #150 ready/merge.

## Backlog

- #149 / LAB-079 — migration checkpoint monotonic-anchor binding and rollback conformance — IN_PROGRESS.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
