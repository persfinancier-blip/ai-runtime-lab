# Current Lab State

Last updated: 2026-08-24

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085.
- Active: Issue #163 / LAB-086 — IN_PROGRESS.
- Branch: `lab/086-asymmetric-break-glass-history`.
- Draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Current observed PR HEAD: `99df30f0b8cae05354b1576ec3d67fb5410080a7`.
- PR remains draft/mergeable; full current-head merged-stack regression gate has not passed.

## Last completed step

A focused SQL-boundary audit found and fixed two additional post-cutoff mutation bypasses in the public-recovery fence.

First, authority/transition/head DELETE operations were not fenced, so an alternate/stale writer could durably remove authenticated public-recovery state and only be caught by later verification. DELETE triggers now protect all three objects.

Second, the prior candidate still allowed `INSERT OR REPLACE` on the singleton public head because the head fence covered UPDATE/DELETE but not INSERT. This bypass was actually executed and replaced `old` with `attacker`. A dedicated `BEFORE INSERT` head trigger now blocks that SQLite conflict-resolution path as well.

## Evidence produced

- Branch commits: `8c7df036817c0e46b47fabc8493424338e2ca3fa` (DELETE fence), `87bda84f189ec335989d65369f052dfbf06a0e30` (DELETE regression), `a17449185b9007f1702a02bff674d37e9778e221` (head INSERT fence), `99df30f0b8cae05354b1576ec3d67fb5410080a7` (REPLACE regression).
- Exact published `strict_fence.py` blob: `eb9f3d60f9bda56de9d71aa3aa406a7d6a99ae78`.
- Exact published `test_strict_fence.py` blob: `9149115cb5f67ce31f35c7a5c31abd876ec01cd8`.
- Both published blobs matched local `git hash-object` on the bytes actually executed.
- Exact focused strict-fence suite: **6/6 passed**.
- Covered: forged proof row rejection; DELETE denial for authority/transition/head; `INSERT OR REPLACE` head bypass denial; controlled write-locked mutation; rollback restoring the fence; replacement of obsolete weak trigger definitions.
- Focused compileall passed.
- The pre-fix `INSERT OR REPLACE` bypass was directly reproduced: the unfixed candidate changed the head from `old` to `attacker`.
- Issue #163 has both audit findings/evidence; PR #165 remains draft.
- Direct shell Internet/GitHub transport is unavailable in this runtime; GitHub connector is healthy and is the supported source/control-plane path.

## Known blockers / constraints

- Forged-proof, destructive-DELETE, and head-REPLACE fence blockers are fixed in the candidate.
- Remaining merge gate: exact current-head LAB-086 integration tests plus merged LAB-085/084/083/082/080 regressions have not yet been executed together from one connector-reconstructed dependency closure.
- Logical SQLite scrubbing is not forensic erasure; WAL/filesystem remnants remain outside the claim.
- Whole-store rollback freshness remains delegated to the external monotonic-anchor layer. No live HSM/KMS is claimed.

## Exact next action

1. Reconstruct exact PR HEAD `99df30f0b8cae05354b1576ec3d67fb5410080a7` dependency closure through the GitHub connector and verify Git blob identities.
2. Execute all current LAB-086 real-schema tests, especially forged-proof, stale LAB-085 writer, direct suffix bypass, destructive DELETE, head `INSERT OR REPLACE`, final-supported legitimate rotation, cutoff/restart, scrubbed-prefix/asymmetric-suffix, trigger-upgrade, and temporary-fence rollback cases.
3. Execute merged LAB-085/084/083/082/080 regressions, the unsafe legacy-promotion seed, and compileall.
4. Perform a fresh full audit focused on every alternate mutation entry point, transaction-scoped fence removal, SQLite conflict algorithms, forged/orphan/substituted proofs, predecessor/root binding, restart, and rotation races; fix and re-run any defect found.
5. Re-check branch/main divergence. Keep PR #165 draft until the full gate is clean; only then mark ready and integrate.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; forged-proof + DELETE + REPLACE blockers fixed, full merged-stack exact-source gate remains.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
