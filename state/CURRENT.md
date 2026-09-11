# Current Lab State

Last updated: 2026-09-11

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and current-main conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`. Keep draft.
- Other open drafts inspected: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues and active PRs; resumed LAB-086 first and re-probed exact source materialization.

Current-run capability observation:
- Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` again failed before repository execution with `Could not resolve host: github.com`.
- GitHub connector reads/writes remain available.
- No supported non-model connector-to-local-filesystem byte-exact materialization primitive is exposed in this run. Manual/model reserialization of the security-critical LAB-086 closure remains prohibited by the retained exact-byte gate.
- Therefore no new LAB-086 behavioral, unsafe-seed, compileall, security-reconciliation or conflict PASS is claimed; PR #165 remains draft. Connector inspection reconfirmed `state=open`, `draft=true`, `mergeable=false`, head `ee210a47221b6df53f3518aa3af74f76c5b0122b`.
- The last verified compare before this run's new main commit was `diverged`, ahead 195 / behind 819. Because this run added another main commit, PR #165 is now at least 820 commits behind main; obtain a fresh supported compare before any conflict conclusion.

Completed the recorded distinct fallback and froze `ASSESSMENT_FORK_RETIREMENT_UNLEARNING_RACE_PRIVACY_SHARDS_FINALITY_CYCLES_GC_JOINT_CONSENSUS_V1_FROZEN` in `research/2026-09-11-assessment-fork-retirement-unlearning-race-privacy-shards-finality-cycles-gc-joint-consensus-v1.md`, main commit `c0f432781a5b60654c30b26ef7beaaacafd4d428`; #178 comment `5629862129` records the result.

Key decisions:
- Compromise-assessment fork recovery counts canonical independent failure domains after interval-scoped compromise/correlation filtering. A higher recovery generation must commit every fork head being resolved; nominal key/issuer count, timestamps and arrival order cannot select a winner. Already-established rollback/equivocation floors are monotonic.
- Verifier-retirement bridge revocation after predecessor compaction yields `RETIREMENT_CONTINUITY_UNCERTAIN` unless retained authenticated predecessor checkpoint/tombstone material supports an independent higher-generation bridge. Successor-only reconstruction and same-compromised-authority re-signing are not recovery.
- Unlearning ancestor GC is an explicit immutable DAG epoch. New descendants depending on a retiring ancestor are fenced/versioned; if any such descendant appears after the snapshot and before commit, GC aborts/recomputes. Every live dependent branch must independently re-proof/re-anchor before ancestor proof deletion.
- Multi-shard privacy reservation release uses one global `analysis_id`/release generation plus participant-set digest and idempotent shard acknowledgements. Missing/lagging/unknown shards block release; participant-set disagreement uses the conservative union; consumed privacy loss is never refunded.
- Finality caches/materialized views form an explicit dependency graph. Invalidation and recomputation operate by SCC plus dependency-generation vectors: one invalid/unknown edge makes the whole SCC stale and propagates downstream; cycles without independent source evidence resolve to `UNKNOWN`; stale `NO_EFFECT` cannot authorize blind retry.
- Distributed destructive `CAN_RESTORE` GC membership changes use a Raft-style joint configuration: no direct `C_old -> C_new` switch during an open epoch; safety-critical decisions in joint mode require the configured old and new quorums, added replicas must catch up to the exact snapshot, and retirement cannot be used merely to edit away an unreachable dissenting inventory replica.
- Frozen 40-case RED-first matrix covers shared-domain assessment forks, post-compaction bridge revocation, descendant/re-proof races, multi-shard privacy release, finality-cache SCC invalidation, and joint-consensus membership changes during destructive GC.

Primary donors: TUF root continuity/threshold rotation and rollback discipline; RFC 9162 append-only consistency proofs; NIST SP 800-226 cumulative privacy composition; Raft joint consensus for membership changes; NIST SP 800-88 Rev. 2 cryptographic-erasure/key-copy assurance.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact local execution of the complete real-ledger closure.
- Direct shell transport cannot currently resolve `github.com`.
- Connector can read pinned source but this run has no supported non-model connector-to-local-filesystem materialization primitive.
- Complete real-schema LAB-086 tests, unsafe expected-failure seed, full compileall, security reconciliation and current-main conflict audit remain pending.
- PR #165 is at least 820 commits behind current main after this run's new research commit; do not infer merge safety from historical conflict observations.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093..100 design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against the pinned blob before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and a fresh current-main conflict audit. Fix every observed blocker before changing draft/merge status.

Do not manually copy connector payloads into the executor. If no supported materialization path exists, record the per-run observation and move directly to the next distinct evidence task: **assessment issuer-domain registry rollback/equivocation + verifier-retirement tombstone trust-root rotation + unlearning DAG snapshot isolation across distributed proof workers + privacy participant-set attestation/coordinator failover + finality-cache SCC compaction/checkpointing + destructive-GC joint-consensus recovery after coordinator crash or split-brain during membership transition**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + current-main conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; architecture now additionally covers shared-domain assessment-fork recovery, post-compaction retirement-bridge revocation, unlearning DAG GC races, multi-shard reservation release, SCC-aware finality-cache invalidation, and joint-consensus distributed-GC membership changes; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen; exact executable gates pending.
