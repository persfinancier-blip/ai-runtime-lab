# Current Lab State

Last updated: 2026-08-23

## Active objective

LAB-085 — recovery-authority lifecycle and asymmetric custody. The HMAC-only new break-glass bypass found in the prior audit is fixed on the final supported surface; keep PR #162 draft until the exact-source regression stack and one fresh final audit pass.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-084.
- Active: Issue #161 / LAB-085 — IN_PROGRESS.
- Branch: `lab/085-recovery-authority-lifecycle`.
- Draft PR: #162 — open and mergeable; current observed HEAD `e6b0b09b5d2734a2a2d4fbe36437d67772a4e756`.
- Follow-up: Issue #163 / LAB-086 — migrate historical pre-cutoff LAB-084 HMAC break-glass proof history to asymmetric/public-only verification after LAB-085.

## Last completed step

Resumed from the final-audit blocker that showed `SupportedRecoveryCustodyLedger` still inherited LAB-084 `recover_rotation_authority()` and therefore allowed a **new** normal/root break-glass recovery with only the symmetric HMAC recovery quorum.

The branch now blocks that inherited HMAC-only entry point on the final surface and adds `recover_rotation_authority_with_custody()`. A new break-glass recovery after final-custody enablement must satisfy both proof families in one `BEGIN IMMEDIATE` transaction:

1. current Ed25519 public recovery quorum over a canonical custody intent; and
2. the LAB-084 compatibility HMAC quorum over the exact legacy recovery intent.

The Ed25519 intent binds old/new rotation authority, exact public recovery authority, exact symmetric compatibility recovery authority, and the exact LAB-084 compatibility intent digest. The SQL transaction commits the legacy LAB-084 proof row, a new public custody proof row, and rotation-authority head advancement atomically.

A durable custody-enablement row records the root/public/symmetric identities at activation. Restart verification requires a public custody proof for every recovery edge whose predecessor root version is at/after the cutoff, while pre-existing LAB-084 edges remain verification-only compatibility history for LAB-086.

New regressions cover HMAC-only rejection, public-only failure with zero partial proof rows, dual-proof commit + restart, missing public proof detection, and recovery-vs-custody-rotation serialization.

During the fix, an additional transaction-boundary defect was found before test execution: the first implementation used `sqlite3.executescript()` while already holding `BEGIN IMMEDIATE`, which can interfere with the intended transaction boundary in Python. The published code now uses individual DDL statements inside the caller transaction.

## Evidence produced

- PR #162 current observed HEAD: `e6b0b09b5d2734a2a2d4fbe36437d67772a4e756`; 14 LAB-085 files; GitHub reports mergeable and draft.
- New custody break-glass helper: `experiments/provider_recovery_authority_lifecycle/custody_break_glass.py`, Git blob `ecd106185be3eda2c45f53d444e3267dd77f9fdc`.
- New regression suite: `experiments/provider_recovery_authority_lifecycle/tests/test_custody_break_glass.py`, Git blob `24deb6dcc20f35f04723d187e7c00a812e7f64cc`.
- Current `final_supported.py` Git blob: `23567c66342e10ba7bb79e0a2751c0bc9cef2b98`.
- Helper and regression bytes were locally matched with `git hash-object` and syntax-compiled; the corrected local final implementation was syntax-compiled before publication.
- Remote patch audit of the new helper, final supported layer, and regressions found no new structural authorization bypass after the `executescript` fix.
- Direct `git clone --branch lab/085-recovery-authority-lifecycle ...` was probed again in this runtime and failed before checkout with `Could not resolve host: github.com`.
- No full exact-source LAB-085/LAB-084/083/082/080 test run is claimed for the current HEAD.

## Known blockers / constraints

- No owner/product blocker.
- PR #162 must remain draft until exact-source execution.
- The authorization blocker from the previous run is fixed in code, but the current integrated HEAD has not yet passed the required exact-source regression stack.
- Historical LAB-084 break-glass proofs created before the final-custody cutoff remain HMAC-based compatibility history; Issue #163 / LAB-086 owns their asymmetric migration. This does not authorize HMAC-only **new** effects on `SupportedRecoveryCustodyLedger`.
- Direct shell GitHub access remains unavailable in this runtime due DNS; connector reconstruction remains the safe supported fallback.

## Exact next action

Reconstruct the exact current PR #162 executable bytes through the GitHub connector, including all LAB-085 files and the merged LAB-084/083/082/080 dependencies required by the regression stack. Verify every reconstructed executable file with `git hash-object` against its GitHub blob ID. Execute:

- all LAB-085 suites, including the new `test_custody_break_glass`;
- LAB-084, LAB-083, LAB-082, and LAB-080 regression suites required by the PR gate;
- the LAB-085 unsafe seed and compileall.

If any new failure appears, fix it and repeat. Then perform one fresh full PR #162 patch audit, re-fetch PR metadata/HEAD, and only if the exact-source run and audit are clean mark the PR ready, squash-merge it, close Issue #161 DONE, and advance to Issue #163 / LAB-086.

## Backlog

- #161 / LAB-085 — recovery-authority lifecycle + asymmetric custody — IN_PROGRESS; code-level HMAC-only new-effect bypass fixed, exact-source regression/final-audit gate remains.
- #163 / LAB-086 — asymmetric migration of historical pre-cutoff LAB-084 break-glass proofs — READY after LAB-085.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
