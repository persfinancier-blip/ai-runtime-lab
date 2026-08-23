# Current Lab State

Last updated: 2026-08-23

## Active objective

LAB-085 — recovery-authority lifecycle, rotation, and asymmetric custody after completed LAB-084 break-glass recovery.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-084.
- Active: Issue #161 / LAB-085 — IN_PROGRESS.
- Branch: `lab/085-recovery-authority-lifecycle`.
- Draft PR: #162.
- Current PR HEAD: `6a348a3e7720b68cec09d913e3a73c3a7da65b7e`.
- Branch compare at this run: ahead 7 / behind 0; six LAB-085 paths are new relative to main.

## Last completed step

Observed that LAB-084 had already completed after the previous handoff: PR #160 is merged as `d91f981f330717ff0fb77103fe201da24a4bb600`, with its PR recording 87/87 corrected checks and a final recovery-head-substitution audit fix. Resumed the already-started LAB-085 branch, inspected its supported integration surface, and opened draft PR #162.

The LAB-085 branch currently implements a recovery-authority lifecycle requiring old-recovery quorum + new-recovery quorum + current normal/root quorum over one canonical transition. The supported layer serializes recovery-authority rotation with unresolved LAB-080 PREPARED work and advances the LAB-084 recovery head in the same SQLite transaction. Historical recovery generations are retained for verification windows; stale generations are rejected for new break-glass edges after their activation cutoff.

## Evidence produced

- LAB-084 PR #160: merged; merge commit `d91f981f330717ff0fb77103fe201da24a4bb600`.
- LAB-084 final PR evidence: 17/17 LAB-084, 24/24 LAB-083, 28/28 LAB-082, 18/18 LAB-080 = 87/87 corrected checks; compileall passed; unsafe self-recovery failed as expected.
- LAB-085 Issue #161 is IN_PROGRESS.
- LAB-085 draft PR #162 opened at HEAD `6a348a3e7720b68cec09d913e3a73c3a7da65b7e`.
- `experiments/provider_recovery_authority_lifecycle/supported.py` remote blob: `df4f17152cddefb66dc7f4e7f76f3112d3ab4733`.
- Fresh remote inspection confirms the supported surface uses one `BEGIN IMMEDIATE` for PREPARED rejection, current normal-root lookup, lifecycle rotation, LAB-084 recovery-authority insertion, and recovery-head CAS.
- No current exact-source test result is claimed for PR #162 in this run.

## Known blockers / constraints

- No owner/product blocker.
- PR #162 remains draft pending exact-source execution and regression/audit evidence.
- Current recovery keys are still symmetric reference material; asymmetric public-only historical custody/HSM-KMS modeling remains part of LAB-085 acceptance and must not be overstated as complete merely because lifecycle rotation exists.
- If both normal/root authorization and recovery lifecycle authorization are unavailable or compromised, fail closed; no recursive self-recovery.

## Exact next action

Resume PR #162 at HEAD `6a348a3e7720b68cec09d913e3a73c3a7da65b7e`. Reconstruct exact executable LAB-085 PR-head blobs plus merged LAB-084/083/082/080 dependencies through the GitHub connector into a local workspace and verify Git blob identities. Run LAB-085 `test_protocol` and `test_supported_integration`, LAB-084/083/082/080 regressions, the LAB-085 unsafe self-swap seed, and compileall. Fix any failure and rerun. Then perform a fresh full PR patch audit, with special attention to lifecycle-window cutoffs, root/recovery rotation races, durable historical proof verification, and whether asymmetric custody acceptance is actually satisfied. Only if clean should PR #162 be marked ready and merged; otherwise persist the blocker/fix and keep it draft.

## Backlog

- #161 / LAB-085 — recovery-authority lifecycle/rotation and asymmetric custody — IN_PROGRESS.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
