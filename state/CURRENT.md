# Current Lab State

Last updated: 2026-09-12

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
- Fresh compare after the research commit: PR #165 is `diverged`, ahead 195 / behind 856, merge base `d2c9781f5a60dc9b8b94fc8dba651f804a73e509`, base/main `4119bfd71ab703c9aea9c9cea8877ec824f87f74`. This state commit advances main again; refresh compare immediately before any integration decision.

Completed the recorded distinct fallback and froze `OVERLAP_EMERGENCY_RETIREMENT_REVOCATION_UNLEARNING_REMIGRATION_PRIVACY_DUAL_SPEND_PROVIDER_DELAYED_OBSERVATION_GC_BOUNDARY_V1_FROZEN` in `research/2026-09-12-overlap-emergency-retirement-revocation-unlearning-remigration-privacy-dual-spend-provider-delayed-observation-gc-boundary-reconciliation-v1.md`, main research commit `4119bfd71ab703c9aea9c9cea8877ec824f87f74`; #178 comment `5640778753` records the result.

Key decisions:
- Emergency/root recovery independence is evaluated over explicit failure domains, not signer cardinality. Successive rotations may partially overlap only if the authenticated policy permits the overlap and a sufficient independent cut set still survives; compromise covering every independent bridge invalidates derivation from that chain.
- Two compact retirement forks with mutually exclusive valid revocations are not resolved by terminal floor or generation number. Preserve the maximum proven non-resurrection floor and withhold future authority until an authenticated ordering/common successor reconciles the revocation provenance.
- Unlearning `dependency unknown` propagates through a third-store descendant's later migration. Remigration cannot upgrade unknown ancestry into clean state; retired stores lose mutation authority but their compact lineage evidence remains required.
- Privacy allocator-generation rotation does not duplicate the residual parent budget. Concurrent near-limit spends reconcile by union of immutable release events and conservative cumulative loss; an overrun cannot be repaired by discarding a valid disclosure or rolling back a branch.
- Provider transport outcome, branch-local receipt and independently observed world state are distinct evidence classes. Delayed authenticated evidence that a losing branch produced an effect remains a monotonic external fact; conflicting authenticated observations create an explicit evidence fork/quarantine rather than history rewrite.
- GC snapshot freshness by `lastIncludedIndex` does not dominate membership provenance. Different compact snapshot boundaries reconcile only if a joint-consensus certificate binds old/new configs, transition index/term and predecessor membership root and proves extension across the compacted boundary.
- Frozen 48-case RED-first matrix covers all six contracts. Architecture/evidence only; exact RED/GREEN pending.

Primary donors re-verified this run: TUF 1.0.36 predecessor/successor root continuity and rollback rejection; RFC 9162 Merkle consistency proofs; NIST SP 800-226 cumulative privacy budgeting; AWS stable idempotency token semantics with finite retention; Raft joint consensus plus snapshot-retained last-included metadata/configuration.

## Known failures / blockers
- LAB-086 remains priority #1. Exact local execution of the complete real-ledger closure is still unavailable.
- Direct shell transport cannot currently resolve `github.com`.
- Connector can read pinned source but cannot byte-exactly materialize the whole pinned closure into the executor in this run.
- Complete real-schema LAB-086 tests, unsafe expected-failure seed, full compileall, security reconciliation and current-main conflict audit remain pending.
- PR #165 is 856 commits behind main before this state commit; refresh compare before integration.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093..100 and subsequent design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against the pinned blob before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and a fresh current-main conflict audit. Fix every observed blocker before changing draft/merge status.

Do not manually copy connector payloads into the executor. If no supported materialization path exists, record the per-run observation and move directly to the next distinct evidence task: **emergency/root partial-overlap cut-set reconciliation when compromise timing is itself forked + retirement revocation ordering after a common successor is later revoked + unlearning remigration lineage proof when both S3 and S4 metadata are compacted + privacy residual-budget lease/checkpoint reconciliation after allocator partition heal without trusting wall-clock expiry + provider delayed-observation ordering when multiple independent observers disagree across retention expiry + GC membership reconciliation across two successive compact joint-consensus certificates with no detailed membership log remaining**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + current-main conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; architecture now additionally covers partial-overlap emergency failure domains, mutually exclusive retirement revocations, third-store remigration after compaction, concurrent allocator-generation privacy spend, delayed external provider observation, and different-boundary compact GC membership reconciliation; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen; exact executable gates pending.
