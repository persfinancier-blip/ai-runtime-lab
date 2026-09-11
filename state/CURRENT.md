# Current Lab State

Last updated: 2026-09-11

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and current-main conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`. Keep draft.
- Other open drafts inspected this run: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open PRs; resumed LAB-086 first and re-probed exact source materialization.

Current-run capability/evidence:
- Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository execution with `Could not resolve host: github.com`.
- GitHub connector reads/writes and compare remain available, but no supported non-model connector-to-local-filesystem byte-exact materialization primitive is exposed. Manual/model reserialization of the security-critical LAB-086 closure remains prohibited by the retained exact-byte gate.
- Therefore no new LAB-086 behavioral, unsafe-seed, compileall, security-reconciliation or conflict PASS is claimed; PR #165 remains draft/open.
- PR #165 metadata was re-read at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`: open, draft, mergeable=false.
- Fresh compare after the research commit: `diverged`, ahead 195 / behind 839, merge base `d2c9781f5a60dc9b8b94fc8dba651f804a73e509`, main/base at `10d8b221afbc0a08e073088371fa9ed50c348a1c`. Refresh again before any integration decision because this state update advances main.

Completed the recorded distinct fallback and froze `SUCCESSOR_COMPROMISE_RETIREMENT_RECONCILIATION_UNLEARNING_ROTATION_PRIVACY_MERGE_PROVIDER_COMPENSATION_GC_TOMBSTONE_V1_FROZEN` in `research/2026-09-11-successor-compromise-retirement-recovery-unlearning-rotation-privacy-merge-provider-compensation-gc-tombstone-v1.md`, main research commit `10d8b221afbc0a08e073088371fa9ed50c348a1c`; #178 comment `5635019574` records the result.

Key decisions:
- Rotated compact cut-set authority does not gain fresh proof by re-signing after successor compromise. Same-generation alternate successors are forks; recovery must commit all competing heads and preserve unknown/shared failure-domain floors. If surviving authority collapses into one compromised failure domain, state is `CUTSET_RECOVERY_AUTHORITY_UNCERTAIN`.
- Retirement state is a logical non-resurrection lineage across destination stores. Independently restored stores reconcile only through authenticated continuity; incomparable or same-generation alternate exports are forks. Recovery preserves the maximum accepted floor; loss of all continuity evidence yields `RETIREMENT_FLOOR_UNRECOVERABLE`, never verifier resurrection.
- Compact unlearning invalidation checkpoints cannot be root-rotated through an unresolved partition by latest-writer-wins. Rotation must commit every required partition head, preserve conservative-union invalidations and gate stale positive cache results until exact catch-up.
- Independently restored privacy branches that both spent budget merge by union/composition of accepted analyses under the configured accountant. Consumed loss is never reset or minimized. Same analysis id with conflicting payload is a fork; union budget overrun blocks new analyses and becomes explicit reconciliation state.
- Original provider effect E1 and separately authorized compensation E2 retain distinct identities. Conflicting authenticated `NO_EFFECT(E1)` / `COMPLETED(E1)` evidence yields `EFFECT_EVIDENCE_FORK`; E2 does not authorize choosing the convenient interpretation or redispatching E1 after provider TTL.
- GC split/merge retention compaction may remove detail only when retained tombstones prove exact scope coverage, successor continuity and the non-resurrection floor. Coverage gaps or sole compact-authority loss block destructive GC rather than reviving older authority.
- Frozen 48-case RED-first matrix covers all six contracts. This remains architecture/evidence only; exact RED/GREEN is pending.

Primary donors re-verified this run: TUF predecessor+successor root continuity and rollback rejection; RFC 9162 append-only consistency proofs; NIST SP 800-226 cumulative privacy budgeting; AWS idempotency identity with finite retention; Raft overlapping membership-change discipline.

## Known failures / blockers
- LAB-086 remains priority #1. Exact local execution of the complete real-ledger closure is still unavailable.
- Direct shell transport cannot currently resolve `github.com`.
- Connector can read pinned source but cannot byte-exactly materialize the whole pinned closure into the executor in this run.
- Complete real-schema LAB-086 tests, unsafe expected-failure seed, full compileall, security reconciliation and current-main conflict audit remain pending.
- PR #165 is now at least 839 commits behind the research-commit main and this state-only commit advances main again; refresh compare before integration.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093..100 and subsequent design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against the pinned blob before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and a fresh current-main conflict audit. Fix every observed blocker before changing draft/merge status.

Do not manually copy connector payloads into the executor. If no supported materialization path exists, record the per-run observation and move directly to the next distinct evidence task: **recovery-of-recovery generation rollback/equivocation after a resolved compact cut-set fork + retirement-floor reconciliation when an accepted reconciliation checkpoint is itself later revoked + unlearning invalidation root rotation with a replica that rejoins carrying pre-rotation descendants + privacy overrun recovery when one branch later retracts/invalidates an analysis result without refunding already released privacy loss + provider compensation chains where E2 itself becomes unknown and E1 late completion arrives + GC tombstone root rotation/compaction after parent-scope metadata has fully crossed retention**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + current-main conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; architecture now additionally covers successor compromise/fork recovery after compact cut-set rotation, cross-destination retirement reconciliation, partition-time invalidation root rotation, independently-spent privacy branch merge, provider evidence conflict after compensation, and GC tombstone compaction across split/merge scope succession; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen; exact executable gates pending.
