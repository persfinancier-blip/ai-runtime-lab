# Current Lab State

Last updated: 2026-08-26

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085.
- Active priority: Issue #163 / LAB-086 — IN_PROGRESS.
- Branch: `lab/086-asymmetric-break-glass-history`.
- Draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Current observed PR HEAD at run start: `66786dea59809fc070006dc911cc6e4822687ed3`; re-fetch before execution/integration.
- Parallel work: Issue #166 / LAB-087 — IN_PROGRESS, branch `lab/087-sqlite-authorizer-boundary`, draft PR #171.

## Last completed step

LAB-086 full connector-reconstructed current-head real-ledger gate remained too expensive to rebuild safely in this run, so per the previous handoff the run advanced the unblocked LAB-087 enforcement slice rather than repeating already-proven LAB-080→085 reconstruction.

First, the exact published pre-change LAB-087 process boundary was reconstructed from GitHub and byte-verified:
- `process_boundary.py` blob `3db8ee6c6fc4881fc21c4074cc987f19bb0ab539`;
- `test_process_boundary.py` blob `82c68ae902ca82f0ca969bf98a6d222036ee7f6d`.
It executed **2/2 PASS** plus compileall.

A fresh WAL/sidecar audit then found a real contract defect. Under broker umask `077`, a WAL database had main DB `0640` for the worker group but `-wal/-shm` sidecars `0600 root:root`. The old `UnixReadOnlyWorkerBoundary.verify()` still returned true, while the distinct `nobody` worker failed read-only open with `OperationalError: unable to open database file`. SQLite's WAL documentation requires readable existing sidecars, directory write authority to create them, or `immutable`; the latter is not valid for a live broker-mutated authority DB.

LAB-087 now fails closed on `journal_mode=wal` during both install and verify, keeping rollback-journal mode as the supported live worker boundary for this slice. Exact published blobs match the locally executed candidates:
- `process_boundary.py` `0bca65f9aa1505960d818405fb1a6f5f8d8fd4f7` (commit `c1911a6621fdc6b6f3a397335b63bd640fa9505e`);
- `test_process_boundary.py` `e4217d8ca016713e380c7631c7d1fc042163a8b8` (commit `41729827f56501edd8ebc07250b51e10b7829d51`).
The exact combined current PR #171 executable slice then passed **11/11** (authorizer 7/7 + process/filesystem/WAL 4/4) and compileall.

README and research note now state the deployment boundary explicitly: rollback-journal mode plus a dedicated broker-owned DB directory; same-UID/root/CAP_DAC_OVERRIDE, permission-changing and ancestor namespace-replacement authority remain outside the claim. Research note: `research/2026-08-26-lab087-wal-readonly-boundary.md`.

## Evidence produced / reconfirmed

- LAB-086 published least-privilege `strict_fence.py` blob remains `5da01e28a9f813a136d138637f855940f04aab46`; prior focused 13/13 was run on those exact bytes.
- Cumulative exact lower-stack evidence for LAB-086 remains: LAB-080 18/18, LAB-082 28/28, LAB-083 24/24, LAB-084 17/17, LAB-085 core 12/12, asymmetric-custody 8/8, public/final 11/11; lower unsafe baselines failed as intended.
- LAB-087 exact current slice: **11/11 PASS**, compileall PASS.
- LAB-087 WAL counterexample: old boundary verified true while a distinct worker could not open the live WAL DB because sidecars were inaccessible.
- LAB-087 post-fix contract: WAL rejected at install and re-verify; rollback-journal deployment remains readable while worker DML/filesystem mutation stays denied.
- Official SQLite sources recorded in the research note: `https://www.sqlite.org/wal.html#readonly` and `https://www.sqlite.org/walformat.html`.

## Known blockers / constraints

- LAB-086 full current-head real-ledger `migration_guard + suffix + final_supported` exact-source gate is still incomplete. Do not mark PR #165 ready until it passes, followed by unsafe seed, full compileall and final security audit.
- Direct shell GitHub transport failed DNS in prior runs; connector remains healthy and is not an owner blocker.
- LAB-087 is not a same-process/root sandbox. The Unix DAC slice assumes a distinct worker principal and a dedicated broker-owned DB directory. WAL is deliberately unsupported in this slice.
- LAB-088/#167 signer-noise; LAB-090/#169 provider handoff freshness; LAB-091/#170 mutable shared-anchor/new-receipt writer authorization remain READY.
- Logical SQL scrubbing is not forensic erasure; whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. Resume LAB-086 first. Re-fetch PR #165 HEAD, connector-reconstruct exact current `migration_guard.py`, `suffix.py`, `final_supported.py` and current real-schema tests on the already proven LAB-080→085 dependency closure.
2. Execute migration/root-coauthorization/restart, scrubbed-prefix/asymmetric-suffix, orphan/partial-state, full lower/public-history guards, public-rotation cross-binding/history, inherited/direct surfaces, rotation races and final single-snapshot verification.
3. Run unsafe legacy-promotion seed and full compileall; perform a fresh full security audit and branch/main divergence check. Fix every blocking failure before ready/merge.
4. Only if LAB-086 reconstruction again cannot fit safely in the run, continue LAB-087 with enforcement/audit of the dedicated-directory and ancestor-namespace deployment assumptions; do not repeat the already-proven 11/11 WAL/process gate.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; full current-head real-ledger gate remains the primary merge gate.
- #166 / LAB-087 — IN_PROGRESS; exact authorizer/process/WAL suite 11/11 PASS; dedicated-directory/namespace deployment boundary remains to be hardened/audited before ready.
- #167 / LAB-088 — READY; threshold signer-noise robustness.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — READY; mutable/shared-ledger plus new provider-receipt ordinary-DML writer authorization.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
