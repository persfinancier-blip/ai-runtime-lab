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
- Fresh connector compare after this run's research commit: `main...ee210a47221b6df53f3518aa3af74f76c5b0122b` = `diverged`, ahead 195 / behind 826, merge base `d2c9781f5a60dc9b8b94fc8dba651f804a73e509`. This state-file commit moves `main` again, so obtain another fresh compare before any merge/conflict conclusion.

Completed the recorded distinct fallback and froze `REGISTRY_ROOT_LOSS_RETIREMENT_CHECKPOINT_UNLEARNING_MEMBERSHIP_PRIVACY_REVOCATION_FINALITY_REPLICA_GC_TRANSITION_V1_FROZEN` in `research/2026-09-11-registry-root-loss-retirement-checkpoint-unlearning-membership-privacy-revocation-finality-replica-gc-transition-v1.md`, main research commit `717abfc0e587ad83a168564098af7783906f207b`; #178 comment `5630916530` records the result.

Key decisions:
- A registry recovery event becomes `REGISTRY_RECOVERY_AUTHORITY_UNCERTAIN` when the recovery root that authorized it is later proven compromised for the signing interval. Successor re-signing is not repair; a higher independently rooted recovery-policy generation must commit the uncertain event, every fork head it resolves, and the last undisputed predecessor.
- Partial retirement-checkpoint loss is classified separately from retirement-floor loss. A retained authenticated non-resurrection floor may stay enforceable even when canonical successor continuity is unknown; destructive compaction and branch selection remain blocked until an authenticated bridge repairs continuity.
- Distributed unlearning proof epochs bind both immutable DAG/theorem state and worker-membership generation/digest. Added workers cannot vote in an already-open epoch, removed workers remain interval/revocation checked, and mixed old/new membership quorums are forbidden.
- Privacy participant-attestation revocation after failover cannot refund consumed loss or erase unresolved reservations. If exact contribution becomes unknowable, use the conservative policy bound; a late revocation after release appends a compensating accounting generation rather than rewriting history.
- Finality replica recovery requires authenticated checkpoint predecessor/consistency/invalidation provenance. Replica majority or copying a resolved value cannot recreate missing authority; incompatible surviving heads create `FINALITY_CHECKPOINT_FORK`.
- Destructive-effect finality and GC membership-transition finality are separate. Crash after durable destructive commit but before `GC_NEW_CONFIG_COMMITTED` resumes joint consensus; local `C_new` application or new-only quorum cannot retire `C_old` early.
- Frozen 42-case RED-first matrix covers all six contracts. This remains architecture/evidence only; exact RED/GREEN is pending.

Primary donors re-verified this run: TUF specification v1.0.36 (modified 2026-08-05) threshold/root/rollback discipline; RFC 9162 append-only consistency; NIST SP 800-226 cumulative privacy budgeting; Raft joint consensus.

## Known failures / blockers
- LAB-086 remains priority #1. Exact local execution of the complete real-ledger closure is still unavailable.
- Direct shell transport cannot currently resolve `github.com`.
- Connector can read pinned source but cannot byte-exactly materialize the whole pinned closure into the executor in this run.
- Complete real-schema LAB-086 tests, unsafe expected-failure seed, full compileall, security reconciliation and current-main conflict audit remain pending.
- PR #165 was 826 commits behind `main` immediately before this state commit; do not infer merge safety from historical conflict observations.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093..100 and subsequent design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against the pinned blob before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and a fresh current-main conflict audit. Fix every observed blocker before changing draft/merge status.

Do not manually copy connector payloads into the executor. If no supported materialization path exists, record the per-run observation and move directly to the next distinct evidence task: **recovery-policy continuity when the independent registry recovery-policy anchor is itself partially lost or equivocal + retirement recovery-bridge revocation after continuity was reconstructed + unlearning worker-result revocation after proof-epoch close + privacy compensating-accounting fork/reconciliation after late attestation revocation + finality checkpoint replica-set membership transition during recovery + stale-old-configuration attacks and audit-evidence retention after `GC_NEW_CONFIG_COMMITTED`**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + current-main conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; architecture now additionally covers compromised registry-recovery authority, partial retirement checkpoint loss, worker-membership transitions in open unlearning epochs, post-failover participant-attestation revocation, finality replica loss, and crash-safe `joint -> new` destructive-GC transition; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen; exact executable gates pending.
