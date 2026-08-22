# Current Lab State

Last updated: 2026-08-23

## Active objective

LAB-083 — contain compromise of one current LAB-082 provider signing key by requiring an independent threshold quorum for every new asymmetric provider-generation transition.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-082.
- Active: Issue #157 / LAB-083 — IN_PROGRESS.
- Active branch: `lab/083-threshold-provider-rotation-v2`.
- Active draft PR: #158 / `[LAB-083] Threshold-authorized asymmetric provider rotation`.
- Current PR HEAD: `b55051ab781efa282fd34a94ebe8a78dad0030ef`.
- PR #158 is currently mergeable and intentionally remains draft.

## Last completed step

Built and published the first threshold-authorized LAB-083 provider-rotation layer. Provider rotation now stores a separately durable quorum proof bound to the exact old provider generation, proposed new generation, and threshold-authority identity/version/generation, inside the same `BEGIN IMMEDIATE` transaction that advances the LAB-082 provider head and excludes unresolved PREPARED shared-anchor work.

Two audit findings were fixed before integration:
1. The first prototype's legacy/new cutoff was ordinary SQL metadata. Moving it could skip required threshold proofs. The supported surface now uses a threshold-signed `ThresholdEnablement` bound to the exact provider generation and exact threshold authority.
2. If the enablement row were deleted after threshold-governed transitions already existed, a constructor could otherwise attempt to create a new cutoff at the later head. The supported surface now refuses rebootstrap when any threshold proof already exists.

The earlier `integration.py` is retained only as prototype/audit evidence. `supported.py` is the fail-closed LAB-083 surface.

## Evidence produced

- New package: `experiments/provider_threshold_rotation/`.
- Research note: `research/2026-08-22-threshold-provider-rotation.md`.
- Isolated threshold/storage suite: 10/10 passed.
- Signed enablement/cutoff suite: 3/3 passed.
- Unsafe old+attacker-new baseline failed as expected because LAB-082-like old+new-only authorization accepts the compromise scenario.
- Compile/py_compile passed for the new package.
- Draft PR #158 opened from current `main`; nine changed paths are additions only.
- Direct `git clone` was probed and failed before execution because this runtime cannot resolve `github.com`; connector reconstruction remains the required exact-source fallback.
- An attempted Issue #157 metadata refresh after the second audit fix was blocked before execution by an external safety-status gate; repository `state/CURRENT.md` remains authoritative for this handoff.

## Known blockers / constraints

- No owner/product blocker.
- PR #158 is not ready to merge: exact published `supported.py` has not yet been executed against merged LAB-082/LAB-080/LAB-036.
- Historical pre-LAB-083 provider transitions remain legacy verification-only; they are not retroactively promoted to threshold-authorized transitions.
- Strict type/canonical-encoding regressions for enablement/authority records are still required (including Python `bool == 1` style aliases).
- The current reference threshold authority implements normal old+new quorum rotation but not yet an explicit break-glass recovery path; LAB-083 must either reuse an existing lab recovery authority or record a deliberate non-goal before DONE.
- Current quorum keys are a local reference mechanism, not HSM/KMS custody or distributed consensus.

## Exact next action

Reconstruct exact PR #158 HEAD bytes through the GitHub connector, including `supported.py`, `enablement.py`, protocol/tests and exact merged LAB-082/LAB-080/LAB-036 dependencies. Verify Git blob identities before execution. Add/run real integration tests for: successful quorum-authorized provider rotation; compromised old+attacker-new without quorum; missing/duplicate/revoked/stale quorum; PREPARED reservation blocking rotation; threshold-authority rotation racing provider rotation; restart proof corruption; signed-enablement deletion/tamper; strict type/canonical encodings; and preservation of historical LAB-082 receipts/legacy transitions. Reuse an existing threshold recovery authority if practical rather than inventing another one. Then run LAB-082/LAB-080 regressions plus compileall and perform a fresh remote patch audit. Only after a clean exact-source gate may PR #158 move from draft to ready/merge.

## Backlog

- #157 / LAB-083 — threshold-authorized asymmetric provider rotation — IN_PROGRESS.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
