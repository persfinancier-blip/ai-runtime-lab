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

A fresh partial-state audit found and fixed another migration-boundary DoS path.

Before this fix, the migration guard rejected an orphan boundary root proof and orphan legacy projection, but it did not reject LAB-086-only post-cutoff evidence before the authenticated cutoff existed. In particular, a row in `provider_asymmetric_recovery_public_root_proofs` or `provider_asymmetric_break_glass_proofs` could exist pre-cutoff; migration could then establish the boundary, and the later full suffix verifier would reject that retained row as orphan evidence. This turns impossible partial state into a persistent fail-closed restart failure.

The branch now treats those tables as post-cutoff-only evidence. `install_public_mutation_fence_locked()` fails closed if either table contains a row while no authenticated boundary exists. This check runs during migration-guard schema/fence setup before cutoff establishment. Legitimate post-cutoff final-writer paths are unaffected because the boundary already exists.

Published branch changes:
- strict-fence fix commit `11eeea55ef52a3bc572905c9dc72810a53cdfa12`;
- isolated regression commit `d07d6322647e0bdcdad0a53bb3a297d0eb110278`;
- real-ledger regression update / current HEAD `f573e83fb9a75f9281ab31bbca3d40c41ab9368b`.

## Evidence produced / reconfirmed

- Exact current `strict_fence.py` blob: `af65f0515681455ffe38bd1ea41913daeda460e3`; locally reconstructed bytes matched exactly.
- Exact isolated regression blob `test_pre_cutoff_orphan_evidence_regression.py`: `8e54574ef671be1bb14734b98fe29b4bbd5d43d7`; locally reconstructed bytes matched exactly.
- Exact isolated new regression: **4/4 PASS**; compileall PASS.
- Existing strict-fence semantics re-executed together with the new regression: **14/14 PASS**. The existing test module was source-equivalent in this focused run; the new implementation and new regression were exact Git blobs.
- Real-ledger orphan regression was extended (blob `ea6285408721fb6e6c1f9de2b2b3dc3ceb12b72a`) so both LAB-086-only proof classes must block `guard.payload()` on the actual LAB-085/LAB-086 schema; that full dependency-closure execution remains pending.
- Lower-stack exact gate remains complete:
  - LAB-080 18/18 PASS.
  - LAB-082 28/28 PASS.
  - LAB-083 24/24 PASS.
  - LAB-084 17/17 PASS.
  - LAB-085 core 12/12 PASS.
  - LAB-085 asymmetric-custody 8/8 PASS.
  - LAB-085 public/final 11/11 PASS.
- Earlier current-head LAB-086 evidence still stands for unchanged paths: standalone 12/12 PASS; prior fence/inherited/root-head slice and final single-snapshot contract passed; unsafe legacy auto-promotion failed as intended.

## Known blockers / constraints

- The new real-ledger orphan-evidence tests have not yet executed in the complete LAB-085/LAB-086 dependency closure. This is the immediate merge gate.
- Remaining LAB-086 merge gate: current-head migration/suffix/final-supported real-schema tests, unsafe legacy-promotion seed, full compileall over the complete closure, and one final security audit.
- Direct shell GitHub transport remains unavailable; GitHub connector reconstruction works and is not an owner-level blocker.
- LAB-083/LAB-084 signer-noise issue #167 remains fail-closed DoS/robustness and separate from LAB-086 unless downstream tests invalidate the candidate.
- LAB-086 SQLite fences cover stale/alternate supported mutation paths and audited DML, not arbitrary same-privilege raw SQLite DDL/schema control; that broader boundary is LAB-087/#166.
- Logical SQL scrubbing is not forensic erasure. Whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. Reconstruct current PR #165 HEAD `f573e83fb9a75f9281ab31bbca3d40c41ab9368b` migration/suffix dependency closure and execute the updated `test_orphan_projection_regression.py` first against the real supported ledger.
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
