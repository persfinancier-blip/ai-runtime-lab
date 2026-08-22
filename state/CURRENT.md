# Current Lab State

Last updated: 2026-08-22

## Active objective

LAB-078 — prove an authenticated migration checkpoint that moves pre-LAB-077 single-signature sink-registry history onto the threshold-publication surface without silently promoting legacy authority.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-077.
- Active: Issue #147 / LAB-078 — IN_PROGRESS.
- Active branch: `lab/078-authenticated-registry-migration`.
- Draft PR: #148 `[LAB-078] Authenticated legacy registry migration checkpoint`.
- Current PR HEAD: `ad8584577d67cedceaddf5fe455c71f440eed880`.

## Last completed step

Extended the first isolated LAB-078 ceremony into a real-schema integration layer. `RealMigrationCoordinator` now operates directly on the existing LAB-076/LAB-077 SQLite tables, reads current/historical roots only through the LAB-076 lifecycle (`registry_authorities` + `_load_root()`), and stores only the migration checkpoint/proof — never a second authority head or synthetic threshold proofs for legacy rows.

The mixed-history verifier re-verifies the threshold-signed migration checkpoint against the historical LAB-076 root, re-verifies every legacy binding against its exact historical root, rejects any overlap between legacy rows and `registry_threshold_publications`, and delegates every post-migration threshold row to the LAB-077 historical threshold verifier. Registry heads must point into exactly one authenticated history class.

A local real-schema matrix passed 8/8: migration/restart, one-signer rejection, pending-state refusal, root-rotation race, legacy substitution, synthetic promotion, first threshold successor, and CONFIRMED receipt-only behavior. Direct `git clone` was probed again and still fails because `github.com` DNS does not resolve in this runtime.

A fresh remote patch audit identified the next supported-surface gap: the coordinator currently duck-types its registry object. Before merge, migration authority must be exposed only through an exact-type-gated composition with the final audited LAB-077 journal, following the same anti-subclass/anti-prototype pattern established in LAB-075–077.

## Evidence produced

- Existing reference LAB-078 slice: corrected 10/10; unsafe auto-promotion failed as expected; compileall passed.
- New `experiments/sink_registry_migration_checkpoint/integration.py`.
- New `experiments/sink_registry_migration_checkpoint/tests/test_real_integration.py`.
- Local real-schema integration suite: **8/8 passed**.
- Published integration Git blob: `69c74a8f24ac6de002b546023527bd13626ab8c1`.
- PR #148 remains open, draft, mergeable at HEAD `ad8584577d67cedceaddf5fe455c71f440eed880`.

## Known blockers / constraints

- No owner/product blocker.
- PR #148 intentionally remains draft.
- `RealMigrationCoordinator` is not yet the supported surface because it accepts duck-typed registry objects.
- The 8/8 integration run used the exact real SQL table layout with a compact verifier double; it is not yet the required exact-source regression against the full merged LAB-077/076/075 module graph.
- Direct GitHub clone/raw checkout is unavailable in this runtime due DNS; connector reconstruction is the allowed exact-source fallback.
- Pending `INTENT`/`UNKNOWN` must be resolved before migration; `CONFIRMED` is receipt-only history.
- Legacy LAB-076 rows remain verification-only and must never receive synthetic LAB-077 threshold proofs.
- Whole-store rollback/freshness remains delegated to LAB-034–037 external monotonic anchors.

## Exact next action

Add `experiments/sink_registry_migration_checkpoint/supported.py` (or equivalent) that requires the exact final audited LAB-077 `ThresholdLifecycleRegistryBoundJournal` type and exposes migration/verification only through that composition; reject subclasses/prototype journals. Add a regression proving a duck-typed/unaudited registry cannot become migration authority. Then reconstruct the exact PR #148 executable bytes plus the merged LAB-077/076/075 dependency/test files through the GitHub connector, verify Git blob identities, run LAB-078 reference + real-integration + supported-surface tests and LAB-077/076/075 regressions plus compileall. Add explicit partial-migration/crash and restart-after-real-threshold-suffix tests. Perform a fresh full remote patch audit; only if clean move PR #148 to ready and merge.

## Backlog

- #147 / LAB-078 — authenticated migration checkpoint — IN_PROGRESS; draft PR #148.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
