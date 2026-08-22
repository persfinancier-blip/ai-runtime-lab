# Current Lab State

Last updated: 2026-08-23

## Active objective

LAB-083 — contain compromise of one current LAB-082 provider signing key by requiring an independent threshold quorum for every new asymmetric provider-generation transition.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-082.
- Active: Issue #157 / LAB-083 — IN_PROGRESS.
- Active branch: `lab/083-threshold-provider-rotation-v2` (the original branch was empty/stale and behind main).
- Active draft PR: #158 / `[LAB-083] Threshold-authorized asymmetric provider rotation`.
- Current PR HEAD: `dc5a1525cd0b24341bd40f461a937b4651eb3c00`.

## Last completed step

Built and published the first LAB-083 threshold rotation layer. A provider rotation now has a separately durable quorum proof bound to the exact old provider generation, proposed new generation, and threshold-authority identity/version/generation. Quorum proof persistence and LAB-082 provider-head advancement are designed to occur inside the same `BEGIN IMMEDIATE` transaction that already excludes unresolved PREPARED shared-anchor work.

A separate audit found that the first integration's legacy/new cutoff was merely SQL metadata and could be moved forward to skip required threshold proofs. That surface is retained as prototype evidence only. The audited supported surface is now `experiments/provider_threshold_rotation/supported.py`, where enablement is itself threshold-signed and bound to the exact provider head and exact rotation authority.

## Evidence produced

- New package: `experiments/provider_threshold_rotation/`.
- Research note: `research/2026-08-22-threshold-provider-rotation.md`.
- Isolated threshold/storage suite: 10/10 passed.
- Signed enablement/cutoff suite: 3/3 passed.
- Unsafe old+attacker-new baseline failed as expected because LAB-082-like old+new-only authorization accepts the compromise scenario.
- Compile/py_compile passed for the new package.
- Draft PR #158 is currently mergeable and intentionally remains draft.
- Direct `git clone` was probed in this runtime and failed before execution because `github.com` DNS resolution is unavailable; connector reconstruction remains the exact-source fallback.

## Known blockers / constraints

- No owner/product blocker.
- PR #158 is not ready to merge: the new `supported.py` has not yet been executed from exact published bytes against the merged LAB-082/LAB-080 dependency stack.
- The earlier `integration.py` has an unsigned cutoff and is explicitly not the supported LAB-083 surface.
- Historical pre-LAB-083 provider transitions remain legacy verification-only; they are not retroactively promoted to threshold-authorized transitions.
- Current quorum keys are a local reference mechanism, not HSM/KMS custody or distributed consensus.

## Exact next action

Reconstruct exact PR #158 HEAD bytes through the GitHub connector, including `supported.py`, `enablement.py`, protocol/tests and the exact merged LAB-082/LAB-080/LAB-036 dependencies. Verify Git blob identities before execution. Add/run real integration tests for: successful quorum-authorized provider rotation; compromised old+attacker-new without quorum; missing/duplicate/revoked/stale quorum; PREPARED reservation blocking rotation; threshold-authority rotation racing provider rotation; restart re-verification after proof corruption; threshold-signed cutoff tamper; and preservation of historical LAB-082 receipts/legacy transitions. Then run LAB-082/LAB-080 regressions plus compileall and perform a fresh remote patch audit. Only after a clean exact-source gate may PR #158 move from draft to ready/merge.

## Backlog

- #157 / LAB-083 — threshold-authorized asymmetric provider rotation — IN_PROGRESS.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
