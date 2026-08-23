# Current Lab State

Last updated: 2026-08-23

## Active objective

LAB-086 — migrate historical break-glass verification from durable symmetric/HMAC material to an explicit authenticated legacy cutoff plus Ed25519 public-only proof history, without auto-promoting legacy rows or weakening LAB-084/LAB-085 authority semantics.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085.
- Active: Issue #163 / LAB-086 — IN_PROGRESS.
- Active branch: `lab/086-asymmetric-break-glass-history`.
- Active draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Current PR #165 HEAD: `95799089beab8e2a67786e543de8bc2dcf016a47`.
- PR #165 is open, mergeable and intentionally draft.

## Last completed step

A fresh authority audit found a new cutoff-specific bypass in the current real-schema design. `migration_guard.verify_locked()` proved that the stored symmetric/public recovery authorities were historically bound, but it did not prove that this recovery generation was active at the cutoff root version. A retired recovery quorum could therefore re-sign a structurally valid migration boundary even though LAB-085 intends old public keys to be verification-only after recovery-authority rotation.

The branch now fixes this by resolving the existing LAB-085 recovery lifecycle activation/deactivation window for the boundary authority and requiring the exact cutoff root version to fall inside it. No second clock/authority mechanism was introduced.

A regression, `test_stale_historical_recovery_quorum_cannot_authorize_cutoff`, rotates the recovery/public authority and then manually inserts an otherwise correctly signed cutoff using the retired generation. Restart/verification must reject it.

## Evidence produced

- Security fix commit: `9ab79e04d4f5085e812cf7ea2776f1383046e479`.
- Regression/current PR HEAD: `95799089beab8e2a67786e543de8bc2dcf016a47`.
- Exact published `migration_guard.py` blob: `c1273de2c83fb806572e3467c8437bdf29155a4c`.
- Exact published `test_migration_guard.py` blob: `26ecc1ba95101d592c573f4098d3f27c4d39df36`.
- Fresh remote patch audit of both changed files found no additional blocker in the new lifecycle-window check.
- The exact `migration_guard.py` bytes were reconstructed locally; `git hash-object` matched `c1273de2c83fb806572e3467c8437bdf29155a4c` and `py_compile` passed.
- Focused execution of the exact method with interface-compatible lifecycle fixtures passed active, stale-at-deactivation, before-activation, later-active, and unknown-generation cases. This is supporting evidence only, not the full merge gate.
- Earlier standalone LAB-086 evidence remains 12/12 corrected tests + expected unsafe failure + compileall, but predates the current real-schema head and must not be reused as merge evidence.
- Direct runtime networking was probed again: DNS to `github.com`, `api.github.com`, public DNS servers and direct 1.1.1.1 connectivity are unavailable. GitHub connector access remains healthy. This is a runtime capability constraint, not an owner blocker.

## Known blockers / constraints

- The current PR head has not yet passed the complete exact-source LAB-086 + LAB-085/084/083/082/080 regression stack after the new cutoff-window fix.
- Direct shell GitHub networking is unavailable; exact reconstruction must continue through the GitHub connector unless network capability changes.
- PR #165 remains draft until exact-source regressions, unsafe seed, compileall and a fresh final full patch audit are actually observed.
- Whole-store rollback freshness remains delegated to the external monotonic-anchor layer.
- No live HSM/KMS was exercised; Ed25519 signer objects remain a reference interface.

## Exact next action

1. Re-fetch PR #165 and require unchanged HEAD `95799089beab8e2a67786e543de8bc2dcf016a47`; if it moved, restart the gate from the new HEAD.
2. Continue connector reconstruction of the exact merged dependency stack and verify every executable/test file with `git hash-object`.
3. Execute exact-source:
   - LAB-086 standalone reference tests;
   - LAB-086 migration-guard tests including stale historical recovery cutoff rejection;
   - LAB-086 asymmetric suffix tests;
   - LAB-085, LAB-084, LAB-083, LAB-082 and LAB-080 regression suites;
   - unsafe legacy auto-promotion seed;
   - `compileall` for the affected experiment tree.
4. Fix any failure and repeat.
5. Perform a fresh full remote patch audit. Only after a clean gate mark PR #165 ready, merge it, close Issue #163 DONE and choose the next highest-value unblocked correctness bottleneck.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; stale-cutoff authority bypass fixed, exact current-head regression/audit gate remains.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
