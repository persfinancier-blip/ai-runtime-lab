# Current Lab State

Last updated: 2026-08-25

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085.
- Active: Issue #163 / LAB-086 — IN_PROGRESS.
- Branch: `lab/086-asymmetric-break-glass-history`.
- Draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Current observed PR HEAD: `f573e83fb9a75f9281ab31bbca3d40c41ab9368b`.
- PR remains draft; the new pre-cutoff orphan-evidence fix must pass the full real-ledger current-head gate before merge.

## Last completed step

Fresh source audit of the new pre-cutoff orphan-evidence guard found no constructor-only TOCTOU bypass. `AuthenticatedBreakGlassMigrationGuard.__init__`, `payload()`, and `establish()` each enter `_ensure_schema_locked()` under `BEGIN IMMEDIATE`; `strict_fence.install_public_mutation_fence_locked()` rejects rows in `provider_asymmetric_recovery_public_root_proofs` and `provider_asymmetric_break_glass_proofs` while no authenticated boundary exists. Therefore post-cutoff-only evidence inserted after guard construction but before `payload()/establish()` is rechecked at the consequential operation.

Direct shell GitHub transport was probed again in this run and failed at DNS (`Could not resolve host: github.com`); GitHub connector remains usable and is not an owner-level blocker.

Branch/main compare was refreshed: diverged, ahead 101 / behind 51. All 34 PR files remain additions under LAB-086/research paths; no path-level conflict is visible in the compare.

## Evidence produced / reconfirmed

- Exact current `strict_fence.py` blob remains `af65f0515681455ffe38bd1ea41913daeda460e3`.
- Real-ledger orphan regression blob remains `ea6285408721fb6e6c1f9de2b2b3dc3ceb12b72a`.
- Exact isolated pre-cutoff orphan-evidence regression previously passed 4/4; strict-fence slice previously passed 14/14; compileall PASS.
- Lower-stack exact gate remains complete: LAB-080 18/18, LAB-082 28/28, LAB-083 24/24, LAB-084 17/17, LAB-085 core 12/12, LAB-085 asymmetric-custody 8/8, LAB-085 public/final 11/11.
- Earlier unchanged LAB-086 evidence remains: standalone 12/12, fence/inherited/root-head slice and final single-snapshot contract PASS; unsafe legacy auto-promotion failed as intended.
- No new test result is claimed in this run; the fresh result is source/audit evidence plus branch divergence refresh.

## Known blockers / constraints

- The updated real-ledger orphan-evidence tests have not yet executed in the complete LAB-085/LAB-086 dependency closure. This is the immediate merge gate.
- Remaining LAB-086 merge gate: current-head migration/suffix/final-supported real-schema tests, unsafe legacy-promotion seed, full compileall over the complete closure, and one final security audit.
- Direct shell GitHub transport remains unavailable; connector reconstruction works.
- LAB-083/LAB-084 signer-noise issue #167 remains separate fail-closed DoS/robustness work.
- LAB-086 SQLite fences cover stale/alternate supported mutation paths and audited DML, not arbitrary same-privilege raw SQLite DDL/schema control; that broader boundary is LAB-087/#166.
- Logical SQL scrubbing is not forensic erasure. Whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. Reconstruct current PR #165 HEAD `f573e83fb9a75f9281ab31bbca3d40c41ab9368b` migration/suffix dependency closure and execute `test_orphan_projection_regression.py` first against the real supported ledger.
2. Execute all remaining current-head migration v4 root-coauthorization/restart, scrubbed-prefix/asymmetric-suffix, forged-proof/stale-writer/direct-surface, lower/public-history guards and rotation-race tests. Re-run strict-fence modules only if dependencies changed.
3. Execute unsafe legacy-promotion expected-failure seed and full compileall over the complete reconstructed closure.
4. Perform a fresh full security audit of every consequential/restart writer plus branch/main divergence. Fix every failure before changing PR #165 out of draft.
5. If the full gate is clean, mark PR #165 ready and integrate by normal merge when available; otherwise use only the documented audited file-scoped Contents API fallback after exact conflict checking.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; pre-cutoff orphan post-cutoff-evidence blocker fixed; real-ledger current-head gate remains.
- #166 / LAB-087 — READY; SQLite schema-control trust boundary.
- #167 / LAB-088 — READY; threshold signer-noise robustness.
- #168 / LAB-089 — CLOSED `not_planned`.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
