# Current Lab State

Last updated: 2026-08-23

## Active objective

LAB-084 — add separately authenticated break-glass recovery for the LAB-083 provider-rotation threshold authority without weakening normal quorum rotation or historical verification.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-083.
- LAB-083 / Issue #157: DONE; PR #158 squash-merged as `de6a83a3279f690bf0ea50f5e9bfaaa91148533d`.
- Active: Issue #159 / LAB-084 — IN_PROGRESS.
- Active branch: `lab/084-provider-rotation-recovery`.
- Active PR: none yet. A normal draft-PR creation attempt was blocked by an external safety-status gate before execution; branch work is not blocked.
- Branch status after first slice: ahead of `main` by 5 commits, behind by 0, five new conflict-free paths.

## Last completed step

LAB-083's final exact-source gate was completed in this invocation. Exact current executable PR bytes and merged LAB-082/LAB-080/LAB-036 dependencies were reconstructed through the GitHub connector and checked against Git blob IDs. LAB-083 corrected tests passed 24/24, LAB-082 supported regression passed 2/2, LAB-080 supported regression passed 4/4, unsafe old+attacker-new failed as expected, and compileall passed. A final audit found no remaining supported-surface fail-open. Break-glass recovery was explicitly split into LAB-084 rather than weakening normal LAB-083 rotation.

LAB-084 then started from merged LAB-083. The first reference `DurableRecoveryController` was built and published. It gives recovery a separate content-addressed quorum authority; binds exact predecessor rotation authority, exact successor, and recovery authority/generation; stores the full recovery proof; and advances rotation-authority version/generation in one SQL transaction. Normal LAB-083 authority signatures cannot substitute for the recovery quorum.

The first LAB-084 audit found that the durable recovery head was not re-bound to the pinned recovery bootstrap on restart. This was fixed before publication. `verify_durable()` now rechecks recovery bootstrap/head identity and every persisted recovery transition proof.

## Evidence produced

- LAB-083 merge: `de6a83a3279f690bf0ea50f5e9bfaaa91148533d`.
- LAB-083 exact corrected evidence: 24/24 LAB-083 + 2/2 LAB-082 supported + 4/4 LAB-080 supported; unsafe seed failed as expected; compileall passed.
- New LAB-084 package: `experiments/provider_rotation_recovery/`.
- LAB-084 research note: `research/2026-08-23-provider-rotation-authority-recovery.md`.
- LAB-084 first corrected local suite: 9/9 passed after bootstrap/head audit fix.
- LAB-084 unsafe normal-quorum-self-recovery seed: failed as expected.
- LAB-084 branch compare: ahead 5 / behind 0, only five new paths.
- Follow-up/recovery Issue #159 is IN_PROGRESS on `lab/084-provider-rotation-recovery`.

## Known blockers / constraints

- No owner/product blocker.
- Draft PR creation for LAB-084 was blocked once by an external safety-status gate before execution; safe branch work remains available and should continue.
- The first LAB-084 slice is intentionally not a supported runtime surface. LAB-083's current durable rotation-authority verifier recognizes only normal old+new quorum edges and will not yet accept a break-glass recovery edge.
- Recovery must be serialized with LAB-080 PREPARED work and with normal provider/authority rotation on one SQL commit boundary.
- The current first slice uses a pinned recovery-authority generation. Recovery-authority lifecycle/rotation still needs reuse of LAB-057-style old-recovery + new-recovery + current-root authorization.
- If both normal threshold authority and recovery quorum are simultaneously lost/compromised, LAB-084 must fail closed and require an external bootstrap/ceremony; no recursive recovery is allowed.
- Current quorum keys remain local reference mechanisms, not HSM/KMS custody or distributed consensus.

## Exact next action

Continue Issue #159 on `lab/084-provider-rotation-recovery`. Build a recovery-aware supported LAB-083 surface. In one `BEGIN IMMEDIATE` boundary, reject unresolved LAB-080 PREPARED work and serialize provider rotation, normal rotation-authority rotation, and break-glass recovery. Replace the normal-only authority-history verifier with a mixed-edge verifier that accepts each adjacent authority transition only when exactly one valid normal old+new quorum proof or recovery-quorum proof exists. Add races normal-rotation↔recovery and provider-rotation↔recovery; prove stale pre-recovery quorum cannot authorize new provider rotation; preserve historical LAB-083 threshold proofs and LAB-082 receipts after recovery; add restart corruption/missing-proof tests. Then integrate LAB-057-style recovery-authority lifecycle, run exact-source LAB-084 + LAB-083/082/080 regressions and compileall, perform a fresh remote patch audit, and only then create/ready/merge a PR.

## Backlog

- #159 / LAB-084 — threshold provider-rotation authority recovery — IN_PROGRESS.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
