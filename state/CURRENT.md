# Current Lab State

Last updated: 2026-08-23

## Active objective

LAB-084 — prove separately authenticated break-glass recovery for the LAB-083 provider-rotation threshold authority while preserving LAB-080 serialization and historical verification.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-083.
- Active: Issue #159 / LAB-084 — IN_PROGRESS.
- Branch: `lab/084-provider-rotation-recovery`.
- Draft PR: #160.
- Current PR HEAD: `a8ae32c910f85c8ad003176c0a5c93dd069e56b9`.
- GitHub currently reports PR #160 mergeable; it remains draft pending exact-source execution.
- Follow-up: #161 / LAB-085 — recovery-authority lifecycle/rotation and asymmetric custody — READY after LAB-084.

## Last completed step

Added the missing concurrency/restart failure-injection surface directly to PR #160 as `experiments/provider_rotation_recovery/tests/test_concurrency.py`.

The new tests cover: (1) normal authority rotation racing break-glass recovery, requiring exactly one authority successor/proof edge; (2) provider rotation racing recovery, requiring SQL serialization such that any provider proof that commits under the predecessor authority remains historical evidence and cannot become a post-recovery use of the stale quorum; and (3) deletion of a committed recovery proof row causing restart verification to fail closed.

The new patch was inspected remotely. PR #160 changed from temporarily non-mergeable while GitHub recomputed status to mergeable after the commit. No merge was attempted because current supported/concurrency bytes have not yet been executed exact-source.

Direct shell GitHub access was probed again and still fails before checkout with `Could not resolve host: github.com`. This is an execution-surface limitation, not a repository/content blocker.

## Evidence produced

- PR #160 current HEAD: `a8ae32c910f85c8ad003176c0a5c93dd069e56b9`.
- New commit: `a8ae32c910f85c8ad003176c0a5c93dd069e56b9` (`LAB-084 add authority concurrency and restart proof regressions`).
- New test file remote patch audited: `experiments/provider_rotation_recovery/tests/test_concurrency.py`.
- Earlier LAB-084 reference suite: 9/9 passed; unsafe normal-quorum-self-recovery failed as expected.
- New supported/concurrency files are **not yet claimed as exact-source executed**.
- Issue #159 updated with the new gate/evidence.

## Known blockers / constraints

- No owner/product blocker.
- Exact-source execution of current PR #160 remains the only substantive merge gate.
- Direct shell GitHub checkout is unavailable in this runtime due DNS resolution failure; use GitHub connector reconstruction rather than fabricating a clone/test result.
- Branch is currently behind `main` by unrelated commits but all LAB-084 changed paths are new; do not use that fact to skip regression execution.
- Recovery authority remains deliberately pinned to bootstrap generation in LAB-084; lifecycle/rotation is #161.
- Current quorum keys are reference mechanisms, not HSM/KMS custody or distributed consensus.
- If both normal threshold authority and recovery quorum are simultaneously lost/compromised, fail closed; no recursive self-recovery.

## Exact next action

Resume PR #160 at HEAD `a8ae32c910f85c8ad003176c0a5c93dd069e56b9`. Reconstruct exact executable PR-head bytes plus merged LAB-083/082/080 dependencies through the GitHub connector into a local workspace and verify Git blob identities. Run LAB-084 `test_protocol`, `test_supported_integration`, and `test_concurrency`, LAB-083/082/080 regressions, the unsafe seed, and compileall. If any concurrency assumption fails, fix the implementation/test and rerun. Then perform a fresh full patch audit. If clean, mark PR #160 ready, squash-merge, close #159 DONE, and start #161 / LAB-085.

## Backlog

- #159 / LAB-084 — threshold provider-rotation authority recovery — IN_PROGRESS.
- #161 / LAB-085 — recovery-authority lifecycle/rotation and asymmetric custody — READY after #159.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
