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
- Therefore no new LAB-086 behavioral, unsafe-seed, compileall, security-reconciliation or conflict PASS is claimed; PR #165 remains draft.
- Fresh connector compare before this run's research commit: `main...ee210a47221b6df53f3518aa3af74f76c5b0122b` = `diverged`, ahead 195 / behind 823, merge base `d2c9781f5a60dc9b8b94fc8dba651f804a73e509`. Because this run then added a main research commit, obtain another fresh compare before any merge/conflict conclusion.

Completed the recorded distinct fallback and froze `ISSUER_REGISTRY_RETIREMENT_ROOT_UNLEARNING_SNAPSHOT_PRIVACY_FAILOVER_FINALITY_CHECKPOINT_GC_RECOVERY_V1_FROZEN` in `research/2026-09-11-issuer-registry-retirement-root-unlearning-snapshot-privacy-failover-finality-checkpoint-gc-recovery-v1.md`, main commit `d02929872609f8fa1b1c44ac2df7ef67725c8199`; #178 comment `5630364736` records the result.

Key decisions:
- Assessment signatures bind an authenticated issuer-domain registry generation/head. Same-generation membership disagreement is explicit `ISSUER_REGISTRY_EQUIVOCATION`; recovery must commit every conflicting head being resolved plus the last undisputed predecessor. Canonical failure domains, not nominal keys, determine independence.
- Verifier-retirement tombstones are authority-bearing history. Trust-root rotation requires predecessor-to-successor continuity; predecessor compromise in the bridge interval yields `RETIREMENT_CONTINUITY_UNCERTAIN`, and successor-only re-signing is not recovery. Split-view tombstone heads block compaction.
- Distributed unlearning proof workers operate on one immutable authenticated DAG snapshot `(generation, root digest, dependency-profile digest)`. Mixed snapshots/profiles cannot be aggregated; new descendants/edges/revocations before commit invalidate the affected proof cone.
- Privacy analyses bind one stable `analysis_id`, accounting generation, participant-set digest and coordinator epoch. Failover adopts the conservative union of unresolved participant claims; conflicting successor release/consume heads create `PRIVACY_COORDINATOR_FORK`; consumed privacy loss is never refunded.
- Finality-cache SCC checkpoints retain source-evidence digests, dependency-generation vectors, authority generation, unresolved gaps/forks and predecessor checkpoint. Cycles without independent source evidence resolve to `UNKNOWN`; compaction cannot erase split-view/invalidation provenance.
- Destructive `CAN_RESTORE` GC recovers through durable joint-consensus state. Coordinator identity is not authority; old-only or new-only quorum is insufficient while joint transition is open, added replicas must catch up to the exact snapshot, and competing coordinator phase/membership heads create `GC_COORDINATOR_FORK` and block destruction.
- Frozen 40-case RED-first matrix covers all six contracts. This remains architecture/evidence only; exact RED/GREEN is pending.

Primary donors: TUF spec v1.0.36 root continuity/rollback/threshold discipline; RFC 9162 append-only consistency/split-view auditing; NIST SP 800-226 cumulative privacy budgeting; Raft joint consensus.

## Known failures / blockers
- LAB-086 remains priority #1. Exact local execution of the complete real-ledger closure is still unavailable.
- Direct shell transport cannot currently resolve `github.com`.
- Connector can read pinned source but cannot byte-exactly materialize the whole pinned closure into the executor in this run.
- Complete real-schema LAB-086 tests, unsafe expected-failure seed, full compileall, security reconciliation and current-main conflict audit remain pending.
- PR #165 was 823 commits behind main immediately before this run's new main research commit; do not infer merge safety from historical conflict observations.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093..100 and subsequent design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against the pinned blob before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and a fresh current-main conflict audit. Fix every observed blocker before changing draft/merge status.

Do not manually copy connector payloads into the executor. If no supported materialization path exists, record the per-run observation and move directly to the next distinct evidence task: **issuer-registry recovery when the registry recovery root itself is compromised + retirement-tombstone continuity after partial checkpoint loss + distributed unlearning worker-membership changes during an open proof snapshot + privacy participant-attestation revocation after coordinator failover + finality-checkpoint recovery after partial replica loss + safe retirement of the old GC configuration after joint-consensus destructive commit, including crash/restart at the joint-to-new transition boundary**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + current-main conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; architecture now additionally covers issuer-registry rollback/equivocation, retirement-root continuity, distributed unlearning snapshot isolation, privacy participant/coordinator failover, SCC finality checkpointing, and destructive-GC joint-consensus recovery; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen; exact executable gates pending.
