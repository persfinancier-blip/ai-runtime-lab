# Current Lab State

Last updated: 2026-08-25

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085.
- Active: Issue #163 / LAB-086 — IN_PROGRESS.
- Branch: `lab/086-asymmetric-break-glass-history`.
- Draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Current observed branch HEAD: `c258cd2c0e2f0ffb91a9280778bef7fa74daac42`.
- Runtime `strict_fence.py` is still blob `7c8387f050bf44894ae02a0a9b90f3bfe09dc003`; the new evidence-DML fix is staged/tested but not yet applied to that runtime file.

## Last completed step

Fresh current-head audit found another ordinary-DML durable-integrity gap. `provider_asymmetric_break_glass_proofs` and `provider_asymmetric_recovery_public_root_proofs` are recognized as post-cutoff-only evidence for the pre-cutoff orphan check, but current `strict_fence.py` does not freeze already committed rows in either table against UPDATE/DELETE/replacement. A stale/raw DML actor can therefore corrupt/delete authenticated restart evidence; later crypto verification fails closed, so this is persistent fail-closed DoS rather than forged authority.

Durable artifacts added to PR #165:
- regression `experiments/asymmetric_break_glass_history/tests/test_post_cutoff_evidence_dml_fence.py`, commit `fe9229aa64065b3484b4b3cd9f43595e5c5d2b3a`;
- design note `research/2026-08-25-lab086-post-cutoff-evidence-dml-fence.md`, commit `805642302b42b00b7ed7c108346a22669630aa24`;
- staged patch `research/2026-08-25-lab086-post-cutoff-evidence-dml-fence.patch`, current branch HEAD `c258cd2c0e2f0ffb91a9280778bef7fa74daac42`.

The exact current runtime `strict_fence.py` was reconstructed from connector chunks and locally verified by `git hash-object` as `7c8387f050bf44894ae02a0a9b90f3bfe09dc003`. The staged fix was applied locally to those exact bytes; candidate blob is `6992a55a1dcc61f4b2f066ff1844f68a7c9610be` and `py_compile` passed.

Executed existing exact `test_strict_fence.py` plus the new regression against that candidate: **12/12 PASS** (10 existing + 2 new). The new tests cover UPDATE, DELETE, `INSERT OR REPLACE`, and UPSERT for both evidence tables while requiring the original digest to remain unchanged.

Correct fence shape: new proof insertion remains allowed only for a previously absent primary key; insertion against an existing key is denied (blocking REPLACE/UPSERT), UPDATE/DELETE are always denied after cutoff, these evidence-history triggers are never thawed by final writers, and `assert_public_mutation_fence_locked()` requires all six triggers.

No branch-runtime PASS is claimed for this fix yet because the 800-line runtime file has not been rewritten. Avoid an unaudited full-file Contents API rewrite; apply the already durable patch to the exact known blob and verify the published result before claiming success.

## Evidence produced / reconfirmed

- Current branch runtime before fix: `strict_fence.py` blob `7c8387f050bf44894ae02a0a9b90f3bfe09dc003`.
- Local exact-byte patched candidate: `6992a55a1dcc61f4b2f066ff1844f68a7c9610be`.
- Candidate focused regression: **12/12 PASS**; compile of patched runtime PASS.
- Issue #163 audit comment: `5410344104`.
- Lower-stack exact gate remains complete: LAB-080 18/18, LAB-082 28/28, LAB-083 24/24, LAB-084 17/17, LAB-085 core 12/12, LAB-085 asymmetric-custody 8/8, LAB-085 public/final 11/11.
- Previous branch-exact migration-metadata strict-fence gate remains 13/13 PASS.
- Direct shell GitHub transport remains unavailable; connector/Contents API work and are not owner blockers.

## Known blockers / constraints

- New post-cutoff evidence-DML blocker is fixed only in the tested local candidate/staged patch; branch runtime still needs exact application + published blob verification.
- After that, the full current-head real-ledger migration/suffix/final-supported suite, unsafe legacy-promotion seed, complete compileall, and final security audit remain mandatory before merge.
- SQLite fences cover audited ordinary DML/stale supported paths, not arbitrary same-privilege SQLite schema/DDL authority; LAB-087/#166 owns that stronger boundary.
- LAB-083/LAB-084 signer-noise robustness remains LAB-088/#167 and is fail-closed availability work.
- Logical SQL scrubbing is not forensic erasure; whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. Re-fetch branch `strict_fence.py` and require blob `7c8387f050bf44894ae02a0a9b90f3bfe09dc003`; apply the durable post-cutoff-evidence patch without unrelated rewrite. Verify published result equals the locally tested candidate blob `6992a55a1dcc61f4b2f066ff1844f68a7c9610be` (or re-run exact tests if formatting/content necessarily changes).
2. Execute exact branch `test_strict_fence.py` + `test_post_cutoff_evidence_dml_fence.py`; require 12/12 PASS and compileall.
3. Reconstruct current PR HEAD `migration_guard.py`, `suffix.py`, `final_supported.py` and remaining real-ledger LAB-086 tests on the already proven LAB-080→085 closure; execute migration v4/root coauthorization/restart, scrubbed-prefix/asymmetric-suffix, orphan/partial state, public-rotation cross-binding, inherited/direct surfaces, final verification snapshot, and rotation races.
4. Execute unsafe legacy-promotion seed + full compileall, then perform final security audit and branch/main divergence check. Fix every failure; only then mark PR #165 ready and integrate.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; new post-cutoff evidence DML blocker has regression + tested patch but branch runtime is not yet updated.
- #166 / LAB-087 — READY; SQLite schema-control trust boundary.
- #167 / LAB-088 — READY; threshold signer-noise robustness.
- #168 / LAB-089 — CLOSED `not_planned`.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
