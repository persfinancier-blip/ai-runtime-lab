# Current Lab State

Last updated: 2026-08-24

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085.
- Active: Issue #163 / LAB-086 — IN_PROGRESS.
- Branch: `lab/086-asymmetric-break-glass-history`.
- Draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Current observed PR HEAD: `21d762c473d3525eb85762dfc782a7c58321b3cb`.
- PR remains draft/mergeable; full current-head merged-stack regression gate has not passed.

## Last completed step

Extended the post-cutoff SQLite mutation-fence audit beyond the prior DELETE and `INSERT OR REPLACE` cases. Added regressions for authority UPSERT `ON CONFLICT DO UPDATE`, transition UPSERT `ON CONFLICT DO UPDATE`, head UPSERT `ON CONFLICT DO UPDATE`, and `UPDATE OR REPLACE` on the singleton head. The focused transition fixture was also corrected to match the production LAB-085 schema by making `new_authority_id` the PRIMARY KEY before the UPSERT result was treated as evidence.

The exact current `strict_fence.py` and exact newly published test bytes were then executed together. All additional SQLite conflict-resolution paths are denied by the existing unconditional post-cutoff triggers; no new bypass was found in this focused pass.

Connector reconstruction of the real merged dependency closure also progressed through LAB-080/082/083/084/085 implementation files. The recovered main files were checked by Git blob identity and the exact `SupportedRecoveryCustodyLedger` import succeeds. The current LAB-086 real-schema package/tests still need to be assembled into that same closure before the full gate can be claimed.

## Evidence produced

- Branch commit: `21d762c473d3525eb85762dfc782a7c58321b3cb` (`LAB-086 cover SQLite conflict-algorithm fence paths`).
- Exact published `strict_fence.py` blob: `eb9f3d60f9bda56de9d71aa3aa406a7d6a99ae78`.
- Exact published updated `test_strict_fence.py` blob: `4b651db3638c8b9f2341d52b512f075c4b3c31d2`.
- Local `git hash-object` matched both published blobs.
- Exact current strict-fence suite: **10/10 passed**.
- Newly covered and rejected: authority UPSERT/DO UPDATE, transition UPSERT/DO UPDATE, head UPSERT/DO UPDATE, and `UPDATE OR REPLACE` head mutation.
- Existing covered cases remain: forged proof row, destructive DELETEs, head `INSERT OR REPLACE`, controlled write-locked mutation, rollback fence restoration, and obsolete-trigger replacement.
- Exact connector-reconstructed merged implementation dependencies verified by Git blob through LAB-080/082/083/084/085; `SupportedRecoveryCustodyLedger` imports from that closure.
- Latest branch/main compare after this run: **ahead 61 / behind 19**, status `diverged`; all **21 LAB-086 paths remain additions** with no path overlap against current `main`.
- Direct shell Internet/GitHub transport remains unavailable; GitHub connector is healthy and is the supported source/control-plane path.

## Known blockers / constraints

- Forged-proof, destructive-DELETE, head-REPLACE, and audited UPSERT/conflict-algorithm fence paths are fixed/covered in the candidate.
- Remaining merge gate: exact current-head LAB-086 real-schema tests plus merged LAB-085/084/083/082/080 regressions have not yet been executed together from one connector-reconstructed dependency closure.
- Logical SQLite scrubbing is not forensic erasure; WAL/filesystem remnants remain outside the claim.
- Whole-store rollback freshness remains delegated to the external monotonic-anchor layer. No live HSM/KMS is claimed.
- Branch divergence is not currently a content conflict because every LAB-086 path is new, but it must be rechecked immediately before integration.

## Exact next action

1. Finish reconstructing the exact current PR HEAD `21d762c473d3525eb85762dfc782a7c58321b3cb` LAB-086 implementation/tests into the already reconstructed merged LAB-080/082/083/084/085 dependency closure, verifying every executable file with its Git blob identity.
2. Execute all current LAB-086 real-schema tests: migration guard, public-only suffix/restart, scrubbed-prefix + asymmetric suffix, forged-proof and stale-writer regressions, direct-suffix denial, strict fence/trigger upgrade, final-supported rotation, and temporary-fence rollback.
3. Execute merged LAB-085/084/083/082/080 regressions, unsafe legacy-promotion seed, and compileall from the same closure.
4. Perform a fresh full audit focused on alternate mutation entry points, transaction-scoped fence removal, SQLite conflict algorithms, forged/orphan/substituted proofs, predecessor/root binding, historical-root authorization windows, restart snapshots, and rotation races; fix and re-run every defect.
5. Re-check branch/main divergence. Keep PR #165 draft until the full gate is clean; only then mark ready and integrate.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; focused fence is now 10/10 with production-shaped conflict-algorithm regressions; full merged-stack exact-source gate remains.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
