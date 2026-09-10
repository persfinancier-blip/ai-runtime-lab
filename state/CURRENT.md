# Current Lab State

Last updated: 2026-09-10

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; current inspection confirms `open`, `draft=true`. Keep draft.
- Other open drafts remain LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues and open PRs; resumed LAB-086 first and re-probed exact source materialization.

Current-run capability observation:
- Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository execution with `Could not resolve host: github.com`.
- GitHub connector reads/writes are available.
- No supported non-model connector-to-local-filesystem byte-exact materialization primitive is exposed in this run. Manual/model reserialization of the security-critical LAB-086 closure remains prohibited by the retained exact-byte gate.
- Therefore no new LAB-086 behavioral, unsafe-seed, compileall, security-reconciliation or conflict PASS is claimed; PR #165 remains draft.

Completed the recorded distinct fallback and froze `RECOVERY_ROOT_ROLLBACK_HOLDOUT_CACHE_GC_PRIVACY_OSCILLATION_RECEIPT_KEY_ROTATION_TICKET_DELAYED_AUTHORITY_V1_FROZEN` in `research/2026-09-10-recovery-root-holdout-cache-gc-privacy-oscillation-receipt-key-rotation-ticket-backup-discovery-v1.md`, main commit `9cf522e4feea8e092c2afecabc6df00435881eed`; #178 comment `5622673901` records the result.

Key decisions:
- `SUCCESSOR_ROOT_PRESENT != SUCCESSOR_ROOT_MONOTONICALLY_AUTHORIZED`: recovery-root transitions are predecessor-bound and monotonic; incompatible overlapping old/new quorum authorizations enter explicit equivocation rather than threshold shopping.
- `COMPACT_ROOT_SIGNATURE_VALID != COMPACT_ROOT_RECONSTRUCTABLE`: cross-log GC requires enough retained membership/conflict/witness-lineage evidence to reconstruct authority-relevant history after witness loss.
- `CACHE_OBJECT_DELETED != HOLDOUT_EXPOSURE_REVOKED`: holdout-derived embeddings/features/statistics and downstream derivatives preserve the predecessor exposure floor until every reachable derivative is fenced or continuity is explicitly inherited.
- `GRAPH_SPLIT_AFTER_MERGE != PRIVACY_SPEND_REFUND`: identity-graph split/merge oscillation cannot refund or mint privacy budget; reconciliation uses a monotonic subject-lineage spend/unknown-loss floor.
- `RECEIPT_KEY_ROTATED != RECEIPT_HISTORY_LINEARIZED`: unresolved provider effects span receipt-key epochs; incompatible valid receipts are provider equivocation, and compensation remains a separately sequenced effect.
- `GC_ACK_QUORUM_COMPLETE_AT_T0 != PREDECESSOR_AUTHORITY_EXTINCT_AFTER_LATE_DISCOVERY`: delayed discovery of backup/wrapped/recovery authority reopens ticket extinction proof without lowering the monotonic ticket-security floor; affected restore domains remain resumption-quarantined.
- Frozen 40-case RED-first matrix across those six domains.

Primary donors: RFC 9162; Dwork et al. 2015 adaptive holdout reuse; NIST SP 800-226; RFC 9325; NIST SP 800-88 Rev. 2.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact local execution of the complete real-ledger closure.
- Direct shell transport cannot currently resolve `github.com`.
- Connector can read pinned source but this run has no supported non-model connector-to-local-filesystem materialization primitive.
- Complete real-schema LAB-086 tests, unsafe expected-failure seed, full compileall, security reconciliation and branch/main conflict audit remain pending.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093..100 design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against the pinned blob before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

Do not manually copy connector payloads into the executor. If no supported materialization path exists, record the per-run observation and move directly to the next distinct evidence task: **recovery-root successor quorum intersection under delayed member-compromise discovery + compact-root reconstruction when retained witness attestations themselves rotate/expire + holdout exposure continuity through lossy compression/distillation and approximate indexes + privacy spend reconciliation under identity deletion/tombstoning and later relinking + provider effect reconciliation across receipt-key compromise/revocation and reordered delayed receipts + ticket-security-epoch authority discovery through external KMS import/replication and cross-region credential escrow**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; architecture now additionally covers monotonic recovery-root rollback/equivocation, compact-root reconstruction after witness loss, holdout-derived cache GC with exposure continuity, privacy graph split/merge monotonic spend, provider receipt-key rotation/equivocation, and delayed ticket-authority discovery after apparent GC; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen; exact executable gates pending.
