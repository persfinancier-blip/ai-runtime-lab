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
- Fresh compare after the research commit: PR #165 is `diverged`, ahead 195 / behind 844, merge base `d2c9781f5a60dc9b8b94fc8dba651f804a73e509`, main/base then `81854ca10ca74d98c699aaa79fc7975202a65d42`. This final state-only commit advances main once more, so refresh again immediately before any integration decision.

Completed the recorded distinct fallback and froze `RECOVERY_ANCHOR_ROTATION_RETIREMENT_MULTIREVOKE_UNLEARNING_PROPAGATION_PRIVACY_VERSION_COMPENSATION_CHAIN_GC_JOINT_LOSS_V1_FROZEN` in `research/2026-09-11-recovery-anchor-retirement-multirevoke-unlearning-propagation-privacy-version-compensation-chain-gc-joint-loss-v1.md`, main commit `81854ca10ca74d98c699aaa79fc7975202a65d42`; #178 comment `5636660373` records the result.

Key decisions:
- Recovery-generation anchor rotation after a resolved recovery-of-recovery fork must authenticate the accepted predecessor, commit all known competing heads, preserve inherited compromise/non-resurrection floors, and use predecessor+successor authority continuity when the authority set changes. Loss/revocation of the sole surviving compact continuity proof yields `RECOVERY_ANCHOR_CONTINUITY_UNRECOVERABLE` rather than self-bootstrap.
- Multiple revoked verifier-retirement checkpoints may be bypassed only through surviving authenticated bridge evidence that preserves a monotonic retirement floor and commits the bypassed checkpoint/range. Missing continuity blocks positive claims but never resurrects a verifier.
- A stale unlearning replica that propagated descendants to another partition creates transitive revalidation obligations. Partition healing requires exact descendant/frontier exchange; omitted or unreconstructable dependencies become `UNLEARNING_DEPENDENCY_UNKNOWN` and fail closed.
- Privacy accounting lineage is independent of coordinator/accountant version. A newer accountant may lower the numeric bound only by reproducibly reevaluating the exact same immutable released-analysis event set under an authorized tighter method; deletion/retraction never refunds released privacy loss and coordinator failover never mints new budget.
- Provider E1/E2/E3 original/compensation/repair effects each retain independent immutable identities. Late authenticated evidence is merged monotonically; contradictory evidence creates uncertainty/fork rather than freshness-based selection. Provider idempotency retention expiry is not proof of no prior effect and does not authorize blind redispatch.
- GC compact-root succession and membership finality are separate. While joint consensus is authoritative, neither old-only nor new-only survivors can authorize destructive GC. If replica loss makes the `C_new` membership commit unprovable, state is `GC_MEMBERSHIP_FINALITY_UNKNOWN` and further destructive GC is blocked.
- Frozen 48-case RED-first matrix covers all six contracts. Architecture/evidence only; exact RED/GREEN pending.

Primary donors re-verified this run: TUF 1.0.36 predecessor/successor trust continuity and rollback rejection; RFC 9162 append-only consistency proofs; NIST SP 800-226 cumulative privacy budgeting; AWS idempotency identity/TTL semantics; Raft joint-consensus membership and new-replica catch-up discipline.

## Known failures / blockers
- LAB-086 remains priority #1. Exact local execution of the complete real-ledger closure is still unavailable.
- Direct shell transport cannot currently resolve `github.com`.
- Connector can read pinned source but cannot byte-exactly materialize the whole pinned closure into the executor in this run.
- Complete real-schema LAB-086 tests, unsafe expected-failure seed, full compileall, security reconciliation and current-main conflict audit remain pending.
- PR #165 was 844 commits behind at the latest compare, and this final state-only commit advances main again; refresh compare before integration.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093..100 and subsequent design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against the pinned blob before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and a fresh current-main conflict audit. Fix every observed blocker before changing draft/merge status.

Do not manually copy connector payloads into the executor. If no supported materialization path exists, record the per-run observation and move directly to the next distinct evidence task: **recovery-anchor successor authority independence/cut-set validation after the recovery-of-recovery rotation + retirement bridge witness-set compaction after multiple revocations + unlearning propagated-descendant closure after one partition compacts its local dependency detail + privacy accountant-version rollback/equivocation after a tighter-bound transition + provider compensation-ledger partition/heal with delayed E1/E2/E3 evidence + GC joint-configuration recovery from snapshot when the surviving replicas disagree on whether `C_new` committed**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + current-main conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; architecture now additionally covers recovery-generation anchor rotation after recovery-of-recovery forks, multi-revocation retirement continuity, propagated stale unlearning descendants, accountant-version privacy reconciliation, E1/E2/E3 compensation ambiguity, and destructive-GC joint-consensus replica loss; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen; exact executable gates pending.
