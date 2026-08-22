# Current Lab State

Last updated: 2026-08-23

## Active objective

LAB-084 — prove separately authenticated break-glass recovery for the LAB-083 provider-rotation threshold authority while preserving LAB-080 serialization and historical verification.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-083.
- Active: Issue #159 / LAB-084 — IN_PROGRESS.
- Branch: `lab/084-provider-rotation-recovery`.
- Draft PR: #160, created this run.
- Follow-up: #161 / LAB-085 — recovery-authority lifecycle/rotation and asymmetric custody — READY after LAB-084.

## Last completed step

Built and published the recovery-aware supported LAB-083 surface. `SupportedRecoveryThresholdProviderLedger` now serializes normal authority rotation and break-glass recovery against unresolved LAB-080 PREPARED work under `BEGIN IMMEDIATE`. Its restart verifier accepts mixed authority history only when every adjacent authority edge has exactly one proof type (normal old+new quorum XOR recovery quorum), requires exact authority name/version/generation continuity, rejects extra/orphan proof counts, and re-verifies historical provider threshold proofs under the exact historical authority.

A fresh audit found and fixed two defects before handoff: (1) the first mixed verifier did not globally reject extra/orphan authority proof rows or explicitly require contiguous authority version/generation; (2) on restart after a recovery edge, Python dynamic dispatch caused LAB-083's constructor to invoke the new verifier before the recovery controller existed, falling back to the normal-only verifier. LAB-084 now has an explicit non-escaping initialization window followed by mandatory full mixed verification before constructor return.

Focused supported integration regressions were added for recovery+restart, stale pre-recovery quorum rejection, PREPARED blocking of both normal rotation and recovery, and duplicate normal+recovery proof corruption. README was updated to distinguish the supported surface from the lower-level reference controller.

Recovery-authority lifecycle was intentionally split into #161 / LAB-085 so LAB-084 keeps a reviewable pinned-recovery-generation trust boundary rather than mixing a second lifecycle problem into this PR.

## Evidence produced

- Draft PR #160, current branch contains the original 9/9 reference slice plus the new supported integration surface/tests.
- Earlier LAB-084 reference suite: 9/9 passed; unsafe normal-quorum-self-recovery failed as expected.
- New supported files were audited in this run but **not yet claimed as exact-source executed**; full execution remains a merge gate.
- New follow-up #161 captures recovery-authority rotation, rollback protection, historical verification, and asymmetric/HSM-KMS custody.

## Known blockers / constraints

- No owner/product blocker.
- Exact-source execution of current PR #160 has not yet been completed in this runtime.
- Recovery authority is deliberately pinned to bootstrap generation in LAB-084; lifecycle/rotation is #161.
- Current quorum keys remain local reference mechanisms, not HSM/KMS custody or distributed consensus.
- If both normal threshold authority and recovery quorum are simultaneously lost/compromised, fail closed; no recursive self-recovery.

## Exact next action

Resume PR #160. Reconstruct exact executable PR-head bytes and merged LAB-083/082/080 dependencies through the GitHub connector into a local test workspace; verify Git blob identities; run LAB-084 `test_protocol` + `test_supported_integration`, LAB-083/082/080 regressions, unsafe seed, and compileall. Add and execute explicit concurrency regressions for normal-authority-rotation↔recovery and provider-rotation↔recovery plus restart missing/corrupted proof cases. Perform a fresh full patch audit. If no blocker remains, mark PR #160 ready, squash-merge, close #159 DONE, then start #161 / LAB-085.

## Backlog

- #159 / LAB-084 — threshold provider-rotation authority recovery — IN_PROGRESS.
- #161 / LAB-085 — recovery-authority lifecycle/rotation and asymmetric custody — READY after #159.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
