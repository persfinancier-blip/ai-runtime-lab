# Current Lab State

Last updated: 2026-08-26

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085.
- Active priority: Issue #163 / LAB-086 — IN_PROGRESS.
- Branch: `lab/086-asymmetric-break-glass-history`.
- Draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Current observed PR HEAD: `4d3da21ef2f8c0f782f5ce0146a04aaea0b62251`.
- PR remains draft; lower-evidence cardinality runtime fix is now published, but the exact real-ledger current-head gate is still incomplete.
- Parallel LAB-087/#166 remains IN_PROGRESS; its previously executed exact authorizer/process/filesystem slice was 12/12 PASS.

## Last completed step

Closed the pre-cutoff lower-evidence cardinality implementation blocker at the runtime level.

The branch already contained a red real-ledger regression and staged patch showing that LAB-082/LAB-083 reference-driven verification could miss orphan durable rows in `asymmetric_provider_transitions`, `provider_rotation_threshold_proofs`, and analogous root-transition evidence. Before touching runtime, the exact current `migration_guard.py` was reconstructed locally. The first local reconstruction differed only by a final newline; preserving the repository's no-final-newline form produced the exact current Git blob `5a5bb928b39a96f93f019b103b483dfb9bf43c6d`.

Applied the staged cardinality change to those exact bytes. Candidate blob: `2ae3df05271385f1a0dd03d7ed85b86ec0ff72e2`; `py_compile` passed.

Executed a focused red→green method/SQLite harness against exact old source and candidate. The old guard accepted orphan provider-transition, orphan threshold-proof, and orphan root-transition rows. The candidate rejected all three while still accepting bootstrap-only state and a valid successor state with matching root/provider transitions and threshold proof. Result: `FOCUSED RED->GREEN: PASS`.

Published the byte-audited candidate through the normal Contents API. Commit `4d3da21ef2f8c0f782f5ce0146a04aaea0b62251`; GitHub returned content blob exactly `2ae3df05271385f1a0dd03d7ed85b86ec0ff72e2`.

This focused run proves the cardinality invariant and exact publication, but it is not a substitute for the still-required real-ledger `test_pre_cutoff_lower_evidence_cardinality.py` execution in the full LAB-080→086 dependency closure.

## Evidence produced / reconfirmed

- Exact old migration guard reconstructed locally: `5a5bb928b39a96f93f019b103b483dfb9bf43c6d`.
- Exact published migration guard after fix: `2ae3df05271385f1a0dd03d7ed85b86ec0ff72e2`.
- Publication commit / current PR HEAD: `4d3da21ef2f8c0f782f5ce0146a04aaea0b62251`.
- Focused exact-old → candidate red/green harness: PASS.
  - old orphan provider transition: accepted;
  - candidate orphan provider transition: rejected;
  - old orphan threshold proof: accepted;
  - candidate orphan threshold proof: rejected;
  - old orphan root transition: accepted;
  - candidate orphan root transition: rejected;
  - bootstrap-only and valid-successor states: accepted by candidate.
- Candidate `py_compile`: PASS.
- Exact real-ledger regression already present on branch: `tests/test_pre_cutoff_lower_evidence_cardinality.py` blob `d2ff264ebbce0611805b880949478df4e5cef6a1`.
- Cumulative exact lower-stack evidence remains: LAB-080 18/18, LAB-082 28/28, LAB-083 24/24, LAB-084 17/17, LAB-085 core 12/12, asymmetric-custody 8/8, public/final 11/11; lower unsafe baselines failed as intended.
- Earlier LAB-086 exact/focused evidence for strict-fence, migration guard, scrubbed-prefix/final-writer and other published fixes remains recorded in Issue #163 / PR #165.

## Known blockers / constraints

- Remaining merge gate: execute the published cardinality fix against the exact real-ledger closure, then run the full current-head LAB-086 migration/suffix/final-supported suite, unsafe seed, compileall and final audit.
- Direct shell GitHub transport remains unavailable; connector blob/content reconstruction is the supported exact-source fallback and is not an owner blocker.
- The focused cardinality harness uses the exact runtime method and real SQL relations but intentionally stubs unrelated imported authorities; it does not count as the real-ledger regression.
- LAB-086 SQL fences cover audited supported/DML paths, not arbitrary same-privilege schema/DDL authority; LAB-087/#166 owns that boundary.
- LAB-088/#167 signer-noise, LAB-090/#169 provider handoff freshness, and LAB-091/#170 mutable shared-anchor/new-receipt authorization remain separate follow-ups.
- Logical SQL scrubbing is not forensic erasure; whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. Reconstruct the exact current PR dependency closure required by `test_pre_cutoff_lower_evidence_cardinality.py` using connector blob/content reads and verify executable files by `git hash-object`.
2. Execute `test_pre_cutoff_lower_evidence_cardinality.py` green against published migration guard blob `2ae3df05271385f1a0dd03d7ed85b86ec0ff72e2`.
3. Execute current `test_suffix.py` and all remaining LAB-086 real-schema migration/final-supported/security modules on the same closure, then unsafe legacy-promotion seed and full compileall.
4. Perform a fresh security audit focused on reverse evidence cardinality, cutoff/root/public proof binding, alternate supported mutation paths, transaction-scoped thaw/restoration, restart snapshots and rotation races.
5. Re-check branch/main divergence. Keep PR #165 draft until the complete current-head gate is clean; only then mark ready and integrate.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; lower-evidence cardinality runtime fix published byte-exact, real-ledger current-head gate remains.
- #166 / LAB-087 — IN_PROGRESS; SQLite schema-control/process boundary work.
- #167 / LAB-088 — READY; threshold signer-noise robustness.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — READY; mutable shared-ledger plus new provider-receipt writer authorization.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
