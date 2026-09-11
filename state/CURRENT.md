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
- GitHub connector reads/writes remain available, but no supported byte-exact connector-to-local-executor materialization primitive is exposed. Manual/model reserialization of the security-critical LAB-086 closure remains prohibited.
- Therefore no new LAB-086 behavioral, unsafe-seed, compileall, security-reconciliation or conflict PASS is claimed.
- PR #165 was freshly fetched and remains `open`, `draft=true`, `mergeable=false`, head `ee210a47221b6df53f3518aa3af74f76c5b0122b`. The compare endpoint was not available through the connector form attempted this run; refresh exact branch/main divergence before any integration decision.

Completed the recorded fallback and froze `FORKED_COMPROMISE_RETIREMENT_COMMON_SUCCESSOR_UNLEARNING_DOUBLE_COMPACTION_PRIVACY_LEASE_PROVIDER_OBSERVER_GC_SUCCESSIVE_CERT_V1_FROZEN` in `research/2026-09-12-forked-compromise-retirement-common-successor-unlearning-double-compaction-privacy-lease-provider-observer-gc-successive-certificates-v1.md`, main research commit `4ed28684443be9f295503a32bdee6daf1d6250f2`; #178 comment `5641291712` records the result.

Key decisions:
- Compromise timing is authenticated order/interval evidence, not trusted wall-clock metadata. If two valid timing histories disagree about whether a required recovery bridge was compromised, successor authority is ambiguous until an authenticated common successor/order proof covers both branches; failure-domain independence matters, not signer count.
- A common retirement successor's later revocation separates historical-statement validity from prospective authority. Prospective revocation blocks new signatures without automatically erasing old reconciliation; retroactive revocation may reopen ordering ambiguity but cannot lower independently proven non-resurrection floors.
- Unlearning `dependency unknown` survives S3->S4 remigration and double compaction unless an authenticated full-closure revalidation clears it. Compact roots must chain predecessor lineage/invalidation obligations; missing bridges fail closed.
- Privacy lease expiry based on wall clock is never sufficient to reclaim budget. Partition heal reconciles immutable release-event unions plus conservative unresolved lease bounds; allocator rollback/rotation cannot recreate residual budget.
- Provider transport outcome, retained receipt, observer statement and external effect are distinct evidence. Receipt/idempotency retention expiry means proof unavailable, not effect absent; incomparable authenticated observers create an explicit evidence fork rather than a blind replay.
- Two successive compact membership certificates must preserve both joint-consensus transition obligations. Snapshot freshness/terminal membership alone does not prove truncated membership history.
- Frozen 48-case RED-first matrix covers all six contracts. Architecture/evidence only; exact RED/GREEN pending.

Primary donors re-verified this run: TUF 1.0.36 predecessor/successor root continuity and rollback semantics; RFC 9162 Merkle consistency proofs; NIST SP 800-226 cumulative privacy-budget semantics; AWS stable idempotency-token semantics; Raft joint consensus and snapshot-retained membership/index/term metadata.

## Known failures / blockers
- LAB-086 remains priority #1. Exact local execution of the complete real-ledger closure is unavailable in this run.
- Direct shell transport cannot resolve `github.com`.
- Connector can read pinned source but cannot byte-exactly materialize the whole pinned closure into the executor in this run.
- Complete real-schema LAB-086 tests, unsafe expected-failure seed, full compileall, security reconciliation and current-main conflict audit remain pending.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093..100 and subsequent design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against the pinned blob before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and a fresh current-main conflict audit. Fix every observed blocker before changing draft/merge status.

Do not manually copy connector payloads into the executor. If no supported materialization path exists, record the per-run observation and move to the next distinct evidence task: **recovery common-successor resolution when the successor's own compromise evidence later forks + multi-generation retirement historical-statement revocation/compaction + unlearning lineage reconciliation when S4 fans out into independently compacted S5/S6 descendants + nested privacy-budget lease delegation across allocator generations and partition heal + provider observer authority rotation/compromise with pre/post-rotation observations + GC compact membership-certificate revocation/replacement after multiple fully truncated joint-consensus transitions**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + current-main conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; architecture now additionally covers forked compromise timing, revoked common-successor retirement ordering, double-compacted unlearning remigration, wall-clock-independent privacy lease reconciliation, conflicting delayed provider observers after retention expiry, and successive compact joint-consensus certificates; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen; exact executable gates pending.
