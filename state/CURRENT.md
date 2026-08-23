# Current Lab State

Last updated: 2026-08-23

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085.
- Active: Issue #163 / LAB-086 — IN_PROGRESS.
- Branch: `lab/086-asymmetric-break-glass-history`.
- Draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Current observed PR HEAD: `dfd369a8f9e40c94621ca8c7022dff2cb05f65d1`.
- PR is open/draft/mergeable; do not merge until the blocker below is fixed and the exact full gate is rerun.

## Last completed step

The exact standalone branch source was reconstructed through the GitHub connector because direct shell GitHub DNS remains unavailable. `protocol.py` blob `cccb531fa13b8f8d4e3a7c3163dd7c7cbeb3ec41` executed 12/12 corrected tests; the unsafe legacy auto-promotion seed failed as expected. Exact `migration_guard.py` blob `605f40490a431226164e7ab3966d8aa1a1d1dc8d` was reconstructed and compiled.

A fresh cross-layer audit found a merge blocker: after the LAB-086 cutoff, an old LAB-085 `AsymmetricRecoveryCustody.rotate()` caller can still commit a new public recovery authority/transition/head using only old-public + new-public Ed25519 quorum. It does not require LAB-086 current-root co-authorization and does not create `provider_asymmetric_recovery_public_root_proofs`. LAB-086 detects the missing root proof later, but invalid durable authority state has already committed, creating persistent fail-closed DoS and violating the advertised post-cutoff rotation boundary.

The counterexample is now durable executable evidence on the branch: commit `dfd369a8f9e40c94621ca8c7022dff2cb05f65d1` adds `experiments/asymmetric_break_glass_history/tests/test_stale_public_writer_regression.py`, which directly invokes the stale underlying LAB-085 public-custody API after cutoff and requires zero authority/transition/head mutation. It is expected to fail until the SQL fence is implemented.

A deterministic SQLite design probe also confirmed the intended correction: without a pre-existing root proof the stale writer is rejected with `IntegrityError`; proof-first insertion followed by authority/transition/head mutation succeeds atomically in one `BEGIN IMMEDIATE`.

## Evidence / constraints

- Exact standalone LAB-086 reference suite: 12/12 passed on the pre-regression HEAD; its source is unchanged by the new regression commit.
- Unsafe legacy auto-promotion seed: failed as expected.
- Exact `migration_guard.py`: `py_compile` passed.
- New stale-writer regression is published but has not yet been executed against a corrected implementation.
- Direct shell GitHub access remains unavailable (`Could not resolve host: github.com`). GitHub connector remains healthy and is the supported exact-source path.
- Logical SQLite-state scrubbing is not forensic erasure; WAL/filesystem remnants remain outside the claim.
- Whole-store rollback freshness remains delegated to the external monotonic-anchor layer. No live HSM/KMS is claimed.

## Exact next action

1. Re-fetch PR #165 and require HEAD `dfd369a8f9e40c94621ca8c7022dff2cb05f65d1` or restart the gate if it moved.
2. Fix the stale public-custody writer bypass at the SQL authority boundary:
   - ensure `provider_asymmetric_recovery_public_root_proofs` exists at migration time;
   - add cutoff-conditional SQL guards so post-cutoff inserts/updates in `provider_recovery_public_authorities`, `provider_recovery_public_transitions`, and `provider_recovery_public_head` require the exact LAB-086 root-proof predecessor/successor binding;
   - reorder `rotate_public_recovery_authority()` to validate old/new public quorum and current-root quorum, persist/check the exact root-proof row first, then call `public_recovery_custody.rotate_locked()` in the same `BEGIN IMMEDIATE`; rollback must remove both proof and rotation on any failure.
3. Run the new stale-writer regression and prove no new public authority, transition, or head is committed; retain the legitimate supported-rotation success path.
4. Reconstruct exact updated branch bytes through the connector and run LAB-086 migration/suffix/mixed-prefix tests plus LAB-085/084/083/082/080 regressions, unsafe seed and compileall.
5. Fix every failure, perform a fresh full remote patch audit, then re-check branch/main divergence and integrate only after a clean gate.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; stale post-cutoff LAB-085 public-custody writer fencing/root-proof ordering is the current blocker.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
