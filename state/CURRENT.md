# Current Lab State

Last updated: 2026-08-23

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085.
- Active: Issue #163 / LAB-086 — IN_PROGRESS.
- Branch: `lab/086-asymmetric-break-glass-history`.
- Draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Current observed PR HEAD: `bde0aa90a8e0180cb9f8f3237bdb7c88a8bfb0e6`.
- PR remained open/draft/mergeable during this run.

## Last completed step

The exact standalone branch source was reconstructed through the GitHub connector because direct shell GitHub DNS remains unavailable. `protocol.py` blob `cccb531fa13b8f8d4e3a7c3163dd7c7cbeb3ec41` executed 12/12 corrected tests; the unsafe legacy auto-promotion seed failed as expected. Exact `migration_guard.py` blob `605f40490a431226164e7ab3966d8aa1a1d1dc8d` was reconstructed and compiled.

A fresh cross-layer audit then found a new merge blocker: after the LAB-086 cutoff, an old LAB-085 `AsymmetricRecoveryCustody.rotate()` caller can still commit a new public recovery authority/transition/head using only old-public + new-public Ed25519 quorum. It does not require LAB-086 current-root co-authorization and does not create `provider_asymmetric_recovery_public_root_proofs`. LAB-086 detects the missing root proof later, but the invalid durable authority state has already committed, creating persistent fail-closed DoS and violating the advertised post-cutoff rotation boundary.

Issue #163 now records the exact counterexample and required correction.

## Evidence / constraints

- Exact standalone LAB-086 reference suite on current PR head: 12/12 passed.
- Unsafe legacy auto-promotion seed: failed as expected.
- Exact `migration_guard.py`: `py_compile` passed.
- Direct shell GitHub access: still unavailable (`Could not resolve host: github.com`). GitHub connector remains healthy and is the supported exact-source path.
- The real-schema migration/suffix stack is not merge-ready until the stale public-custody writer is fenced and the complete gate is rerun.
- Logical SQLite-state scrubbing is not forensic erasure; WAL/filesystem remnants remain outside the claim.
- Whole-store rollback freshness remains delegated to the external monotonic-anchor layer. No live HSM/KMS is claimed.

## Exact next action

1. Re-fetch PR #165 and require the recorded HEAD or restart the gate if it moved.
2. Fix the stale public-custody writer bypass at the SQL authority boundary:
   - ensure the LAB-086 public-root-proof table exists at migration time;
   - add cutoff-conditional SQL guards so post-cutoff inserts/updates in `provider_recovery_public_authorities`, `provider_recovery_public_transitions`, and `provider_recovery_public_head` require the exact LAB-086 root-proof predecessor/successor binding;
   - reorder `rotate_public_recovery_authority()` to validate old/new public quorum and current-root quorum, persist/check the root-proof row first, then call `public_recovery_custody.rotate_locked()` in the same `BEGIN IMMEDIATE`; any failure must roll back both proof and rotation.
3. Add a real regression that calls the stale underlying `public_recovery_custody.rotate()` after cutoff and proves no new public authority, transition, or head is committed.
4. Reconstruct exact updated branch bytes through the connector and run LAB-086 migration/suffix/mixed-prefix tests plus LAB-085/084/083/082/080 regressions, unsafe seed and compileall.
5. Fix every failure, perform a fresh full patch audit, then re-check branch/main divergence and integrate only after a clean gate.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; stale post-cutoff LAB-085 public-custody writer fencing/root-proof ordering is the current blocker.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
