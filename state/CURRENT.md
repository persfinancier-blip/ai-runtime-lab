# Current Lab State

Last updated: 2026-08-24

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085.
- Active: Issue #163 / LAB-086 — IN_PROGRESS.
- Branch: `lab/086-asymmetric-break-glass-history`.
- Draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Current observed PR HEAD: `87bda84f189ec335989d65369f052dfbf06a0e30`.
- PR remains draft/mergeable; full current-head merged-stack regression gate has not passed.

## Last completed step

A fresh SQL-boundary audit found that the post-cutoff public-recovery fence denied INSERT/UPDATE but did not deny DELETE. That left a persistent destructive mutation path for `provider_recovery_public_authorities`, `provider_recovery_public_transitions`, and `provider_recovery_public_head`: a stale/alternate writer could delete authenticated state and only be detected by later verification.

The branch now adds unconditional post-cutoff DELETE triggers for all three objects. The transaction-scoped final writer already removes/reinstalls the complete fence inside one `BEGIN IMMEDIATE`, so the expanded policy preserves the controlled mutation path while closing destructive bypasses.

## Evidence produced

- Branch commits: `8c7df036817c0e46b47fabc8493424338e2ca3fa` (fence) and `87bda84f189ec335989d65369f052dfbf06a0e30` (regression).
- Exact published `strict_fence.py` blob: `3250c008af66100e348361d413b67e0d60b87899`.
- Exact published `test_strict_fence.py` blob: `e8d102fa8d9270564968628d5c14fa9555ba0c4a`.
- Both published blobs matched local `git hash-object` on the bytes actually executed.
- Exact focused strict-fence suite: **5/5 passed**.
- New coverage: post-cutoff DELETE of authority, transition, and head all fail with `sqlite3.IntegrityError` and leave state unchanged.
- Focused compileall passed.
- Earlier forged-proof evidence remains valid: durable proof rows are evidence only, not mutation capability; rollback restores the deny fence; obsolete proof-row-authorizing triggers are replaced.
- Issue #163 received the new audit evidence; PR #165 description was updated to the current HEAD/gate.
- Direct shell Internet/GitHub transport remains unavailable in this runtime; GitHub connector is healthy and is the supported source/control-plane path.

## Known blockers / constraints

- Forged-proof and destructive-DELETE fence blockers are fixed in the candidate.
- Remaining merge gate: exact current-head LAB-086 integration tests plus merged LAB-085/084/083/082/080 regressions have not yet been executed together from one connector-reconstructed dependency closure.
- Logical SQLite scrubbing is not forensic erasure; WAL/filesystem remnants remain outside the claim.
- Whole-store rollback freshness remains delegated to the external monotonic-anchor layer. No live HSM/KMS is claimed.

## Exact next action

1. Reconstruct the exact PR HEAD `87bda84f189ec335989d65369f052dfbf06a0e30` dependency closure through the GitHub connector and verify Git blob identities.
2. Execute all current LAB-086 real-schema tests, especially forged-proof, stale LAB-085 writer, direct suffix bypass, destructive DELETE, final-supported legitimate rotation, cutoff/restart, scrubbed-prefix/asymmetric-suffix, trigger-upgrade, and temporary-fence rollback cases.
3. Execute merged LAB-085/084/083/082/080 regressions, the unsafe legacy-promotion seed, and compileall.
4. Perform a fresh full audit focused on every alternate mutation entry point, transaction-scoped fence removal, forged/orphan/substituted proofs, predecessor/root binding, restart, delete/update/insert mutation coverage, and rotation races; fix and re-run any defect found.
5. Re-check branch/main divergence. Keep PR #165 draft until the full gate is clean; only then mark ready and integrate.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; forged-proof + destructive-delete blockers fixed, full merged-stack exact-source gate remains.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
