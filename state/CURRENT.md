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
- PR remains draft; full current-head real-ledger regression/compileall gate has not passed.

## Last completed step

Performed another fresh source/security pass over the current consequential/restart path and checked two lower-layer analogues that could have undermined the post-cutoff fence.

1. Provider-head analogue: exact lower `AsymmetricProviderHistory.rotate()` writes `generation -> asymmetric_provider_transitions -> asymmetric_provider_head` in one transaction. LAB-086 denies the transition INSERT after cutoff. A focused SQLite execution using that exact write ordering observed `IntegrityError`, rollback of the already inserted generation, unchanged provider head, and no surviving transition. Therefore the fact that `asymmetric_provider_head` itself is not separately fenced is not a supported-writer bypass.
2. Provider-threshold stale-root analogue: the supported provider rotation path constructs threshold authorization from `rotation_authority.current_locked(q)` at write time; after cutoff, lower provider threshold/transition INSERTs are fenced. The durable verifier can verify historical proofs under their referenced historical root, but no stale-root supported writer path was established. Arbitrary same-privilege SQL tampering remains LAB-087/#166 rather than an LAB-086 claim.

No new privilege escalation or stale-supported-writer bypass was established. Direct shell GitHub transport was probed again and still fails DNS; GitHub connector access remains healthy. No new full-stack test PASS is claimed in this run.

Fresh branch/main compare: diverged, ahead 101 / behind 53. All 34 PR paths remain additions under LAB-086/research paths; no path-level overlap with current `main` is visible.

## Evidence produced / reconfirmed

- Current PR HEAD: `f573e83fb9a75f9281ab31bbca3d40c41ab9368b`.
- Current audited implementation blobs:
  - `migration_guard.py` `5a5bb928b39a96f93f019b103b483dfb9bf43c6d`;
  - `strict_fence.py` `af65f0515681455ffe38bd1ea41913daeda460e3`;
  - `suffix.py` `bb9f8e55fb03424ac19c152ae2d8aceaf2e1c078`;
  - `final_supported.py` `9f0198d2db85d08ec64f614d6288323c1d642383`.
- Lower-stack exact gate remains complete from prior observed runs: LAB-080 18/18, LAB-082 28/28, LAB-083 24/24, LAB-084 17/17, LAB-085 core 12/12, LAB-085 asymmetric-custody 8/8, LAB-085 public/final 11/11.
- Earlier unchanged LAB-086 evidence remains: standalone 12/12, strict/inherited/root-head fence slices, orphan/pre-cutoff evidence focused regressions, and final single-snapshot contract PASS; unsafe legacy auto-promotion failed as intended.
- Focused provider-writer SQLite result: transition fence blocked the stale lower sequence before head update; transaction rollback removed the inserted successor generation and preserved the old head.
- LAB-089/#168 is CLOSED `not_planned`: its same-root premise was invalid under the actual exact-successor supported writer.
- Fresh compare: ahead 101 / behind 53; all 34 PR files are additions with no visible path-level conflict against current main.
- Issue #163 fresh provider/stale-root audit report: comment `5406462344`.

## Known blockers / constraints

- Immediate LAB-086 merge gate remains exact current-head real-ledger execution: orphan projection/post-cutoff evidence, migration v4 root-coauthorization/restart, scrubbed-prefix/asymmetric-suffix, public/root/provider history guards, rotation races, unsafe seed and full compileall.
- No new full-stack test result is claimed in this run; source/semantic audit is not a substitute for execution.
- Direct shell GitHub transport remains unavailable; connector reconstruction works and is not an owner-level blocker.
- LAB-083/LAB-084 signer-noise issue #167 remains separate fail-closed DoS/robustness work.
- LAB-086 SQLite fences cover stale/alternate supported mutation paths and audited DML, not arbitrary same-privilege raw SQLite DDL/schema control; that broader boundary is LAB-087/#166.
- Logical SQL scrubbing is not forensic erasure. Whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. Reconstruct the exact current PR #165 HEAD dependency closure needed by `test_orphan_projection_regression.py` / `test_migration_guard.py` and execute the real supported-ledger tests first; verify executable files by Git blob identity.
2. Execute all remaining current-head migration/suffix/final-supported real-schema modules: cutoff/root coauthorization and restart, scrubbed-prefix/asymmetric suffix, forged-proof/stale/direct-surface cases, inherited/public history guards, strict conflict algorithms, final verification snapshot and rotation races.
3. Execute unsafe legacy-promotion expected-failure seed and full `python -m compileall` over the reconstructed closure.
4. Perform one final security audit of every consequential/restart writer plus branch/main divergence. Fix every failure before changing PR #165 out of draft.
5. If the full gate is clean, mark PR #165 ready and integrate by normal merge when available; otherwise use only the documented audited file-scoped Contents API fallback after exact conflict checking.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; current-head supported-writer audit remains clean, full real-ledger execution gate remains.
- #166 / LAB-087 — READY; SQLite schema-control trust boundary.
- #167 / LAB-088 — READY; threshold signer-noise robustness.
- #168 / LAB-089 — CLOSED `not_planned`.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
