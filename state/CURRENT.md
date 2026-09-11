# Current Lab State

Last updated: 2026-09-11

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and current-main conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`. Keep draft.
- Other open drafts inspected this run: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues/PRs; resumed LAB-086 first and re-probed exact materialization.

Current-run capability/evidence:
- Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository execution with `Could not resolve host: github.com`.
- GitHub connector reads/writes/compare remain available, but no supported byte-exact connector-to-local-executor materialization primitive is exposed. Manual/model reserialization of the security-critical LAB-086 closure remains prohibited.
- Therefore no new LAB-086 behavioral, unsafe-seed, compileall, security-reconciliation or conflict PASS is claimed; PR #165 remains draft/open.
- Fresh compare before the research commit: PR #165 is `diverged`, ahead 195 / behind 840, merge base `d2c9781f5a60dc9b8b94fc8dba651f804a73e509`, main/base then `c38dc23d359a59517d3ff84839a6e56bc5d61e87`. Refresh before integration because main advanced again.

Completed the recorded distinct fallback and froze `RECOVERY_OF_RECOVERY_RETIREMENT_REVOKE_UNLEARNING_REJOIN_PRIVACY_OVERRUN_PROVIDER_COMPENSATION_GC_ROOT_V1_FROZEN` in `research/2026-09-11-recovery-of-recovery-retirement-revocation-unlearning-rejoin-privacy-overrun-provider-compensation-gc-root-v1.md`, main commit `9e2c6b18c8e851d85a77d1ecb314c006d10d2697`; #178 comment `5635858225` records the result.

Key decisions:
- A resolved compact cut-set fork establishes a monotonic accepted recovery generation. Replay of older generations is rollback; alternate same-generation recovery is a fork. Recovery-of-recovery must commit all competing heads and preserve inherited compromise/non-resurrection floors.
- Revocation of an accepted retirement reconciliation checkpoint removes it as positive continuity evidence but never resurrects a verifier or lowers the maximum accepted retirement floor. If compacted detail is gone and no independent bridge survives, state is `RETIREMENT_CONTINUITY_UNRECOVERABLE`.
- A rejoining unlearning replica must present its last authenticated invalidation checkpoint and descendant frontier. Pre-rotation descendants/caches are authority-bearing only after exact catch-up/revalidation; newly revealed omitted branches make the current rotation incomplete until a successor root commits the union.
- Privacy accounting is tied to cumulative released analyses, not retained result files. Retraction/deletion of an already released result does not refund privacy loss; merge overrun blocks new analyses unless policy adds budget or a reproducible tighter accountant validly lowers the bound over the same immutable event set.
- Original provider effect E1 and compensation E2 retain distinct immutable identities. `E1=COMPLETED, E2=UNKNOWN` is a two-effect unresolved state; neither compensation nor late completion authorizes blind redispatch, especially after provider idempotency retention expires.
- GC tombstone-root rotation after parent detail crosses retention requires predecessor continuity, exact split/merge scope coverage, surviving non-resurrection floors, and overlapping authority/catch-up when voters change. Loss/revocation of sole compact authority becomes `GC_AUTHORITY_UNRECOVERABLE`, blocking future destructive GC rather than reviving old authority.
- Frozen 48-case RED-first matrix covers all six contracts. Architecture/evidence only; exact RED/GREEN pending.

Primary donors re-verified this run: TUF predecessor+successor root continuity and rollback rejection; RFC 9162 append-only consistency proofs; NIST SP 800-226 cumulative privacy budgeting; AWS idempotency identity; Raft joint-consensus membership/catch-up discipline.

## Known failures / blockers
- LAB-086 remains priority #1. Exact local execution of the complete real-ledger closure is still unavailable.
- Direct shell transport cannot currently resolve `github.com`.
- Connector can read pinned source but cannot byte-exactly materialize the whole pinned closure into the executor in this run.
- Complete real-schema LAB-086 tests, unsafe expected-failure seed, full compileall, security reconciliation and current-main conflict audit remain pending.
- PR #165 is at least 840 commits behind the pre-research main; this research commit and state commit advance main again. Refresh compare before integration.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093..100 and subsequent design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against the pinned blob before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and a fresh current-main conflict audit. Fix every observed blocker before changing draft/merge status.

Do not manually copy connector payloads into the executor. If no supported materialization path exists, record the per-run observation and move directly to the next distinct evidence task: **recovery-generation anchor rotation after a recovery-of-recovery fork + retirement continuity reconstruction across multiple revoked checkpoints + unlearning rejoin where the stale replica has already propagated descendants to another partition + privacy overrun reconciliation after coordinator/accountant version change + provider E1/E2/E3 compensation chains with contradictory late evidence + GC compact-root succession where both old and new authority sets lose replicas across the joint-consensus boundary**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + current-main conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; architecture now additionally covers recovery-of-recovery rollback/fork semantics, revoked retirement reconciliation checkpoints, stale-replica descendant revalidation, no-refund privacy overrun recovery, unknown compensation chains, and post-retention GC tombstone-root succession; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen; exact executable gates pending.
