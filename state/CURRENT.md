# Current Lab State

Last updated: 2026-09-11

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and current-main conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`. Keep draft.
- Other open drafts inspected this run: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues and active PRs; resumed LAB-086 first and re-probed exact source materialization.

Current-run capability/evidence:
- Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository execution with `Could not resolve host: github.com`.
- GitHub connector reads/writes and compare remain available, but no supported non-model connector-to-local-filesystem byte-exact materialization primitive is exposed. Manual/model reserialization of the security-critical LAB-086 closure remains prohibited by the retained exact-byte gate.
- Therefore no new LAB-086 behavioral, unsafe-seed, compileall, security-reconciliation or conflict PASS is claimed; PR #165 remains draft/open.
- PR #165 was re-read at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; compare immediately after the research commit was `diverged`, ahead 195 / behind 832, merge base `d2c9781f5a60dc9b8b94fc8dba651f804a73e509`. This state-file commit moves `main` again, so obtain another fresh compare before any merge/conflict conclusion.

Completed the recorded distinct fallback and froze `RECOVERY_CHAIN_RETIREMENT_EXPORT_UNLEARNING_CACHE_PRIVACY_NAMESPACE_FINALITY_REPLAY_GC_CHECKPOINT_V1_FROZEN` in `research/2026-09-11-recovery-chain-retirement-export-unlearning-cache-privacy-namespace-finality-replay-gc-checkpoint-v1.md`, main research commit `e1883a455226ba98a7ec6bb0d1aa4ae23c0ec31f`; #178 comment `5633011608` records the result.

Key decisions:
- Recovery trust is evaluated over a time-scoped dependency/failure-domain graph. A later assessment is not independent if it derives from or shares a canonical failure domain with a compromised intermediate repair authority; same-generation repair heads remain an explicit fork until a higher generation commits all live heads and the last undisputed floor.
- A compact verifier-retirement floor is explicitly non-authoritative for live verification. Export across a trust-root rotation requires an authenticated bridge and preserves retirements monotonically; bridge revocation may make continuity uncertain but never resurrects retired authority.
- Unlearning result caches commit theorem/profile and ancestor status generations. Any ancestor generation change invalidates dependent caches until re-proof/revalidation; descendant issuance is CAS/snapshot-linearized against ancestor generation.
- Privacy split/merge retains one immutable root budget lineage. Child entitlements must be disjoint and bounded by the parent's remaining entitlement; consumed loss and unresolved reservations survive split, merge, participant removal and coordinator failover.
- Effect-ledger replay is generation/dependency aware. Compacted finality cache entries are performance hints until authority is re-established; revoked `FINAL` and `NO_EFFECT` decisions become `EFFECT_UNKNOWN`, and duplicate replay cannot repeat an external effect.
- A compact GC checkpoint whose authority is later revoked becomes `AUTHORITY_UNCERTAIN` for future decisions even after detailed evidence has crossed retention. If no independent evidence survives, record `PROOF_UNRECOVERABLE_AFTER_RETENTION` and fail closed instead of fabricating continuity.
- Frozen 48-case RED-first matrix covers all six contracts. This remains architecture/evidence only; exact RED/GREEN is pending.

Primary donors re-verified this run: TUF predecessor+successor threshold/root rollback discipline; RFC 9162 append-only consistency proofs; NIST SP 800-226 cumulative privacy budgeting; Raft joint-consensus membership changes.

## Known failures / blockers
- LAB-086 remains priority #1. Exact local execution of the complete real-ledger closure is still unavailable.
- Direct shell transport cannot currently resolve `github.com`.
- Connector can read pinned source but cannot byte-exactly materialize the whole pinned closure into the executor in this run.
- Complete real-schema LAB-086 tests, unsafe expected-failure seed, full compileall, security reconciliation and current-main conflict audit remain pending.
- PR #165 was 832 commits behind `main` immediately before this state commit; do not infer merge safety from historical conflict observations.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093..100 and subsequent design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against the pinned blob before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and a fresh current-main conflict audit. Fix every observed blocker before changing draft/merge status.

Do not manually copy connector payloads into the executor. If no supported materialization path exists, record the per-run observation and move directly to the next distinct evidence task: **recovery-chain cut-set validation when compromise evidence itself is pruned/compacted + replay/rollback protection for exported retirement floors after the source store is deleted + distributed unlearning cache invalidation/eviction proof across stale replicas/readers + privacy namespace split/merge reconciliation after shard loss/recovery and duplicate namespace identities + effect-ledger replay when provider transaction outcome is externally ambiguous + succession/recovery of overlapping compact GC checkpoints when one checkpoint authority is later revoked**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + current-main conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; architecture now additionally covers double-compromise recovery chains, retirement-floor export/root rotation, unlearning cache invalidation, privacy namespace split/merge, finality/effect replay and post-retention GC checkpoint authority loss; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen; exact executable gates pending.
