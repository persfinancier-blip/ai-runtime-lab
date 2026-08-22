# Current Lab State

Last updated: 2026-08-22

## Active objective

LAB-078 — prove an authenticated migration checkpoint that moves pre-LAB-077 single-signature sink-registry history onto the threshold-publication surface without silently promoting legacy authority.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-077.
- Active: Issue #147 / LAB-078 — IN_PROGRESS.
- Active branch: `lab/078-authenticated-registry-migration`.
- Draft PR: #148 `[LAB-078] Authenticated legacy registry migration checkpoint`.
- Current PR HEAD: `04ab5f0f3bea989036d0fc46da425560aecf7d28`.
- PR is currently mergeable but remains intentionally draft.

## Last completed step

Closed the supported-surface gap identified by the previous audit. `experiments/sink_registry_migration_checkpoint/supported.py` now exposes `SupportedMigrationCoordinator`, which accepts only the exact final audited LAB-077 `ThresholdLifecycleRegistryBoundJournal` type. Subclasses, duck-typed registries and prototype journals are rejected before migration setup; the lower-level `RealMigrationCoordinator` remains available only for regression/audit work.

Published additional failure-injection regressions in `tests/test_supported_and_crash.py`: exact final LAB-077 journal acceptance, subclass/duck rejection, an SQLite abort on migration-checkpoint INSERT that must leave zero partial migration rows and permit later clean retry, and restart verification after the first threshold-authenticated successor.

A fresh remote patch review of the new supported/crash files found no supported-surface or transaction-boundary defect. Direct `git ls-remote`/clone was re-probed and still fails because `github.com` DNS does not resolve in the runtime, so the new PR HEAD has not yet been claimed as exact-source executed.

## Evidence produced

- Existing reference LAB-078 slice: corrected 10/10; unsafe auto-promotion failed as expected; compileall passed in an earlier invocation.
- Existing real-schema integration suite: 8/8 passed in an earlier invocation.
- `integration.py` published blob remains `69c74a8f24ac6de002b546023527bd13626ab8c1`.
- Added exact-type supported surface in commit `11d21fbcf0d5811f71c64d1ba0409c589ffc3c1c`.
- Added supported/crash/restart regression file in commit `04ab5f0f3bea989036d0fc46da425560aecf7d28`.
- Current PR #148 HEAD: `04ab5f0f3bea989036d0fc46da425560aecf7d28`; 9 changed files; mergeable; draft.
- Remote per-file audit of the two newly added files completed without a blocking finding.
- Direct GitHub checkout probe: failed before execution evidence because DNS cannot resolve `github.com`; connector reconstruction remains the supported exact-source fallback.

## Known blockers / constraints

- No owner/product blocker.
- PR #148 intentionally remains draft.
- The prior duck-typed coordinator is no longer the supported authority-bearing surface; exact-type supported composition is now present.
- The new supported/crash/restart tests are published but have not yet been executed as the exact current PR HEAD; do not count older 10/10 or 8/8 results as proof for these new bytes.
- Direct GitHub clone/raw checkout is unavailable in this runtime due DNS; connector reconstruction is the allowed exact-source fallback.
- Pending `INTENT`/`UNKNOWN` must be resolved before migration; `CONFIRMED` is receipt-only history.
- Legacy LAB-076 rows remain verification-only and must never receive synthetic LAB-077 threshold proofs.
- Whole-store rollback/freshness remains delegated to LAB-034–037 external monotonic anchors.

## Exact next action

Reconstruct the exact executable bytes of PR #148 HEAD `04ab5f0f3bea989036d0fc46da425560aecf7d28` plus the merged LAB-077/076/075 dependency and regression files through the GitHub connector. Verify each reconstructed file with `git hash-object` against its GitHub blob identity. Run LAB-078 reference, real-integration and supported/crash suites; run LAB-077, LAB-076 and LAB-075 regressions plus compileall; also run the unsafe auto-promotion seed and require its expected failure. If all exact-source tests pass, perform one fresh full PR patch audit. Only if that audit is clean should PR #148 be moved from draft to ready, squash-merged, Issue #147 closed DONE, and the next highest-value gap selected.

## Backlog

- #147 / LAB-078 — authenticated migration checkpoint — IN_PROGRESS; draft PR #148; exact-source regression/final audit remains.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
