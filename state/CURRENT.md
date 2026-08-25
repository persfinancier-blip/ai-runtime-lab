# Current Lab State

Last updated: 2026-08-25

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085.
- Active: Issue #163 / LAB-086 — IN_PROGRESS.
- Branch: `lab/086-asymmetric-break-glass-history`.
- Draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Current observed branch HEAD: `fb26868f084a6f61c1b4d3e7281159c5de1f44b5`.
- PR remains draft/mergeable; full current-head real-ledger gate has not passed.

## Last completed step

Fresh audit found an ordinary-DML gap in the authenticated migration metadata itself. After a completed cutoff, `provider_asymmetric_break_glass_boundary`, `provider_asymmetric_break_glass_legacy_projection`, and `provider_asymmetric_break_glass_root_proof` were cryptographically checked on restart but were not DML-fenced. Executable pre-fix probes confirmed UPDATE/DELETE/`INSERT OR REPLACE` mutation paths, creating persistent fail-closed corruption.

Built and executed a minimal candidate from the exact branch `strict_fence.py` blob `1422f4435913cd95c37a38a0a62c2116f8e80476`. The candidate installs non-thawable INSERT/UPDATE/DELETE guards on all three metadata singletons. Guards activate only after all three rows exist, preserving the current atomic migration order `projection -> boundary -> root proof`; final-writer thaw deliberately does not remove them.

The runtime file is NOT updated on the branch yet. Instead, durable branch artifacts record the exact tested change so the next run can apply it without repeating the audit:
- regression commit `d717ff6573513219a71a637ae317a4b894120137`;
- exact unified patch/current branch HEAD `fb26868f084a6f61c1b4d3e7281159c5de1f44b5`;
- patch path `research/2026-08-25-lab086-migration-metadata-dml-fence.patch`.

## Evidence produced / reconfirmed

- Exact original `strict_fence.py` reconstructed locally and reconfirmed by `git hash-object`: `1422f4435913cd95c37a38a0a62c2116f8e80476`.
- Tested patched candidate blob: `7c8387f050bf44894ae02a0a9b90f3bfe09dc003`.
- Previous strict-fence suite + new metadata-fence suite on the candidate: **13/13 PASS**.
- Focused metadata matrix: UPDATE/DELETE/`INSERT OR REPLACE`/UPSERT across all three singleton tables all BLOCKED.
- Existing migration insertion order `projection -> boundary -> root proof`: PASS.
- Final-writer `remove_public_mutation_fence_locked()` leaves migration metadata guards active: PASS.
- Patched `strict_fence.py` `py_compile`: PASS.
- Full temporary-workspace compileall was not counted because an unrelated, intentionally incomplete local `migration_guard.py` reconstruction remained in that scratch workspace.
- Issue #163 evidence comment: `5409153172`.
- Lower-stack exact gate remains complete from prior observed runs: LAB-080 18/18, LAB-082 28/28, LAB-083 24/24, LAB-084 17/17, LAB-085 core 12/12, LAB-085 asymmetric-custody 8/8, LAB-085 public/final 11/11.
- Direct shell GitHub transport remains unavailable; GitHub connector/Contents API work.

## Known blockers / constraints

- The new migration-metadata regression is expected to fail on current branch runtime code until the recorded patch is applied to exact blob `1422f443...`.
- After applying it, re-fetch `strict_fence.py` and require Git blob `7c8387f050bf44894ae02a0a9b90f3bfe09dc003` before counting the 13/13 focused evidence as branch evidence.
- Full current-head real-ledger migration/suffix/final-supported suite, unsafe legacy-promotion seed, full compileall and final security audit remain mandatory before merge.
- LAB-086 SQLite fences cover audited ordinary DML/stale supported paths, not arbitrary same-privilege SQLite schema/DDL authority. LAB-087/#166 owns that stronger boundary.
- Logical SQL scrubbing is not forensic erasure; whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. Apply `research/2026-08-25-lab086-migration-metadata-dml-fence.patch` to exact branch `strict_fence.py` blob `1422f4435913cd95c37a38a0a62c2116f8e80476` using a safe supported path; do not rewrite from an unverified source.
2. Re-fetch the published file and require Git blob `7c8387f050bf44894ae02a0a9b90f3bfe09dc003`; then run exact `test_strict_fence.py + test_migration_metadata_dml_fence.py` and compile the module.
3. Resume the full current-head real-ledger migration/suffix/final-supported suite, unsafe seed and complete compileall.
4. Perform a final security audit of migration metadata, alternate DML entry points, consequential writers, restart verification and branch/main divergence. Keep PR #165 draft until all gates are clean.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; migration metadata DML blocker found; tested patch durable but runtime application still pending.
- #166 / LAB-087 — READY; SQLite schema-control trust boundary.
- #167 / LAB-088 — READY; threshold signer-noise robustness.
- #168 / LAB-089 — CLOSED `not_planned`.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
