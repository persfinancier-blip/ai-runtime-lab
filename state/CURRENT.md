# Current Lab State

Last updated: 2026-08-24

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085.
- Active: Issue #163 / LAB-086 — IN_PROGRESS.
- Branch: `lab/086-asymmetric-break-glass-history`.
- Draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Current observed PR HEAD: `62dc131c888f36a48eab3b750235518d60597eac`.
- PR remains draft; full current-head merged-stack exact-source regression gate has not passed.

## Last completed step

A fresh current-head audit found a consequential-operation fail-open in the final public-recovery rotation path. `SupportedFencedAsymmetricBreakGlassLedger.rotate_public_recovery_authority()` verified the migration boundary and the public-rotation slice, but did not re-run the complete LAB-086 root/provider/recovery history before committing a new public recovery generation. Therefore an already-corrupted `provider_asymmetric_break_glass_proofs` row could survive a successful new public-recovery rotation and only fail on a later restart.

The branch is fixed: the final writer now executes `_verify_lab086_locked(q)` before any public-authority mutation and again after fence restoration, before commit. Added `test_public_rotation_history_guard.py`: create a valid asymmetric root suffix, corrupt its persisted public signature set, attempt a public-recovery rotation, require failure, and require zero changes to public head/authority/transition/root-proof counts.

The exact published fix files were reconstructed locally and matched GitHub blob identities. `py_compile` passed. A focused AST ordering check passed and confirms: full-history verify -> fence removal -> fence reinstall -> full-history verify.

## Evidence produced / reconfirmed

- Exact new `final_supported.py` blob: `066b4a09652b4c331c693ce9a5275d84fe303036`; local `git hash-object` matched.
- Exact new regression blob: `3586b909aa9bd52b4d0c58f393a698a7a592e10d`; local `git hash-object` matched.
- Focused `py_compile` for both exact files: PASS.
- Focused AST guard-order check: PASS.
- Issue #163 and PR #165 description updated with the new blocker/fix and evidence.
- Current branch compare: ahead 77 / behind 31; all 24 PR paths remain additions relative to current main.
- Earlier exact regression evidence remains valid for unchanged lower layers: LAB-080 18/18 PASS; LAB-082 28/28 PASS; LAB-083 24/24 PASS; standalone LAB-086 protocol 12/12 PASS.
- LAB-083 signer-noise robustness remains tracked separately in #167 and is fail-closed availability/robustness, not privilege escalation.

## Known blockers / constraints

- Remaining LAB-086 merge gate: exact LAB-084 and LAB-085 layers plus current-head LAB-086 real-schema tests must still be executed together from one connector-reconstructed dependency closure after the new public-rotation history guard.
- The local filesystem was empty at the beginning of this run; prior reconstructed workspaces are not durable. Direct shell GitHub transport remains unavailable, while the GitHub connector/Contents API is healthy.
- The focused compile/AST checks are not substitutes for the current-head integration regression.
- LAB-086 SQL fences protect against stale/alternate supported mutation paths, not an arbitrary same-privilege raw SQLite DDL writer. That broader boundary is LAB-087 / #166.
- Logical SQL scrubbing is not forensic erasure; WAL/filesystem remnants remain outside the claim.
- Whole-store rollback freshness remains delegated to the external monotonic-anchor layer. No live HSM/KMS is claimed.

## Exact next action

1. Reconstruct exact LAB-084 `provider_rotation_recovery/{protocol,supported}.py` and its corrected tests at merge-base `d2c9781f5a60dc9b8b94fc8dba651f804a73e509`, together with the already-known LAB-036/080/082/083 implementation dependency closure; verify executable/test files by Git blob identity and execute the complete corrected LAB-084 suite.
2. Repeat cumulatively for LAB-085 provider-recovery-authority lifecycle.
3. Fetch the then-current PR #165 HEAD and execute all LAB-086 real-schema tests, explicitly including `test_public_rotation_history_guard.py`, migration v4 root coauthorization/restart, stale-public rebinding, scrubbed-prefix/asymmetric-suffix, forged-proof/stale-writer/direct-surface, strict-fence conflict algorithms, final single-snapshot verification and rotation races.
4. Run unsafe legacy-promotion seed and `python -m compileall` over the complete reconstructed closure.
5. Perform a fresh full audit focused on cutoff/root/public proof substitution, pre-existing-corruption guards on every consequential writer, alternate supported mutation entry points, transaction-scoped fence removal/restoration, predecessor/root binding, restart snapshots and rotation races. Re-check branch/main divergence and integrate only after the full gate is clean.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; current-head public-rotation history guard is fixed and focused-checked, full merged-stack gate remains.
- #166 / LAB-087 — READY; establish/enforce the SQLite schema-control trust boundary behind post-cutoff authority fences.
- #167 / LAB-088 — READY; fix LAB-083 invalid-known-signer noise consuming signer identity before cryptographic validation.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
