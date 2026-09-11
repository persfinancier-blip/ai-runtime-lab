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
- Fresh compare after the research commit: PR #165 is `diverged`, ahead 195 / behind 846, merge base `d2c9781f5a60dc9b8b94fc8dba651f804a73e509`, base/main then `1a391cc56c94fe2512c0b9b65ba5a46aaec1ee15`. This state-only commit advances main once more, so refresh again immediately before any integration decision.

Completed the recorded distinct fallback and froze `RECOVERY_CUTSET_RETIREMENT_WITNESS_UNLEARNING_CLOSURE_PRIVACY_ACCOUNTANT_PROVIDER_HEAL_GC_SNAPSHOT_V1_FROZEN` in `research/2026-09-11-recovery-cutset-retirement-witness-unlearning-closure-privacy-accountant-provider-heal-gc-snapshot-v1.md`, main commit `1a391cc56c94fe2512c0b9b65ba5a46aaec1ee15`; #178 comment `5637397314` records the result.

Key decisions:
- Recovery successor threshold cardinality and independence are distinct. Compact recovery certificates must preserve enough failure-domain/cut-set evidence to prove independence; otherwise positive recovery authorization becomes `RECOVERY_INDEPENDENCE_UNPROVABLE`. Same-generation successor alternatives remain a fork until a later authenticated resolver commits all known competing heads.
- Retirement bridge compaction binds both a monotonic non-resurrection floor and a witness-set commitment. Equal numeric floors with incomparable witness provenance are not equivalent. Losing continuity proof blocks positive provenance but never resurrects a retired verifier.
- Distributed unlearning invalidation survives local dependency compaction only through immutable ancestry/dependency commitments. Incomparable invalidation frontiers merge conservatively; unknown ancestry yields `UNLEARNING_DEPENDENCY_UNKNOWN` rather than a positive cache result.
- Privacy accountant/coordinator versions do not define new budget lineages. A tighter bound is accepted only when reproducibly computed over the exact same immutable released-analysis event set under an authorized method transition. Rollback/equivocation is rejected independently of numeric conservatism.
- Provider E1/E2/E3 original/compensation/repair effects retain separate immutable identities. Partition healing unions authenticated evidence per identity; contradictory terminal evidence yields `PROVIDER_EFFECT_FORK`, and TTL expiry never proves no prior effect or authorizes blind redispatch.
- GC snapshot authority and membership-finality authority are separate. A snapshot containing `C_new` does not prove `C_new` committed. When survivors disagree and commit proof cannot be reconstructed, state is `GC_MEMBERSHIP_FINALITY_UNKNOWN` and destructive GC is blocked.
- Frozen 48-case RED-first matrix covers all six contracts. Architecture/evidence only; exact RED/GREEN pending.

Primary donors re-verified this run: TUF root succession/rollback protection; RFC 9162 append-only consistency; NIST SP 800-226 cumulative privacy budgeting; Raft joint-consensus membership safety.

## Known failures / blockers
- LAB-086 remains priority #1. Exact local execution of the complete real-ledger closure is still unavailable.
- Direct shell transport cannot currently resolve `github.com`.
- Connector can read pinned source but cannot byte-exactly materialize the whole pinned closure into the executor in this run.
- Complete real-schema LAB-086 tests, unsafe expected-failure seed, full compileall, security reconciliation and current-main conflict audit remain pending.
- PR #165 was 846 commits behind at the latest compare, and this final state-only commit advances main again; refresh compare before integration.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093..100 and subsequent design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against the pinned blob before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and a fresh current-main conflict audit. Fix every observed blocker before changing draft/merge status.

Do not manually copy connector payloads into the executor. If no supported materialization path exists, record the per-run observation and move directly to the next distinct evidence task: **recovery cut-set key/domain revocation after compact-certificate issuance + retirement witness-threshold changes across bridge generations + unlearning closure proof retention after result-store migration + privacy event-set checkpoint/Merkle compaction across accountant rotation + provider compensation semantics when the provider rolls back/replays receipts + GC membership-proof retention across multiple snapshot generations and consensus-log truncation**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + current-main conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; architecture now additionally covers recovery cut-set independence, retirement witness compaction, propagated unlearning closure under dependency compaction, privacy-accountant rollback/equivocation, provider compensation partition/heal, and GC snapshot recovery with disputed membership finality; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen; exact executable gates pending.
