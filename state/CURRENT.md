# Current Lab State

Last updated: 2026-09-11

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and current-main conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`. Keep draft.
- Other open drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues and active PRs; resumed LAB-086 first and re-probed exact source materialization.

Current-run capability observation:
- Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository execution with `Could not resolve host: github.com`.
- GitHub connector reads/writes are available.
- No supported non-model connector-to-local-filesystem byte-exact materialization primitive is exposed in this run. Manual/model reserialization of the security-critical LAB-086 closure remains prohibited by the retained exact-byte gate.
- Therefore no new LAB-086 behavioral, unsafe-seed, compileall, security-reconciliation or conflict PASS is claimed; PR #165 remains draft.
- Fresh compare: PR #165 branch vs current `main` is `diverged`, ahead 195 / behind 811. Historical conflict conclusions are not sufficient for merge safety.

Completed the recorded distinct fallback and froze `EMERGENCY_RECOVERY_CHECKPOINT_UNLEARNING_REVOCATION_PRIVACY_RESOLVER_PROVIDER_FINALITY_AUTHORITY_FIXED_POINT_V1_FROZEN` in `research/2026-09-11-emergency-recovery-checkpoint-unlearning-revocation-privacy-resolver-provider-finality-authority-fixed-point-v1.md`, main commit `8c0308046579b2c3304bb89c1e1e8612ce7c0e7a`; #178 comment `5627350123` records the result.

Key decisions:
- A recovery successor cannot use a predecessor authority known compromised over the transition interval as the independent authorization needed to restore trust. Overlapping emergency roots count by canonical failure domain, not key count; circular cross-signing does not create trust.
- Compacted witness membership requires an authenticated predecessor checkpoint plus continuity/consistency proof. Inclusion under a signed compact root is insufficient; inconsistent heads are explicit equivocation and block GC.
- Certified-unlearning evidence is theorem/profile-scoped. A soundness/profile defect revokes affected claims as authorization evidence; resigning old results is not recomputation, and correlated component certificates compose only when their theorem explicitly permits it.
- Privacy resolver fork/rollback converges through a monotonic conservative accounting floor independent of one mutable resolver version. Rollback/split/version rotation cannot resurrect privacy budget.
- Competing valid provider-finality statements create `FINALITY_FORK`; failover cannot silently supersede predecessor unknown/fork state, and signer quorum is counted by canonical failure domain.
- Authority extinction is a fixed-point property over recursive `CAN_RESTORE` edges. Unknown edges remain live for GC; cycles require externally grounded break evidence; the inventory/completeness issuer is itself part of the restoration graph.
- Frozen 40-case RED-first matrix across those six domains.

Primary donors: TUF root continuity; RFC 9162 consistency proofs/auditing; Guo et al. certified data removal; NIST SP 800-226 privacy-budget definition; NIST SP 800-88 Rev. 2 sanitization/key-management guidance.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact local execution of the complete real-ledger closure.
- Direct shell transport cannot currently resolve `github.com`.
- Connector can read pinned source but this run has no supported non-model connector-to-local-filesystem materialization primitive.
- Complete real-schema LAB-086 tests, unsafe expected-failure seed, full compileall, security reconciliation and current-main conflict audit remain pending.
- PR #165 is now at least 811 commits behind current main; do not infer merge safety from historical conflict observations.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093..100 design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against the pinned blob before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and a fresh current-main conflict audit. Fix every observed blocker before changing draft/merge status.

Do not manually copy connector payloads into the executor. If no supported materialization path exists, record the per-run observation and move directly to the next distinct evidence task: **recovery-root set intersection and partial-compromise admissibility across emergency generations + checkpoint co-sign/retention rules when witness membership and checkpoint authority rotate together + supersession DAGs for certified-unlearning theorem/profile versions + resolver-evidence cutoff rollback and conservative join proofs + transition rules for competing provider-finality quorum generations + strongly-connected-component/fixed-point proofs for authority inventories whose `CAN_RESTORE` graph changes during GC**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + current-main conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; architecture now additionally covers compromised emergency recovery overlap, authenticated compact-membership checkpoint anchoring, theorem/profile revocation for certified unlearning, privacy resolver fork/rollback convergence, provider-finality quorum forks, and fixed-point authority inventory with unknown/cyclic restoration edges; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen; exact executable gates pending.
