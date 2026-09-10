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

Completed the recorded distinct fallback and froze `WITNESS_SUCCESSOR_HOLDOUT_CACHE_PRIVACY_REVOCATION_RECEIPT_EQUIVOCATION_TICKET_GC_V1_FROZEN` in `research/2026-09-10-witness-successor-holdout-cache-privacy-revocation-receipt-equivocation-ticket-gc-v1.md`, main commit `607b678d19ac817ae62951eb6b23cd2be04941b5`; #178 comment `5621845253` records the result.

Key decisions:
- `SUCCESSOR_QUORUM_VALID != SUCCESSOR_LINEAGE_AUTHORIZED`: successor witness membership must prove continuity from the last non-disputed predecessor state; re-keying/renaming does not create a new independent domain and removed witnesses do not erase prior conflict evidence.
- `CHECKPOINT_COMPACTED != CHECKPOINT_HISTORY_DISPENSABLE`: cross-log checkpoint GC requires completeness commitments across membership epochs and conflict intervals; unresolved split-view evidence blocks GC.
- `DISTINCT_DATASET_ROWS != INDEPENDENT_HOLDOUT_INFORMATION`: shared feature/embedding/statistics caches derived from holdout data inherit disclosure ancestry and exposure budget even when raw rows are hidden or deleted.
- `DISJOINTNESS_PROOF_VALID_AT_T0 != DISJOINTNESS_PROOF_VALID_AFTER_GRAPH_MERGE`: privacy disjointness evidence is bound to identity-graph/resolver/evidence epochs; graph merges revoke affected proofs and cumulative spend is reconciled conservatively.
- `VALID_PROVIDER_RECEIPT != UNIQUE_PROVIDER_EFFECT_HISTORY`: mutually inconsistent but valid provider receipts trigger equivocation; compensation is a new effect with bounded generation, not erasure of the original effect.
- `TICKET_EXPIRED_LOCALLY != PREDECESSOR_AUTHORITY_EXTINCT_GLOBALLY`: ticket-security-epoch GC waits for provable extinction across active/retired keys, KMS/HSM wrapped copies, backup/DR, regions, replay state and recovery credentials.
- Frozen 40-case RED-first matrix across those six domains.

Primary donors: RFC 9162; Dwork et al. 2015 adaptive holdout reuse; NIST SP 800-226; RFC 8446/RFC 9846 TLS 1.3; RFC 9325.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact local execution of the complete real-ledger closure.
- Direct shell transport cannot currently resolve `github.com`.
- Connector can read pinned source but this run has no supported non-model connector-to-local-filesystem materialization primitive.
- Complete real-schema LAB-086 tests, unsafe expected-failure seed, full compileall, security reconciliation and branch/main conflict audit remain pending.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093..100 design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against the pinned blob before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

Do not manually copy connector payloads into the executor. If no supported materialization path exists, record the per-run observation and move directly to the next distinct evidence task: **successor witness recovery-root rollback and overlapping old/new quorum ambiguity + cross-log compact-root witness loss/reconstruction + revocation/garbage-collection of holdout-derived feature caches with proof of exposure-floor continuity + privacy identity-graph split/merge oscillation and monotonic spend reconciliation + provider receipt equivocation across key rotation and partial compensation + ticket-security-epoch GC under delayed backup discovery and recovery-credential rotation**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; architecture now additionally covers successor witness authorization, checkpoint GC completeness, holdout leakage through derived caches, privacy disjointness revocation after identity-graph changes, provider receipt equivocation/compensation bounds, and ticket-security-epoch GC after provable predecessor-authority extinction; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen; exact executable gates pending.
