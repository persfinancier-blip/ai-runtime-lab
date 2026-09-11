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
- Therefore no new LAB-086 behavioral, unsafe-seed, compileall, security-reconciliation or conflict PASS is claimed; PR #165 remains draft/open/mergeable=false.
- Fresh compare after the research commit: PR #165 is `diverged`, ahead 195 / behind 850, merge base `d2c9781f5a60dc9b8b94fc8dba651f804a73e509`, base/main `27fbd199e169db9baa1c1c23ace46848d4b02da4`. This state commit advances main again; refresh compare immediately before any integration decision.

Completed the recorded distinct fallback and froze `REVOCATION_ROTATION_RETIREMENT_INTERSECTION_UNLEARNING_ROLLBACK_PRIVACY_SPLIT_PROVIDER_FORK_GC_TRUNCATION_V1_FROZEN` in `research/2026-09-11-revocation-rotation-retirement-intersection-unlearning-rollback-privacy-split-provider-fork-gc-truncation-v1.md`, main research commit `27fbd199e169db9baa1c1c23ace46848d4b02da4`; #178 comment `5638892668` records the result.

Key decisions:
- Recovery revocation-policy succession binds old/new policy generations, compact recovery head/floor, all known competing revocation heads and the exact authority path. Normal rotation needs old+new continuity; a known-compromised predecessor cannot authorize escape from its own compromise, so emergency succession needs an already-anchored independent recovery/root authority.
- Retirement bridges across disjoint witness sets require explicit joint old+new transition authorization or a previously anchored emergency authority. A higher/equal retirement floor signed only by a successor witness set is not provenance; revocation never lowers the non-resurrection floor.
- Unlearning result-store migration emits an independent succession checkpoint binding source terminal root, destination imported root, result set/range, theorem/profile generation, invalidation frontier, descendant-closure root and source-retirement floor. A retired source cannot regain positive authority and a pre-migration destination snapshot is rollback.
- Privacy split/merge preserves one logical released-event lineage. Split representation does not create fresh independent budgets. Merge authenticates both branch heads, unions immutable released-event IDs, rejects same-ID/different-content collisions, and conservatively composes all unique released events; compaction never refunds loss.
- Provider receipts have two separate verification questions: effect authenticity and provider-generation lineage authority. Individually valid receipts on unresolved generation forks remain evidence of possible effects but cannot authorize replay, confirmation or compensation until lineage resolution.
- GC snapshots that truncate across Raft membership transitions must carry a compact old -> joint -> new membership-finality proof package. Snapshot presence of `C_new` is not proof it committed; loss of the compact transition proof blocks destructive GC as finality unknown.
- Frozen 48-case RED-first matrix covers all six contracts. Architecture/evidence only; exact RED/GREEN pending.

Primary donors re-verified this run: TUF root succession/rollback protection; RFC 9162 Merkle consistency; NIST SP 800-226 cumulative privacy budgeting; AWS idempotent mutation guidance; Raft joint consensus.

## Known failures / blockers
- LAB-086 remains priority #1. Exact local execution of the complete real-ledger closure is still unavailable.
- Direct shell transport cannot currently resolve `github.com`.
- Connector can read pinned source but cannot byte-exactly materialize the whole pinned closure into the executor in this run.
- Complete real-schema LAB-086 tests, unsafe expected-failure seed, full compileall, security reconciliation and current-main conflict audit remain pending.
- PR #165 is at least 850 commits behind main before this state commit; refresh compare before integration.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093..100 and subsequent design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against the pinned blob before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and a fresh current-main conflict audit. Fix every observed blocker before changing draft/merge status.

Do not manually copy connector payloads into the executor. If no supported materialization path exists, record the per-run observation and move directly to the next distinct evidence task: **recovery emergency-authority/root succession after the emergency authority itself rotates or is compromised + retirement continuity across multiple consecutive disjoint witness-policy transitions + unlearning cutover where destination and retired source receive independent invalidations before reconciliation + privacy branch allocation rollback/overspend with partially compacted event sets + provider fork resolution after compensation effects were independently issued on competing branches + GC compact membership-proof succession across multiple membership transitions and snapshot generations after all detailed joint-consensus logs are truncated**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + current-main conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; architecture now additionally covers revocation-authority succession/compromise, disjoint retirement witness-policy transitions, post-retirement unlearning migration rollback, independently advanced privacy split/merge, valid provider receipts on forked generation lineages, and compact GC membership proof across truncated joint-consensus boundaries; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen; exact executable gates pending.
