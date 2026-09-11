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
- Therefore no new LAB-086 behavioral, unsafe-seed, compileall, security-reconciliation or conflict PASS is claimed; PR #165 remains `open`, `draft=true`, `mergeable=false`.
- Fresh compare after the research commit: PR #165 is `diverged`, ahead 195 / behind 852, merge base `d2c9781f5a60dc9b8b94fc8dba651f804a73e509`, base/main `be7c61560a016b07cc5d8edfe992927b338b69e3`. This state commit advances main again; refresh compare immediately before any integration decision.

Completed the recorded distinct fallback and froze `EMERGENCY_ROOT_SUCCESSION_RETIREMENT_MULTITRANSITION_UNLEARNING_DUAL_INVALIDATION_PRIVACY_ALLOCATION_PROVIDER_COMPENSATION_FORK_GC_MEMBERSHIP_V1_FROZEN` in `research/2026-09-11-emergency-root-succession-retirement-multitransition-unlearning-dual-invalidation-privacy-allocation-provider-compensation-fork-gc-membership-v1.md`, main research commit `be7c61560a016b07cc5d8edfe992927b338b69e3`; #178 comment `5639519110` records the result.

Key decisions:
- Emergency/root succession cannot self-authenticate. Normal transition binds predecessor+successor authority, recovery floor/head, known competing heads and policy generation. A known-compromised predecessor cannot authorize escape from itself; recovery then requires a separately pre-anchored independent path established before compromise.
- Retirement continuity across consecutive disjoint witness policies requires an authenticated bridge at every transition (or a pre-anchored emergency authority). Compaction commits the terminal non-resurrection floor plus bridge-chain digest/root; evidence loss never lowers the floor.
- Unlearning cutover retains source/destination invalidation lineage and reconciles the conservative union/descendant closure. A retired source may contribute evidence but never positive authority; unknown compacted ancestry becomes `UNLEARNING_DEPENDENCY_UNKNOWN` until exact revalidation.
- Privacy split/allocation branches preserve one logical lineage. Rollback, partial compaction, result deletion or invalidation never refunds already incurred privacy loss. Merge unions immutable released-event IDs and rejects same-ID/different-content collisions.
- Provider-generation fork resolution separates receipt authenticity from lineage authority. Original effects and compensations keep distinct immutable identities; late losing-branch completion remains safety-relevant possible-effect evidence. Unknown outcome after idempotency retention expiry requires external reconciliation before mutation.
- GC snapshots that compact several membership transitions must carry/chains compact old -> joint -> new finality proofs plus scope coverage. Merely naming `C_new` in a snapshot does not prove commit; one-sided survivors of unresolved joint consensus cannot obtain destructive authority.
- Frozen 48-case RED-first matrix covers all six contracts. Architecture/evidence only; exact RED/GREEN pending.

Primary donors re-verified this run: TUF root succession/rollback protection; RFC 9162 Merkle consistency; NIST SP 800-226 cumulative privacy budgeting; AWS idempotent mutation/token-retention semantics; Raft joint consensus and snapshot-retained configuration.

## Known failures / blockers
- LAB-086 remains priority #1. Exact local execution of the complete real-ledger closure is still unavailable.
- Direct shell transport cannot currently resolve `github.com`.
- Connector can read pinned source but cannot byte-exactly materialize the whole pinned closure into the executor in this run.
- Complete real-schema LAB-086 tests, unsafe expected-failure seed, full compileall, security reconciliation and current-main conflict audit remain pending.
- PR #165 is at least 852 commits behind main before this state commit; refresh compare before integration.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093..100 and subsequent design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against the pinned blob before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and a fresh current-main conflict audit. Fix every observed blocker before changing draft/merge status.

Do not manually copy connector payloads into the executor. If no supported materialization path exists, record the per-run observation and move directly to the next distinct evidence task: **multi-generation emergency/root cut-set independence after the pre-anchored escape authority itself retires + retirement witness-policy fork resolution after bridge-chain compaction + unlearning invalidation-vector compaction when descendants crossed a third store + privacy delegated-allocation reconciliation after allocator-generation compromise + provider fork resolution containing an irreversible/non-compensable external effect + GC snapshot/membership-proof fork resolution after compact checkpoints replicate across partitions and all detailed transition logs are gone**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + current-main conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; architecture now additionally covers emergency/root authority succession after compromise, multi-hop disjoint retirement transitions, dual-sided unlearning invalidations, privacy allocation rollback/overspend, compensated effects across provider-generation forks, and compact membership-proof succession after complete transition-log truncation; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen; exact executable gates pending.
