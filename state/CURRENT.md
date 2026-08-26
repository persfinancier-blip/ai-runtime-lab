# Current Lab State

Last updated: 2026-08-26

## Active objective

LAB-086 — migrate historical break-glass recovery from durable LAB-084/LAB-085 symmetric/HMAC authority to an authenticated cutoff plus Ed25519 public-only history, without auto-promoting legacy rows or weakening root/recovery continuity.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-085 and LAB-087.
- Active priority: Issue #163 / LAB-086 — IN_PROGRESS.
- Branch: `lab/086-asymmetric-break-glass-history`.
- Draft PR: #165 `[LAB-086] Asymmetric break-glass proof migration`.
- Current observed PR HEAD: `54e7d2d8cd46e30a0a2455b375cc1fa658570c83`.
- PR remains draft; exact real-ledger current-head gate is incomplete and a new pre-cutoff proof-cardinality blocker is staged but not yet applied to runtime.
- LAB-088 / Issue #167 remains IN_PROGRESS on draft PR #172.
- LAB-091 / Issue #170 remains IN_PROGRESS on draft PR #173.

## Last completed step

Resumed LAB-086 and performed a fresh migration-boundary completeness audit. Found that `_verify_lower_evidence_cardinality_locked()` rejects unexplained lower LAB-082/LAB-083 root/provider/threshold rows before cutoff, but does not reject LAB-086's own post-cutoff proof rows already present before migration:

- `provider_asymmetric_break_glass_proofs`;
- `provider_asymmetric_recovery_public_root_proofs`.

This is a real persistent fail-closed correctness/availability blocker. Pre-cutoff `_verify_lab086_locked()` verifies LAB-085 compatibility history only; `migration_guard.establish()` can otherwise sign/commit the cutoff while these unexplained LAB-086 rows remain outside the signed migration projection.

Published to PR #165:
- real-ledger regression `experiments/asymmetric_break_glass_history/tests/test_pre_cutoff_lab086_proof_cardinality.py`, commit `ec8029a9cf46aa00aa2f86d797e75ff02b28156d`;
- research note, commit `872f7ae9294798f1b855c717daba603389178075`;
- exact minimal patch file, commit/current HEAD `54e7d2d8cd46e30a0a2455b375cc1fa658570c83`.

Executed a focused SQLite/cardinality counterexample: current logic accepts clean state and both orphan LAB-086 proof-table cases; the staged invariant accepts clean state and blocks both orphan tables. This is focused evidence, not the full real-ledger test.

Byte-exact reconstruction of current `migration_guard.py` succeeded locally. Repository source (no final newline) hashed exactly to current Git blob `2ae3df05271385f1a0dd03d7ed85b86ec0ff72e2`. Applying only the staged invariant produced candidate blob `7db4b53ff5d85483a4937b17d1d039fe954a9728`; `py_compile` passed.

The runtime file was not rewritten in this run because the available connector exposes only whole-file replacement and no safe line/file patch endpoint. The patch + candidate hash are durable; do not perform an unverified manual rewrite.

## Evidence produced / reconfirmed

LAB-086 cumulative exact lower-stack evidence remains:
- LAB-080 18/18 PASS.
- LAB-082 28/28 PASS.
- LAB-083 24/24 PASS on pre-LAB-088 source.
- LAB-084 17/17 PASS.
- LAB-085 core 12/12 PASS, asymmetric-custody 8/8 PASS, public/final 11/11 PASS.
- Exact standalone LAB-086 corrected suite previously passed 12/12; unsafe legacy-auto-promotion seed failed as intended.
- Current published LAB-086 migration guard blob is still `2ae3df05271385f1a0dd03d7ed85b86ec0ff72e2`.
- Current least-privilege fence blob remains `5da01e28a9f813a136d138637f855940f04aab46`.
- Current suffix blob remains `44847bde53b9f7b0e2fbcbab37d36dc992f497b2`.
- Current final-supported blob remains `ceb7f48a55a931ba9923cac77d4ebf6c4cd2cfec`.
- New staged migration-guard candidate blob: `7db4b53ff5d85483a4937b17d1d039fe954a9728`, compile PASS.
- New focused red→green SQL/cardinality evidence: current accepts both LAB-086 orphan proof tables; staged candidate blocks both and preserves clean state.

LAB-088 exact evidence remains 22/22 focused/core PASS + compileall; draft PR #172 still needs supported/downstream compatibility.

LAB-087 is merged/DONE with final exact 14/14 PASS + compileall.

LAB-091 reference evidence remains 11/11 PASS + compileall; unsafe raw-DML seed failed as expected; real LAB-080/LAB-082 integration remains.

## Known blockers / constraints

- New LAB-086 blocker must be applied to runtime before any merge gate can be considered clean. Safe publication condition: current source blob must still equal `2ae3df...`; the resulting published blob must equal `7db4b53...`.
- After publication, execute the new real-ledger `test_pre_cutoff_lab086_proof_cardinality.py`, then the full current-head migration/suffix/final-supported/security suite from one exact LAB-080→086 dependency closure.
- Direct shell/raw GitHub transport remains unavailable. Connector reads work; connector whole-file rewrite is available but should not be used for this large source unless byte identity can be guaranteed.
- PR #165 is substantially diverged from current `main`; do not reconcile/integrate until the complete test/security gate is clean.
- LAB-088 PR #172 remains draft pending downstream regressions.
- LAB-091 PR #173 remains draft pending real supported-path integration; its SQL UDF/trigger scheme depends on LAB-087 sole-writable-handle process/filesystem boundary.
- LAB-090/#169 provider handoff freshness remains a separate correctness follow-up.
- Logical SQL scrubbing is not forensic erasure; whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. Re-fetch branch `migration_guard.py`; proceed only if its blob is still `2ae3df05271385f1a0dd03d7ed85b86ec0ff72e2`.
2. Apply the durable patch `research/2026-08-26-lab086-pre-cutoff-own-proof-cardinality.patch` using a byte-safe whole-file path. Verify GitHub returns exactly candidate blob `7db4b53ff5d85483a4937b17d1d039fe954a9728`.
3. Execute exact real-ledger `test_pre_cutoff_lab086_proof_cardinality.py`; then run current `test_pre_cutoff_lower_evidence_cardinality.py`, `test_suffix.py`, migration-guard/final-supported/security modules, unsafe legacy-promotion seed, and full compileall on the same LAB-080→086 closure.
4. Perform the final LAB-086 security audit and branch/main reconciliation only after tests are clean; keep PR #165 draft until then.
5. If the runtime publication path is still unavailable without byte-risk, continue LAB-091 real integration rather than weakening the LAB-086 publication standard.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; new pre-cutoff LAB-086-own-proof cardinality blocker staged, runtime fix not yet published.
- #166 / LAB-087 — DONE; merged as `65a44cc8d12cf37d04d9cd59398b456d7429cc31`.
- #167 / LAB-088 — IN_PROGRESS; draft PR #172.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — IN_PROGRESS; draft PR #173, reference writer exact-tested, real integration remains.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.