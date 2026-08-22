# Current Lab State

Last updated: 2026-08-22

## Active objective

LAB-078 — prove an authenticated migration checkpoint that moves pre-LAB-077 single-signature sink-registry history onto the threshold-publication surface without silently promoting legacy authority.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-077.
- Active: Issue #147 / LAB-078 — IN_PROGRESS.
- Active branch: `lab/078-authenticated-registry-migration`.
- Draft PR: #148 `[LAB-078] Authenticated legacy registry migration checkpoint`.
- Current PR HEAD: `64f9e0937a21a57961be248d036382b86c941f7e`.
- PR is mergeable and intentionally remains draft.

## Last completed step

A fresh full audit found that the lower-level idempotent `migrate()` path could return success for an already-present checkpoint by comparing stored SQL rows without reauthenticating the threshold proof and historical root. That made the retry path weaker than restart verification.

The supported authority-bearing surface was hardened in commit `64f9e0937a21a57961be248d036382b86c941f7e`: `SupportedMigrationCoordinator.migrate()` now runs the existing mixed-history verifier after both a fresh migration and an exact idempotent retry. Therefore supported success is reported only after stored checkpoint signatures, historical authority material, legacy-prefix binding, and post-migration threshold history are reverified.

No merge was attempted because the new supported-surface bytes have not yet passed the required exact-source regression stack.

## Evidence produced

- Prior reference LAB-078 slice: 10/10 passed; unsafe auto-promotion failed as expected; compileall passed in an earlier invocation.
- Prior real-schema integration suite: 8/8 passed in an earlier invocation.
- `integration.py` published blob: `69c74a8f24ac6de002b546023527bd13626ab8c1`.
- Hardened `supported.py` blob: `d770d1487e91b2bb3b4d78308b89e2dbf0626d8c`.
- Current PR #148 HEAD: `64f9e0937a21a57961be248d036382b86c941f7e`; 9 changed files; mergeable; draft.
- Direct GitHub checkout remains unavailable in the shell runtime due DNS; connector reconstruction is the supported exact-source fallback.

## Known blockers / constraints

- No owner/product blocker.
- PR #148 intentionally remains draft.
- New audit fix is not yet exact-source executed; older 10/10 and 8/8 results do not prove current HEAD.
- Direct GitHub clone/raw checkout is unavailable in this runtime due DNS; connector reconstruction is the allowed exact-source fallback.
- Pending `INTENT`/`UNKNOWN` must be resolved before migration; `CONFIRMED` is receipt-only history.
- Legacy LAB-076 rows remain verification-only and must never receive synthetic LAB-077 threshold proofs.
- Whole-store rollback/freshness remains delegated to LAB-034–037 external monotonic anchors.

## Exact next action

Reconstruct the exact executable bytes of PR #148 HEAD `64f9e0937a21a57961be248d036382b86c941f7e` plus merged LAB-077/076/075 dependencies/regressions through the GitHub connector. Verify every reconstructed executable file with `git hash-object` against its GitHub blob identity. Add/execute a regression proving that the supported idempotent retry path re-verifies stored migration proof/history rather than trusting row equality. Run LAB-078 reference, real-integration and supported/crash suites; run LAB-077, LAB-076 and LAB-075 regressions plus compileall; require the unsafe auto-promotion seed to fail as expected. Then perform a fresh full PR patch audit. Only if clean should PR #148 be moved ready, squash-merged, Issue #147 closed DONE, and the next highest-value gap selected.

## Backlog

- #147 / LAB-078 — authenticated migration checkpoint — IN_PROGRESS; draft PR #148; exact-source regression/final audit remains.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
