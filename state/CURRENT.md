# Current Lab State

Last updated: 2026-09-11

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and current-main conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`. Keep draft.
- Other open drafts inspected this run: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues and active PR metadata; resumed LAB-086 first and re-probed exact source materialization.

Current-run capability/evidence:
- Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository execution with `Could not resolve host: github.com`.
- GitHub connector reads/writes and compare remain available, but no supported non-model connector-to-local-filesystem byte-exact materialization primitive is exposed. Manual/model reserialization of the security-critical LAB-086 closure remains prohibited by the retained exact-byte gate.
- Therefore no new LAB-086 behavioral, unsafe-seed, compileall, security-reconciliation or conflict PASS is claimed; PR #165 remains draft/open.
- PR #165 was re-read at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; fresh compare before this run's research commit was `diverged`, ahead 195 / behind 833, merge base `d2c9781f5a60dc9b8b94fc8dba651f804a73e509`. Main moved after that compare; refresh before any merge/conflict conclusion.

Completed the recorded distinct fallback and froze `COMPACTED_CUTSET_RETIREMENT_REPLAY_UNLEARNING_EVICTION_PRIVACY_SHARD_RECOVERY_PROVIDER_AMBIGUITY_GC_SUCCESSION_V1_FROZEN` in `research/2026-09-11-compacted-cutset-retirement-replay-unlearning-eviction-privacy-shard-recovery-provider-ambiguity-gc-succession-v1.md`, main research commit `536597ecc2498084286b0483f75f3fc5fe2ad192`; #178 comment `5633656054` records the result.

Key decisions:
- Compacted recovery cut-set evidence commits graph/registry generations, compromise intervals, exclusions and surviving independent domains; unresolved dependency uncertainty cannot be compacted into independence. Revoked/equivocated cut authority becomes `CUTSET_AUTHORITY_UNCERTAIN` rather than being recomputed optimistically from missing detail.
- Exported verifier-retirement floors carry a destination-side monotonic export high-water mark. After source-store deletion, older validly signed exports are rollback, same-generation different digests are forks, and bridge revocation never resurrects retired authority.
- Distributed unlearning invalidation is a monotonic authority floor distinct from cache eviction. Stale replicas/readers must catch up invalidation state before serving positive authority-bearing cached results; invalidation tombstones may be reclaimed only after an authenticated compact invalidation checkpoint supersedes them.
- Privacy shard loss/recovery preserves one immutable logical root-budget lineage. Duplicate physical namespace identities are aliases, not new budget; stale recovered shards cannot spend before catch-up; missing reservations stay conservatively live; merge deduplicates immutable analysis/reservation IDs without choosing the least-spent view.
- External destructive provider mutations are bound to one immutable effect/idempotency identity before dispatch. Timeout/transport loss yields `EFFECT_UNKNOWN`; retries reuse the same identity and exact parameters only when provider semantics still make that safe. Expired idempotency retention forbids blind retry.
- Overlapping compact GC checkpoints form a scope-aware DAG. Newer checkpoints supersede only explicit authenticated scope; authority revocation does not revive older retired scope, and incomplete surviving coverage blocks new destructive/restoration authority.
- Frozen 48-case RED-first matrix covers all six contracts. This remains architecture/evidence only; exact RED/GREEN is pending.

Primary donors re-verified this run: TUF predecessor+successor threshold/root rollback discipline; RFC 9162 append-only consistency proofs; NIST SP 800-226 cumulative privacy budgeting; Raft joint-consensus membership changes; AWS idempotency-token semantics for retrying uncertain mutating operations without duplicate effects.

## Known failures / blockers
- LAB-086 remains priority #1. Exact local execution of the complete real-ledger closure is still unavailable.
- Direct shell transport cannot currently resolve `github.com`.
- Connector can read pinned source but cannot byte-exactly materialize the whole pinned closure into the executor in this run.
- Complete real-schema LAB-086 tests, unsafe expected-failure seed, full compileall, security reconciliation and current-main conflict audit remain pending.
- PR #165 was 833 commits behind `main` immediately before this run's research commit; do not infer merge safety from historical conflict observations.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093..100 and subsequent design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against the pinned blob before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and a fresh current-main conflict audit. Fix every observed blocker before changing draft/merge status.

Do not manually copy connector payloads into the executor. If no supported materialization path exists, record the per-run observation and move directly to the next distinct evidence task: **root/registry rotation of compact recovery cut-set certificates after detailed evidence deletion + re-export/recovery of verifier-retirement floors after destination-store compromise + partition/heal semantics for compact distributed unlearning invalidation checkpoints + logical privacy-lineage identity collisions across independently restored roots + ambiguous provider effects when idempotency TTL expires and a late authenticated completion signal arrives + split/merge succession of compact GC checkpoint scopes across authority rotation and partial retention**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + current-main conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; architecture now additionally covers compacted recovery cut-sets, retirement-export replay after source deletion, distributed unlearning invalidation/eviction, privacy shard loss/recovery, ambiguous provider effects, and overlapping compact GC checkpoint succession; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen; exact executable gates pending.
