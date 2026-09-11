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
- Therefore no new LAB-086 behavioral, unsafe-seed, compileall, security-reconciliation or conflict PASS is claimed; PR #165 remains draft/open (`mergeable=false`).
- Fresh connector compare after this run's research commit: `main...ee210a47221b6df53f3518aa3af74f76c5b0122b` = `diverged`, ahead 195 / behind 828, merge base `d2c9781f5a60dc9b8b94fc8dba651f804a73e509`. This state-file commit moves `main` again, so obtain another fresh compare before any merge/conflict conclusion.

Completed the recorded distinct fallback and froze `RECOVERY_ANCHOR_RETIREMENT_REVOCATION_UNLEARNING_RESULT_PRIVACY_COMPENSATION_FINALITY_MEMBERSHIP_STALE_GC_V1_FROZEN` in `research/2026-09-11-recovery-anchor-retirement-revocation-unlearning-result-privacy-compensation-finality-membership-stale-gc-v1.md`, main research commit `8bec07398f27db2e2d6c24738b9a78b164fefbbf`; #178 comment `5631564878` records the result.

Key decisions:
- Recovery-policy anchor loss has explicit `PROVEN`, `FLOOR_PROVEN_CONTINUITY_UNKNOWN`, and `UNKNOWN` states. A surviving self-signed successor cannot repair predecessor loss; same-generation incompatible policy digests are equivocation. A monotonic authenticated floor can continue to forbid rollback while blocking new recovery until a higher independently rooted generation commits all conflicting heads and the last undisputed predecessor.
- A reconstructed retirement bridge can later lose authority through interval-scoped revocation/compromise. The independently authenticated non-resurrection floor remains monotonic, but bridge-derived canonical continuity becomes uncertain. Re-signing is not repair; higher bridge recovery must commit the revoked bridge, all surviving conflicting heads, predecessor/floor, and crossed compaction boundary.
- Post-close unlearning worker-result revocation invalidates contributions for the affected evaluation interval. If the remaining original quorum/profile still holds, a durable revalidation record may preserve the certificate; otherwise the certificate and dependent descendants become authority-uncertain until successor re-proof. New workers cannot retroactively vote in a closed epoch.
- Privacy compensation is append-only. Conflicting compensating generations form `PRIVACY_COMPENSATION_FORK`; reconciliation must commit all fork heads and preserve a conservative cumulative-loss floor plus unresolved reservations. No revocation/failover can refund consumed loss.
- Finality checkpoint recovery and replica-set membership transition are separate. New replicas cannot vote before exact checkpoint/evidence catch-up; direct old->new switching is forbidden during recovery; joint authority is required and membership finality never upgrades an `UNKNOWN` external effect.
- After `GC_NEW_CONFIG_COMMITTED`, stale `C_old` loses all future voting/mutation authority but historical evidence may still be required for audit/reconciliation. Replayed old-generation votes/receipts are evidence-only; retention dependencies can block deletion without restoring authority.
- Frozen 42-case RED-first matrix covers all six contracts. This remains architecture/evidence only; exact RED/GREEN is pending.

Primary donors re-verified this run: TUF authenticated threshold/root/rollback discipline; RFC 9162 append-only consistency proofs; NIST SP 800-226 cumulative privacy budgeting; Raft joint consensus and the unsafe disjoint-majority direct-switch failure mode.

## Known failures / blockers
- LAB-086 remains priority #1. Exact local execution of the complete real-ledger closure is still unavailable.
- Direct shell transport cannot currently resolve `github.com`.
- Connector can read pinned source but cannot byte-exactly materialize the whole pinned closure into the executor in this run.
- Complete real-schema LAB-086 tests, unsafe expected-failure seed, full compileall, security reconciliation and current-main conflict audit remain pending.
- PR #165 was 828 commits behind `main` immediately before this state commit; do not infer merge safety from historical conflict observations.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093..100 and subsequent design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against the pinned blob before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and a fresh current-main conflict audit. Fix every observed blocker before changing draft/merge status.

Do not manually copy connector payloads into the executor. If no supported materialization path exists, record the per-run observation and move directly to the next distinct evidence task: **recovery-policy-anchor repair when the new independent anchor is later compromised or forks + retirement non-resurrection-floor proof when all reconstructed bridge continuity evidence has been compacted + unlearning certificate revalidation races with concurrent descendant issuance + privacy compensation reconciliation across participant-set generation change/coordinator failover + finality joint-membership recovery when catch-up attestations are later revoked + GC audit-evidence retention/compaction protocol that cannot let stale `C_old` regain authority or delete evidence needed by unresolved destructive effects**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + current-main conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; architecture now additionally covers recovery-policy-anchor partial loss/equivocation, reconstructed-retirement-bridge revocation, post-close unlearning worker-result revocation, privacy compensating-accounting forks, finality replica membership recovery, and stale-old GC replay/evidence retention; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen; exact executable gates pending.
