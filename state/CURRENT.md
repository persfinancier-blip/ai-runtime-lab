# Current Lab State

Last updated: 2026-08-25

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085.
- Active: Issue #163 / LAB-086 — IN_PROGRESS.
- Branch: `lab/086-asymmetric-break-glass-history`.
- Draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Current observed branch HEAD: `76f37534cad26531284442e06d4a170bd4a8cad4`.
- PR remains draft; runtime `strict_fence.py` still has the broad thaw and the full current-head real-ledger gate has not passed.

## Last completed step

Fresh transaction-scoped-thaw audit found a least-privilege/correctness merge blocker. `remove_public_mutation_fence_locked()` currently drops more SQL capabilities than any supported consequential writer needs: committed inherited/public history UPDATE/DELETE guards and singleton-head INSERT/DELETE guards are removed together with the exact creation/head-UPDATE permissions required by rotation/recovery.

The actual lower primitives were audited. Required operations are only:
- root rotation: INSERT root authority + INSERT root transition + UPDATE root head;
- provider rotation: INSERT provider generation + INSERT threshold proof + INSERT provider transition + UPDATE provider head;
- public-recovery rotation: INSERT public authority + INSERT public transition + UPDATE public head;
- asymmetric break-glass: INSERT root authority + UPDATE root head + INSERT asymmetric recovery proof.

A focused SQLite counterexample was actually executed: current-source-equivalent broad thaw allowed UPDATE of an existing authenticated transition; creation-only thaw raised `sqlite3.IntegrityError` and preserved the old row.

The current exact `strict_fence.py` blob `02128fb866d7b4a3382622356f33e7b1739ff167` was reconstructed byte-for-byte locally. A deterministic minimal patch splits full reinstall cleanup from runtime thaw and narrows runtime capability to creation + head UPDATE only. Patched candidate blob is `5da01e28a9f813a136d138637f855940f04aab46`; it compiles and passed **13/13 focused tests** (`test_strict_fence` 10 + `test_transaction_scoped_thaw_minimality` 3).

The exact unified patch is durable in the PR at `research/2026-08-25-lab086-minimal-thaw.patch` (commit/current branch HEAD `76f37534cad26531284442e06d4a170bd4a8cad4`). Runtime `strict_fence.py` has intentionally not been rewritten yet because the available GitHub connector exposes only whole-file Contents API replacement for existing files; direct shell GitHub transport is unavailable. Do not claim the candidate is published until GitHub returns content blob `5da01e28...`.

## Evidence produced / reconfirmed

- Exact current branch runtime blob before fix: `strict_fence.py` `02128fb866d7b4a3382622356f33e7b1739ff167`; local reconstruction hash matched exactly.
- Exact local minimal-thaw candidate blob: `5da01e28a9f813a136d138637f855940f04aab46`.
- Local patched candidate: `py_compile` PASS.
- Focused patched candidate gate: **13/13 PASS** (10 existing strict-fence cases + 3 minimal-thaw cases).
- New regression current blob: `test_transaction_scoped_thaw_minimality.py` `a25da2dc0c8382bd2dd3c295e1ae7b9b98dded2a`; it covers inherited history immutability, existing public-recovery history immutability, and public/root/provider head INSERT OR REPLACE + DELETE during thaw.
- Exact patch file is durable at `research/2026-08-25-lab086-minimal-thaw.patch`.
- Research note `research/2026-08-25-lab086-minimal-transaction-thaw.md` records the exact supported-writer capability matrix.
- Cumulative lower-stack exact evidence remains: LAB-080 18/18, LAB-082 28/28, LAB-083 24/24, LAB-084 17/17, LAB-085 core 12/12, asymmetric-custody 8/8, public/final 11/11; lower unsafe baselines failed as intended.
- Exact standalone LAB-086 corrected suite previously passed 12/12; post-cutoff proof-row creation exact gate passed 12/12 before this new blocker.

## Known blockers / constraints

- Runtime minimal-thaw fix is not yet published. The current branch `strict_fence.py` remains blob `02128fb8...`; the tested candidate is local blob `5da01e28...` plus a durable exact patch.
- Required safe publication: apply the saved patch to exact blob `02128fb8...` and accept the Contents API write only if returned content SHA is exactly `5da01e28a9f813a136d138637f855940f04aab46`.
- After publication, rerun exact branch `test_transaction_scoped_thaw_minimality.py` + complete strict-fence regression set, then resume the full real-ledger `migration_guard + suffix + final_supported` gate.
- Direct shell GitHub transport is unavailable; GitHub connector/Contents API is the supported fallback. The connector does not expose a line-patch/file-upload action for replacing an existing UTF-8 file.
- LAB-087/#166 owns arbitrary same-privilege SQLite DDL/schema control; LAB-088/#167 signer-noise; LAB-090/#169 provider handoff freshness; LAB-091/#170 mutable shared-anchor/new-receipt DML authorization.
- Logical SQL scrubbing is not forensic erasure; whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. Apply durable patch `research/2026-08-25-lab086-minimal-thaw.patch` to exact current runtime blob `02128fb8...` via a supported whole-file Contents API replacement; verify returned Git blob is exactly `5da01e28a9f813a136d138637f855940f04aab46`. If exact byte transfer cannot be guaranteed, do not perform a risky rewrite.
2. Reconstruct published source and execute `test_transaction_scoped_thaw_minimality.py` plus the complete current strict-fence regression set; require a clean gate.
3. Resume exact current-head real-ledger LAB-086 migration/suffix/final-supported suite on the proven LAB-080→085 dependency closure.
4. Run unsafe legacy-promotion seed, full compileall and final security audit; only then mark PR #165 ready/integrate.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; minimal-thaw blocker has exact red regression, exact patch, candidate hash and focused 13/13 evidence; runtime publication + full gate remain.
- #166 / LAB-087 — READY; SQLite schema-control trust boundary.
- #167 / LAB-088 — READY; threshold signer-noise robustness.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — READY; mutable/shared-ledger plus new provider-receipt ordinary-DML writer authorization.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
