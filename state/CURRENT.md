# Current Lab State

Last updated: 2026-08-26

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085.
- Active priority: Issue #163 / LAB-086 — IN_PROGRESS.
- Branch: `lab/086-asymmetric-break-glass-history`.
- Draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Current observed PR HEAD: `d529167595efb1a6c1a480aeb32235be50183de1`.
- PR is mergeable but remains draft; full current-head real-ledger gate is not complete.
- Parallel LAB-087/#166 remains IN_PROGRESS; its exact authorizer/process/filesystem gate was previously 12/12 PASS.

## Last completed step

Built a fresh connector-reconstructed exact dependency closure for LAB-086 using the already proven LAB-080→085 implementations. Each executable dependency used in this run was verified locally with `git hash-object` against its GitHub blob.

Current PR implementation bytes reconstructed exactly:
- `migration_guard.py` `5a5bb928b39a96f93f019b103b483dfb9bf43c6d`;
- `strict_fence.py` `5da01e28a9f813a136d138637f855940f04aab46`;
- `suffix.py` `44847bde53b9f7b0e2fbcbab37d36dc992f497b2`;
- `final_supported.py` `ceb7f48a55a931ba9923cac77d4ebf6c4cd2cfec`.

Exact current `test_migration_guard.py` blob `38f482e1488dd0c8b36584ffb3d6d09812172898` executed against that exact closure: **11/11 PASS**.

The next exact regression exposed a stale test-harness assumption. Old `test_legacy_scrubbed_suffix.py` blob `4a4628fa...` called consequential `SupportedAsymmetricBreakGlassLedger.recover_rotation_authority_asymmetric()` directly after cutoff. The strengthened SQL fence correctly rejected root-authority INSERT because direct suffix mutation is intentionally unsupported; consequential mutation belongs to `SupportedFencedAsymmetricBreakGlassLedger`.

Only the regression was changed: post-cutoff restart/verification still uses the public-only suffix ledger, but the consequential asymmetric recovery is routed through `SupportedFencedAsymmetricBreakGlassLedger.from_existing(...)`. Branch commit `d529167595efb1a6c1a480aeb32235be50183de1`; new test blob `9951fb0b197cf79368ada21de8372f764ad2208e`.

The updated exact test was executed against exact current `final_supported.py`: **1/1 PASS**. `python -m compileall -q experiments/asymmetric_break_glass_history` also passed in the reconstructed workspace.

## Evidence produced / reconfirmed

- Exact LAB-086 migration guard integration: 11/11 PASS.
- Exact updated scrubbed-prefix → asymmetric-suffix/final-writer → restart regression: 1/1 PASS.
- Exact current LAB-086 implementation blobs listed above all matched GitHub.
- LAB-086 package compileall: PASS for the reconstructed current files.
- Cumulative exact lower-stack evidence remains: LAB-080 18/18, LAB-082 28/28, LAB-083 24/24, LAB-084 17/17, LAB-085 core 12/12, asymmetric-custody 8/8, public/final 11/11; lower unsafe baselines failed as intended.
- The stale regression failure was reproduced before the fix as `sqlite3.IntegrityError: LAB-086 root authority creation requires final supported writer`; this confirms the final-writer boundary is actually enforced.

## Known blockers / constraints

- Full current-head LAB-086 gate is still incomplete: remaining suffix/final-supported/security regression modules must be connector-reconstructed and executed, followed by unsafe legacy-promotion seed, full compileall and final audit.
- Do not weaken the runtime fence to satisfy old direct-suffix tests. Direct consequential mutation after cutoff is intentionally denied; tests must use the final fenced surface.
- Direct shell GitHub transport remains unavailable in this runtime; connector reconstruction works and is not an owner blocker.
- LAB-086 SQL fences cover audited supported/DML paths, not arbitrary same-privilege schema/DDL authority; LAB-087/#166 owns that boundary.
- LAB-088/#167 signer-noise, LAB-090/#169 provider handoff freshness, and LAB-091/#170 mutable shared-anchor/new-receipt authorization remain separate follow-ups.
- Logical SQL scrubbing is not forensic erasure; whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. Re-fetch PR #165 HEAD and reconstruct the remaining current-head LAB-086 tests from the same exact dependency closure; do not rerun already proven lower LAB-080→085 suites.
2. Execute remaining real-ledger suffix/final-supported/security modules: orphan/partial migration, full lower/public-history guards, public-rotation cross-binding/history, inherited/direct surfaces, rotation races, final single-snapshot verification, strict DML/fence regressions not already counted in this closure.
3. Run unsafe legacy-promotion seed and full compileall over the complete reconstructed closure.
4. Perform a fresh security audit of every consequential/restart path and re-check branch/main divergence. Fix every blocking failure before ready/merge.
5. Only after the complete current-head gate is clean, mark PR #165 ready and integrate; otherwise keep it draft with exact evidence and next action recorded.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; exact migration guard 11/11 and corrected scrubbed-suffix/final-writer 1/1 now PASS; remaining current-head real-ledger modules still required.
- #166 / LAB-087 — IN_PROGRESS; prior exact current slice 12/12 PASS.
- #167 / LAB-088 — READY; threshold signer-noise robustness.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — READY; mutable/shared-ledger plus new provider-receipt writer authorization.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
