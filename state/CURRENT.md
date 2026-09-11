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
- Fresh compare after the research commit: PR #165 is `diverged`, ahead 195 / behind 854, merge base `d2c9781f5a60dc9b8b94fc8dba651f804a73e509`, base/main `d8d9ad51a71377fc7738dbb9f1c6e227709e8770`. This state commit advances main again; refresh compare immediately before any integration decision.

Completed the recorded distinct fallback and froze `MULTIGEN_EMERGENCY_RETIREMENT_FORK_UNLEARNING_THIRDSTORE_PRIVACY_ALLOCATOR_PROVIDER_IRREVERSIBLE_GC_FORK_V1_FROZEN` in `research/2026-09-11-emergency-root-multigen-retirement-fork-unlearning-thirdstore-privacy-allocator-provider-irreversible-gc-fork-v1.md`, main research commit `d8d9ad51a71377fc7738dbb9f1c6e227709e8770`; #178 comment `5640128682` records the result.

Key decisions:
- Multi-generation emergency/root succession preserves the predecessor/successor bridge and the independence cut-set that justified escape authority. Once the escape authority itself retires, the successor cannot become self-authenticating; compromise before the bridge invalidates that derivation and requires a separately pre-anchored independent path.
- Consecutive disjoint retirement witness policies compact to an ordered bridge-chain root plus policy generations and the terminal non-resurrection floor. Equal floors with incompatible provenance are forks, not equivalent states; reconciliation never lowers the floor.
- Unlearning invalidation vectors remain transitive across migrations. When stale descendants cross a third store before convergence, compaction must preserve descendant-closure/lineage evidence; unknown ancestry is `UNLEARNING_DEPENDENCY_UNKNOWN` and cannot produce an authority-bearing positive result.
- Delegated privacy allocations partition one logical cumulative budget; allocator rotation/compromise, rollback, result deletion or branch restore never refunds incurred privacy loss. Reconciliation unions immutable release-event IDs and treats same-ID/different-content as a hard collision.
- Provider receipt authenticity is distinct from branch authority. An irreversible/non-compensable effect produced on a losing provider branch remains a monotonic external fact; fork resolution cannot rewrite it to `NO_EFFECT`, and unknown outcomes after idempotency-retention expiry forbid blind replay.
- GC snapshots that outlive detailed membership-transition logs must carry compact membership-chain/joint-consensus proof. Two replicated snapshots naming the same terminal configuration but carrying incompatible proof roots are a fork; neither partition gets destructive GC authority without authenticated reconciliation.
- Frozen 48-case RED-first matrix covers all six contracts. Architecture/evidence only; exact RED/GREEN pending.

Primary donors re-verified this run: TUF root predecessor+successor threshold continuity and rollback rejection; RFC 9162 Merkle consistency; NIST SP 800-226 cumulative privacy budgeting; AWS stable idempotency tokens and finite token-retention examples; Raft joint consensus plus snapshot-retained membership configuration.

## Known failures / blockers
- LAB-086 remains priority #1. Exact local execution of the complete real-ledger closure is still unavailable.
- Direct shell transport cannot currently resolve `github.com`.
- Connector can read pinned source but cannot byte-exactly materialize the whole pinned closure into the executor in this run.
- Complete real-schema LAB-086 tests, unsafe expected-failure seed, full compileall, security reconciliation and current-main conflict audit remain pending.
- PR #165 is 854 commits behind main before this state commit; refresh compare before integration.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093..100 and subsequent design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against the pinned blob before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and a fresh current-main conflict audit. Fix every observed blocker before changing draft/merge status.

Do not manually copy connector payloads into the executor. If no supported materialization path exists, record the per-run observation and move directly to the next distinct evidence task: **emergency/root cut-set renewal when the independent escape domains partially overlap after successive rotations + retirement bridge reconciliation when two compacted forks each contain valid but mutually exclusive revocation evidence + unlearning closure reconciliation when the third-store descendant itself migrates after compaction + privacy delegated-allocation fork after both allocator generations independently spend near the parent limit + provider irreversible-effect reconciliation when external observation is delayed and contradicts branch-local receipts + GC membership-chain reconciliation when two compact snapshots have different last-included boundaries but overlap only in a compact joint-consensus certificate**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + current-main conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; architecture now additionally covers multi-generation emergency cut-set independence, retirement bridge-chain fork provenance, third-store unlearning closure, delegated privacy allocation compromise, irreversible losing-branch provider effects, and replicated compact GC membership-proof forks; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen; exact executable gates pending.
