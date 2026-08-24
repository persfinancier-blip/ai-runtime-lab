# Current Lab State

Last updated: 2026-08-24

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085.
- Active: Issue #163 / LAB-086 — IN_PROGRESS.
- Branch: `lab/086-asymmetric-break-glass-history`.
- Draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Current observed PR HEAD: `6ef4a0d67017c067d159f042ad578f6233783308`.
- PR is mergeable but remains draft; the full current-head merged-stack exact-source regression gate has not passed.

## Last completed step

A fresh consequential-writer audit found a new cross-layer gap in the final LAB-086 wrapper. `SupportedFencedAsymmetricBreakGlassLedger` guarded public-recovery rotation, but normal root rotation and provider-generation rotation were still delegated through `__getattr__` to lower LAB-083/LAB-084 writers. Those writers are valid for their own layers but do not know about LAB-086 migration/asymmetric history, so a pre-existing corrupted LAB-086 proof could survive a newly committed root/provider successor and only fail later on restart.

The branch now overrides both `rotate_rotation_authority()` and `rotate_provider()`. Each path uses one `BEGIN IMMEDIATE`, rejects PREPARED work, installs/asserts the current public mutation fence, runs `_verify_lab086_locked(q)` before mutation and again before commit, and commits only if the complete LAB-086 history remains valid. Provider runtime `attested`/`signer` fields are changed only after successful commit.

Added `test_inherited_writer_history_guard.py`: it creates a valid migrated/asymmetric history, corrupts an existing asymmetric proof, then attempts a normal root rotation and a provider-generation rotation; both must fail with zero durable changes.

## Evidence produced / reconfirmed

- Cumulative exact merged-stack evidence already proven in prior runs remains: LAB-080 **18/18 PASS**, LAB-082 **28/28 PASS**, LAB-083 **24/24 PASS**, LAB-084 **17/17 PASS**, LAB-085 core **12/12 PASS**; their unsafe baselines failed as expected and recorded compileall passes remain valid for those exact lower blobs.
- New exact published LAB-086 bytes were reconstructed locally and matched Git blobs:
  - `final_supported.py` `0f95c698b45246d2582937d04ff3909ce5cdc82d`
  - `test_inherited_writer_history_guard.py` `ed84a87815112c8b0a6d37ff8ad94bb7f3bf6328`
- `py_compile` on both exact files: PASS.
- Focused AST guard check: both new consequential writers contain two `_verify_lab086_locked` calls and a commit path.
- Focused transaction/control-flow harness on exact `final_supported.py`: corrupt-history precheck blocked normal root rotation with **0 mutations**; blocked provider rotation with **0 mutations** and left runtime signer/attested unchanged.
- Issue #163 comment records the defect, fix and focused evidence.
- Fresh branch/main compare: **ahead 79 / behind 35**; all 25 PR paths are additions with no path overlap against current main.

## Known blockers / constraints

- Full merge gate is still incomplete after the new HEAD: finish exact LAB-085 public-custody/supported/final tests, then execute all current LAB-086 real-schema tests including the new inherited-writer regression, unsafe seed, full compileall and final audit.
- Focused exact evidence above is not a substitute for the merged-stack run.
- File-by-file connector reconstruction is slower because shell GitHub transport is unavailable; connector reconstruction works and is not an owner blocker.
- LAB-083/LAB-084 signer-noise issue #167 is fail-closed DoS/robustness and remains separate unless downstream results invalidate LAB-086.
- LAB-086 SQLite fences protect against stale/alternate supported mutation paths, not arbitrary same-privilege raw SQLite DDL. That broader boundary is LAB-087 / #166.
- Logical SQL scrubbing is not forensic erasure; WAL/filesystem remnants remain outside the claim. Whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. Finish connector reconstruction of exact LAB-085 `asymmetric_custody.py`, `custody_break_glass.py`, `supported.py`, `public_custody_supported.py`, `final_supported.py` plus their five corrected test modules; verify blob identities, execute all remaining LAB-085 corrected tests together and compileall.
2. Reconstruct the then-current PR #165 LAB-086 executable/test files and run the complete real-schema suite, explicitly including `test_inherited_writer_history_guard.py`, public-rotation history guard, migration v4 root coauthorization/restart, stale-public rebinding, scrubbed-prefix/asymmetric-suffix, forged-proof/stale-writer/direct-surface, strict-fence conflict algorithms, final verification snapshot and rotation races.
3. Run LAB-086 unsafe legacy-promotion seed and compileall over the complete closure.
4. Perform a fresh audit of every consequential writer/restart path, including normal root rotation and provider rotation in addition to public recovery/asymmetric recovery, plus cutoff/root/public proof substitution, fence removal/restoration and restart snapshots.
5. Re-check branch/main divergence. Keep PR #165 draft until the entire current-head gate is clean; only then mark ready and integrate.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; new inherited normal-root/provider writer guard is published and focused-verified; full merged-stack gate remains.
- #166 / LAB-087 — READY; establish/enforce the SQLite schema-control trust boundary behind post-cutoff authority fences.
- #167 / LAB-088 — READY; signer-noise robustness in LAB-083/LAB-084 threshold collectors.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
