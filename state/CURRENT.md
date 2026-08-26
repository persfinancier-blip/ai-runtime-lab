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
- PR remains draft; GitHub currently reports `mergeable=false` and the exact real-ledger current-head gate is incomplete.
- Parallel LAB-087/#166 remains IN_PROGRESS; its previously executed exact authorizer/process/filesystem slice was 12/12 PASS.

## Last completed step

Performed a fresh current-head continuation audit after the published lower-evidence cardinality fix.

Fresh branch/main compare is `ahead 146 / behind 87`; all 56 PR files are still additions, so the observed divergence remains path-nonoverlapping at the PR-file level even though GitHub currently reports the PR non-mergeable.

Re-audited the published cardinality guard together with the current least-privilege SQL fence and final consequential-writer composition. The reverse-cardinality check runs under the migration `BEGIN IMMEDIATE` before cutoff. After cutoff, inherited transition/proof creation is denied except during the verified final-writer transaction-scoped thaw; inherited history UPDATE/DELETE guards remain active during thaw. Migration metadata and committed post-cutoff evidence history remain non-thawable. No new privilege-escalation or stale-supported-writer bypass was found in this source pass.

Direct shell/raw GitHub transport remains unavailable. Connector reads work, but this runtime still lacks a safe bulk exact-byte repository export into the local executor, so no new real-ledger test PASS is claimed.

Issue #163 comment `5420950584` records this audit.

## Evidence produced / reconfirmed

- Published migration guard blob: `2ae3df05271385f1a0dd03d7ed85b86ec0ff72e2`.
- Current least-privilege fence blob: `5da01e28a9f813a136d138637f855940f04aab46`.
- Current final supported writer blob: `ceb7f48a55a931ba9923cac77d4ebf6c4cd2cfec`.
- Exact real-ledger cardinality regression on branch: `tests/test_pre_cutoff_lower_evidence_cardinality.py` blob `d2ff264ebbce0611805b880949478df4e5cef6a1`.
- Current `test_suffix.py` blob: `14b87522974a365738a56d82923ed9ae377a752e`.
- Cumulative exact lower-stack evidence remains: LAB-080 18/18, LAB-082 28/28, LAB-083 24/24, LAB-084 17/17, LAB-085 core 12/12, asymmetric-custody 8/8, public/final 11/11; lower unsafe baselines failed as intended.
- Earlier LAB-086 exact/focused strict-fence, migration-guard, scrubbed-prefix/final-writer and publication evidence remains recorded in Issue #163 / PR #165.

## Known blockers / constraints

- Remaining merge gate: execute the published cardinality fix against the exact real-ledger closure, then run the full current-head LAB-086 migration/suffix/final-supported suite, unsafe seed, compileall and final audit.
- Branch is substantially diverged (`ahead 146 / behind 87`) and PR currently reports non-mergeable; reconcile only after the test/security gate is clean.
- Direct shell/raw GitHub transport is unavailable in this run; connector reads are available but no safe bulk exact-byte export into the local executor was observed.
- This run's source audit is not a substitute for the required exact real-ledger execution.
- LAB-086 SQL fences cover audited supported/DML paths, not arbitrary same-privilege schema/DDL authority; LAB-087/#166 owns that boundary.
- LAB-088/#167 signer-noise, LAB-090/#169 provider handoff freshness, and LAB-091/#170 mutable shared-anchor/new-receipt authorization remain separate follow-ups.
- Logical SQL scrubbing is not forensic erasure; whole-store rollback freshness remains delegated to the external monotonic-anchor layer.

## Exact next action

1. Reconstruct the exact current PR dependency closure required by `test_pre_cutoff_lower_evidence_cardinality.py` using connector blob/content reads and verify executable files by `git hash-object`.
2. Execute `test_pre_cutoff_lower_evidence_cardinality.py` green against published migration guard blob `2ae3df05271385f1a0dd03d7ed85b86ec0ff72e2`.
3. Execute current `test_suffix.py` and all remaining LAB-086 real-schema migration/final-supported/security modules on the same closure, then unsafe legacy-promotion seed and full compileall.
4. Perform a fresh security audit focused on reverse evidence cardinality, cutoff/root/public proof binding, alternate supported mutation paths, transaction-scoped thaw/restoration, restart snapshots and rotation races.
5. Re-check and reconcile branch/main divergence using only supported auditable operations. Keep PR #165 draft until the complete current-head gate is clean; only then mark ready and integrate.

## Backlog

- #163 / LAB-086 — IN_PROGRESS; lower-evidence cardinality runtime fix published byte-exact, real-ledger current-head gate remains.
- #166 / LAB-087 — IN_PROGRESS; SQLite schema-control/process boundary work.
- #167 / LAB-088 — READY; threshold signer-noise robustness.
- #168 / LAB-089 — CLOSED `not_planned`.
- #169 / LAB-090 — READY; provider-generation handoff freshness/external-anchor race.
- #170 / LAB-091 — READY; mutable shared-ledger plus new provider-receipt writer authorization.
- PostgreSQL-specific validation and open-model serving remain deferred until representative runtime/hardware is available.
