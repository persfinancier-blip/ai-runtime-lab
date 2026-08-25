# Current Lab State

Last updated: 2026-08-25

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085.
- Active: Issue #163 / LAB-086 — IN_PROGRESS.
- Branch: `lab/086-asymmetric-break-glass-history`.
- Draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Current observed PR HEAD: `46e187b35776f4c7ac2999e17f321da9e02d127e`.
- PR is open/draft/mergeable; the new migration-guard fix must pass the real-ledger current-head gate before merge.

## Last completed step

A fresh migration-boundary audit found and fixed a partial-state integrity bug after the previously clean lower/fence/final-snapshot slices.

`AuthenticatedBreakGlassMigrationGuard.verify_locked()` previously loaded the boundary and root proof, rejected `root proof present + boundary absent`, but did not load/check the legacy projection until after a boundary existed. Therefore `projection present + boundary absent` was silently classified as clean pre-cutoff state. Such a projection cannot result from a successful atomic migration; if retained, a later `establish()` collides with the existing singleton and creates a persistent fail-closed migration DoS.

The branch now loads the projection before the no-boundary branch and rejects `projection present + boundary absent` with `MigrationGuardError('orphan migration legacy projection')`.

Published branch changes:
- code fix commit `3772606096267ad37fbd462e767f5c17cb1d1496`;
- `migration_guard.py` new Git blob `5a5bb928b39a96f93f019b103b483dfb9bf43c6d`;
- regression commit/current HEAD `46e187b35776f4c7ac2999e17f321da9e02d127e`;
- new `test_orphan_projection_regression.py` Git blob `f20a1d717872931da8d7fecdbf2778cb8bb7c540`.

Executed focused SQLite counterexample: the pre-fix branch logic returned `None` (accepted as pre-cutoff) for projection-only state; the patched condition rejected the same state with `orphan migration legacy projection`. The real-ledger regression is published but has not yet executed in the complete dependency closure, so PR #165 remains draft.

Earlier in this same verification cycle, exact current-head `final_supported.py` blob `9f0198d2db85d08ec64f614d6288323c1d642383` and exact `test_final_verification_snapshot.py` blob `0426dcfe61bef665bcbc5c21b937d805f223da64` were executed together; the final single-snapshot contract passed **1/1**.

## Evidence produced / reconfirmed

- Lower-stack exact gate is complete:
  - LAB-080 18/18 PASS.
  - LAB-082 28/28 PASS.
  - LAB-083 24/24 PASS.
  - LAB-084 17/17 PASS.
  - LAB-085 core 12/12 PASS.
  - LAB-085 asymmetric-custody 8/8 PASS.
  - LAB-085 public/final 11/11 PASS.
  - Lower unsafe baselines failed as expected; compileall passed on reconstructed layers.
- Pre-fix/current-earlier LAB-086 exact fence subgate: **17/17 PASS** + compileall PASS; `strict_fence.py` has not changed in the orphan-projection fix.
- Current final single-snapshot contract: **1/1 PASS** using exact `final_supported.py` and exact test bytes.
- Current migration-guard orphan projection fix: focused semantic counterexample changed from ACCEPT (`None`) to fail-closed rejection; full real-ledger regression pending.
- Current PR #165 implementation identities after fix:
  - `migration_guard.py` `5a5bb928b39a96f93f019b103b483dfb9bf43c6d`.
  - `final_supported.py` remains `9f0198d2db85d08ec64f614d6288323c1d642383`.
  - `protocol.py` remains `cccb531fa13b8f8d4e3a7c3163dd7c7cbeb3ec41`.
  - `strict_fence.py` remains `62a9b602edb8692894cad3874ba6d5c211129aa5`.
  - `suffix.py` remains `bb9f8e55fb03424ac19c152ae2d8aceaf2e1c078`.
  - new orphan regression `f20a1d717872931da8d7fecdbf2778cb8bb7c540`.
- Exact standalone LAB-086 corrected suite previously passed 12/12; unsafe legacy-auto-promotion seed failed as intended.
- Re-check branch/main divergence immediately before integration; prior compare was ahead 96 / behind 47 before the two new branch commits.
- LAB-089/#168 is CLOSED `not_planned`; do not treat it as active backlog.

## Known blockers / constraints

- The new orphan-projection regression has not yet run against the real LAB-085/LAB-086 ledger closure; this is now part of the remaining merge gate.
- Remaining LAB-086 merge gate is the current-head migration/suffix real-schema tests and remaining final-supported integration/history-guard tests, unsafe legacy-promotion seed, full compileall over the complete closure, and one final security audit.
- Direct shell GitHub transport is unavailable; connector reconstruction works and is not an owner-level blocker.
- The final single-snapshot 1/1 test uses exact branch implementation/test bytes but import-only stubs for lower modules by design of that isolated test; lower real implementations are separately covered by the completed LAB-080–085 gate.
- LAB-083/LAB-084 signer-noise issue #167 remains fail-closed DoS/robustness and separate from LAB-086 unless downstream tests invalidate the candidate.
- LAB-086 SQLite fences cover stale/alternate supported mutation paths and audited DML, not arbitrary same-privilege raw SQLite DDL/schema control; that broader boundary is LAB-087/#166.
- Logical SQL scrubbing is not forensic erasure. Whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. Reconstruct current PR #165 HEAD `46e187b35776f4c7ac2999e17f321da9e02d127e` migration/suffix dependency closure and execute `test_orphan_projection_regression.py` first against the real supported ledger.
2. Execute the complete current-head migration v4 root-coauthorization/restart, scrubbed-prefix/asymmetric-suffix, forged-proof/stale-writer/direct-surface, full lower/public history guards and rotation-race tests. The strict/inherited/root-head fence slice and final single-snapshot contract need not be repeated unless their dependencies change.
3. Execute unsafe legacy-promotion expected-failure seed and full compileall over the complete closure.
4. Perform a fresh full security audit of every consequential/restart writer plus branch/main divergence. Fix every failure before changing PR #165 out of draft.
5. If the full gate is clean, mark PR #165 ready and integrate by normal merge when available; otherwise use only the documented audited file-scoped Contents API fallback after exact conflict checking.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; new orphan-projection partial-state blocker fixed in branch, real-ledger regression pending.
- #166 / LAB-087 — READY; SQLite schema-control trust boundary.
- #167 / LAB-088 — READY; threshold signer-noise robustness.
- #168 / LAB-089 — CLOSED `not_planned`.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
