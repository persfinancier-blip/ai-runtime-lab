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
- Parallel work: Issue #166 / LAB-087 — IN_PROGRESS, branch `lab/087-sqlite-authorizer-boundary`, draft PR #171 HEAD `6d148c6a3b57df72675a1fa7787ad70952d91e05`.

## Last completed step

LAB-086 full connector-reconstructed current-head real-ledger gate remained too expensive to rebuild safely in this run, so per the handoff the run advanced the unblocked LAB-087 enforcement slice rather than repeating already-proven LAB-080→085 reconstruction.

The exact published pre-change LAB-087 process boundary was first reconstructed and byte-verified (`process_boundary.py 3db8ee6...`, test `82c68ae...`) and executed 2/2 PASS plus compileall.

A fresh WAL/sidecar audit then found a real contract defect. Under broker umask `077`, a WAL database had main DB `0640` for the worker group but `-wal/-shm` sidecars `0600 root:root`. The old boundary returned `verify()==True` while the distinct `nobody` worker failed read-only open with `OperationalError: unable to open database file`. SQLite's documented read-only WAL requirements therefore were not represented by the boundary.

LAB-087 now fails closed on `journal_mode=wal` during install and verify, keeping rollback-journal mode as the supported live-worker contract. A second deployment defect was also closed: `install()` previously changed ownership/mode of whatever parent directory contained the DB. It now rejects a parent containing unrelated siblings before permission changes, enforcing the documented dedicated broker-owned directory boundary.

Exact published current PR #171 bytes match the executed candidates:
- `protocol.py` `5c999166c2155baa5ce3f644c36efe0e01e4e3fe`;
- `test_protocol.py` `3f795d22d844293d62a09a0c1285764443db2279`;
- `process_boundary.py` `fee25421ab74b7c1fa0a97129473b3b310385a5c`;
- `test_process_boundary.py` `bb1fb631d70a0d8c2867c7f8d4b05aa107711918`.
Combined exact suite: **12/12 PASS** (authorizer 7/7 + process/filesystem/WAL/dedicated-directory 5/5); compileall PASS.

README and `research/2026-08-26-lab087-wal-readonly-boundary.md` record the primary-source WAL constraint and deployment boundary. Same-UID/root/CAP_DAC_OVERRIDE, permission-changing authority and ancestor/filesystem namespace replacement remain outside this slice's claim.

## Evidence produced / reconfirmed

- LAB-086 published least-privilege `strict_fence.py` blob remains `5da01e28a9f813a136d138637f855940f04aab46`; prior focused 13/13 was run on those exact bytes.
- Cumulative exact lower-stack evidence for LAB-086 remains: LAB-080 18/18, LAB-082 28/28, LAB-083 24/24, LAB-084 17/17, LAB-085 core 12/12, asymmetric-custody 8/8, public/final 11/11; lower unsafe baselines failed as intended.
- LAB-087 exact current slice: **12/12 PASS**, compileall PASS.
- LAB-087 WAL counterexample: old boundary verified true while a distinct worker could not open the live WAL DB because sidecars were inaccessible.
- LAB-087 shared-parent regression: install rejects unrelated siblings before changing parent ownership/mode.
- Official SQLite sources recorded in the research note: `https://www.sqlite.org/wal.html#readonly` and `https://www.sqlite.org/walformat.html`.

## Known blockers / constraints

- LAB-086 full current-head real-ledger `migration_guard + suffix + final_supported` exact-source gate is still incomplete. Do not mark PR #165 ready until it passes, followed by unsafe seed, full compileall and final security audit.
- Direct shell GitHub transport has repeatedly failed DNS; connector remains healthy and is not an owner blocker.
- LAB-087 is not a same-process/root sandbox. It assumes a distinct worker principal, rollback-journal mode and a dedicated broker-owned DB directory. Ancestor namespace replacement remains outside the current claim.
- LAB-088/#167 signer-noise; LAB-090/#169 provider handoff freshness; LAB-091/#170 mutable shared-anchor/new-receipt writer authorization remain READY.
- Logical SQL scrubbing is not forensic erasure; whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. Resume LAB-086 first. Re-fetch PR #165 HEAD, connector-reconstruct exact current `migration_guard.py`, `suffix.py`, `final_supported.py` and current real-schema tests on the already proven LAB-080→085 dependency closure.
2. Execute migration/root-coauthorization/restart, scrubbed-prefix/asymmetric-suffix, orphan/partial-state, full lower/public-history guards, public-rotation cross-binding/history, inherited/direct surfaces, rotation races and final single-snapshot verification.
3. Run unsafe legacy-promotion seed and full compileall; perform a fresh full security audit and branch/main divergence check. Fix every blocking failure before ready/merge.
4. Only if LAB-086 reconstruction again cannot fit safely in the run, continue LAB-087 with ancestor-namespace hardening/verification; do not repeat the already-proven exact 12/12 authorizer/process/WAL/dedicated-directory gate.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; full current-head real-ledger gate remains the primary merge gate.
- #166 / LAB-087 — IN_PROGRESS; exact current PR slice 12/12 PASS; ancestor namespace boundary remains to be hardened/audited before ready.
- #167 / LAB-088 — READY; threshold signer-noise robustness.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — READY; mutable/shared-ledger plus new provider-receipt ordinary-DML writer authorization.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
