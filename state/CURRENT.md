# Current Lab State

Last updated: 2026-08-26

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085.
- Active: Issue #163 / LAB-086 — IN_PROGRESS.
- Branch: `lab/086-asymmetric-break-glass-history`.
- Draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Current observed PR HEAD: `66786dea59809fc070006dc911cc6e4822687ed3`.
- Parallel unblocked work: Issue #166 / LAB-087 — IN_PROGRESS, branch `lab/087-sqlite-authorizer-boundary`, draft PR #171 HEAD `de211a80d2010df3d653c13e806356f158f13cc2`.

## Last completed step

LAB-086 remains the priority, but the full connector-reconstructed LAB-080→086 closure was not locally persistent in this run and direct shell GitHub transport again failed DNS resolution. Per the prior handoff, advanced LAB-087 instead of spending the run repeating already-proven lower-layer reconstruction.

LAB-087 now has a real Unix process/filesystem ownership experiment in addition to the connection-scoped SQLite authorizer. Existing `UnixReadOnlyWorkerBoundary` exact branch blob `3db8ee6c6fc4881fc21c4074cc987f19bb0ab539` was reconstructed and executed. The runtime provides a root broker principal plus distinct `nobody:nogroup` worker principal. With broker-owned parent `0750` and DB `0640` owned by broker UID + worker GID, the worker can read the canonical DB but cannot open it `O_RDWR`, commit a SQLite UPDATE, unlink/rename the DB pathname, or chmod it. The broker UID remains writable as the explicit negative control.

A process-level regression was published in branch commit `fc43b928ee3e127b22f553a9742caff71f809007`; README update commit `de211a80d2010df3d653c13e806356f158f13cc2`. Actual local pre-publication run: 2/2 PASS plus compileall. Published test blob is `82c68ae902ca82f0ca969bf98a6d222036ee7f6d`; exact published-byte re-execution is still required before counting it as exact-source evidence.

## Evidence produced / reconfirmed

- LAB-086 published least-privilege `strict_fence.py` blob remains `5da01e28a9f813a136d138637f855940f04aab46`; prior focused 13/13 was run on those exact bytes.
- Cumulative exact lower-stack evidence remains: LAB-080 18/18, LAB-082 28/28, LAB-083 24/24, LAB-084 17/17, LAB-085 core 12/12, asymmetric-custody 8/8, public/final 11/11; lower unsafe baselines failed as intended.
- LAB-087 authorizer slice exact published suite remains 7/7 PASS; compileall PASS.
- LAB-087 outer-boundary pre-publication process test: 2/2 PASS; compileall PASS.
- Worker-principal denial observed for `O_RDWR`, SQLite write, unlink, rename and chmod; canonical DB value remained unchanged.
- Broker-principal negative control successfully updated the DB after the boundary was installed.
- Exact LAB-087 process-boundary implementation blob: `3db8ee6c6fc4881fc21c4074cc987f19bb0ab539`.
- Published process regression blob: `82c68ae902ca82f0ca969bf98a6d222036ee7f6d`; publication commit `fc43b928ee3e127b22f553a9742caff71f809007`.

## Known blockers / constraints

- LAB-086 full current-head real-ledger migration/suffix/final-supported exact-source gate is still incomplete. Do not mark PR #165 ready until it passes, followed by unsafe seed, full compileall and final security audit.
- Direct shell GitHub transport again failed DNS resolution in this run; connector remains healthy and is not an owner blocker.
- LAB-087 authorizer/wrapper is not a same-process sandbox. The Unix DAC slice protects only a distinct worker UID/GID without broker UID/root/CAP_DAC_OVERRIDE/permission-changing or namespace-replacement authority.
- The LAB-087 process regression was executed before publication; published-byte exact rerun remains.
- LAB-088/#167 signer-noise; LAB-090/#169 provider handoff freshness; LAB-091/#170 mutable shared-anchor/new-receipt writer authorization remain READY.
- Logical SQL scrubbing is not forensic erasure; whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. Resume LAB-086 first: connector-reconstruct the exact current PR HEAD `migration_guard + suffix + final_supported` and current real-schema tests on the already proven LAB-080→085 dependency closure; execute migration/root-coauthorization/restart, scrubbed-prefix/asymmetric-suffix, orphan/partial state, lower/public-history guards, cross-binding/history, inherited/direct surfaces, rotation races and final single-snapshot verification.
2. Run unsafe legacy-promotion seed and full compileall; perform a fresh full security audit and branch/main divergence check. Only then mark PR #165 ready/integrate.
3. If LAB-086 closure reconstruction is again too expensive for the run, exact-reconstruct the published LAB-087 process regression blob `82c68ae...`, execute it against exact `process_boundary.py`, then audit dedicated-directory/WAL-sidecar assumptions before considering PR #171 ready.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; minimal-thaw runtime published exactly; full current-head real-ledger gate remains.
- #166 / LAB-087 — IN_PROGRESS; draft PR #171 now includes authorizer plus real distinct-UID/GID filesystem boundary; published-byte process test rerun and deployment-assumption audit remain.
- #167 / LAB-088 — READY; threshold signer-noise robustness.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — READY; mutable/shared-ledger plus new provider-receipt ordinary-DML writer authorization.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
