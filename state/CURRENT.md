# Current Lab State

Last updated: 2026-08-23

## Active objective

LAB-083 — contain compromise of one current LAB-082 provider signing key by requiring an independent threshold quorum for every new asymmetric provider-generation transition.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-082.
- Active: Issue #157 / LAB-083 — IN_PROGRESS.
- Active branch: `lab/083-threshold-provider-rotation-v2`.
- Active draft PR: #158 / `[LAB-083] Threshold-authorized asymmetric provider rotation`.
- Current PR HEAD: `9d8bd132d891a47a0f92b2cf2e9291a5380ba360`.
- PR #158 is mergeable and intentionally remains draft.

## Last completed step

Built and published the first threshold-authorized LAB-083 provider-rotation layer. Provider rotation stores a separately durable quorum proof bound to the exact old provider generation, proposed new generation, and threshold-authority identity/version/generation inside the same `BEGIN IMMEDIATE` transaction that advances the LAB-082 provider head and excludes unresolved PREPARED shared-anchor work.

Three audit hardenings are now on the draft branch:
1. The initial legacy/new cutoff was unsigned SQL metadata. It is now a threshold-signed `ThresholdEnablement` bound to the exact provider generation and exact threshold authority.
2. If the enablement row is missing while any threshold-governed provider proof already exists, supported initialization fails closed instead of creating a later cutoff.
3. Enablement fields now require canonical lowercase 64-hex identities and exact integer types; Python `bool == 1` aliases are rejected.

The earlier `integration.py` is retained only as prototype/audit evidence. `supported.py` is the fail-closed LAB-083 surface.

## Evidence produced

- New package: `experiments/provider_threshold_rotation/`.
- Research note: `research/2026-08-22-threshold-provider-rotation.md`.
- Threshold/storage corrected suite: 11/11 passed after signed-cutoff helper coverage was added.
- Signed enablement/cutoff suite: 3/3 passed.
- Strict enablement type/canonicalization suite: 3/3 passed.
- Unsafe old+attacker-new baseline failed as expected because LAB-082-like old+new-only authorization accepts the compromise scenario.
- Compile/py_compile passed for the new package slices exercised locally.
- Draft PR #158 has ten changed paths, all additions except later hardening updates to those new files.
- Direct `git clone` was probed and failed before execution because this runtime cannot resolve `github.com`; connector reconstruction remains the required exact-source fallback.
- Issue #157 received a progress comment after a full issue-body update was transiently blocked before execution by an external safety-status gate.

## Known blockers / constraints

- No owner/product blocker.
- PR #158 is not ready to merge: exact published `supported.py` has not yet been executed against merged LAB-082/LAB-080/LAB-036.
- Historical pre-LAB-083 provider transitions remain legacy verification-only; they are not retroactively promoted to threshold-authorized transitions.
- The current reference threshold authority implements normal old+new quorum rotation but not yet an explicit break-glass recovery path; LAB-083 must either reuse an existing lab recovery authority or record a deliberate non-goal before DONE.
- Current quorum keys are a local reference mechanism, not HSM/KMS custody or distributed consensus.

## Exact next action

Reconstruct exact PR #158 HEAD bytes through the GitHub connector, including `supported.py`, `enablement.py`, protocol/tests and exact merged LAB-082/LAB-080/LAB-036 dependencies. Verify Git blob identities before execution. Add/run real integration tests for: successful quorum-authorized provider rotation; compromised old+attacker-new without quorum; missing/duplicate/revoked/stale quorum; PREPARED reservation blocking rotation; threshold-authority rotation racing provider rotation; restart proof corruption; signed-enablement deletion/tamper; and preservation of historical LAB-082 receipts/legacy transitions. Reuse an existing threshold recovery authority if practical rather than inventing another one. Then run LAB-082/LAB-080 regressions plus compileall and perform a fresh remote patch audit. Only after a clean exact-source gate may PR #158 move from draft to ready/merge.

## Backlog

- #157 / LAB-083 — threshold-authorized asymmetric provider rotation — IN_PROGRESS.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
