# Current Lab State

Last updated: 2026-09-10

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; current connector read confirms `open`, `draft=true`, `mergeable=false`. Keep draft.
- Other open drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected current open issues/PRs; resumed LAB-086 first and re-probed exact source materialization.

Current-run capability observation:
- Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository execution with `Could not resolve host: github.com`.
- GitHub connector reads/writes are available.
- No supported non-model connector-to-local-filesystem byte-exact materialization primitive is exposed in this run. Manual/model reserialization of the security-critical LAB-086 closure remains prohibited by the retained exact-byte gate.
- Therefore no new LAB-086 behavioral, unsafe-seed, compileall, security-reconciliation or conflict PASS is claimed; PR #165 remains draft.

Completed the recorded distinct fallback and froze `OBSERVER_EXPIRY_HOLDOUT_PROVENANCE_PRIVACY_WITNESS_ROTATION_RETENTION_FENCE_ROLLBACK_PQ_ASYMMETRIC_RECOVERY_V1_FROZEN` in `research/2026-09-10-observer-expiry-holdout-provenance-privacy-witness-rotation-retention-fence-rollback-pq-asymmetric-recovery-v1.md`, main commit `179310fa5c62188e9cfb017ebb0551a0d9f382c7`; #178 comment `5616203300` records the result.

Key decisions:
- `EMERGENCY_MEMBER_EXPIRED != EMERGENCY_EVIDENCE_EXPIRED`: observer expiry removes future voting authority but preserves prior checkpoint/conflict evidence; replacement is an explicit successor transition and partial recovery-authority compromise is evaluated by signer/failure-domain overlap.
- `SYNTHETIC != INDEPENDENT` and `DISJOINT_ROWS != DISJOINT_INFORMATION`: reusable-holdout provenance is a DAG across source data, generators/models, analyst/controller state and prior disclosures. Derived/synthetic data that consumed holdout feedback inherits exposure lineage unless a separately justified guarantee proves otherwise.
- `WITNESS_ROTATED != SPEND_FLOOR_ROTATED_AWAY`: privacy spend-witness rotation carries the maximum authenticated cumulative floor plus unresolved uncertainty; stale witness eviction removes future authority but does not erase old signed evidence or equivocation.
- `CONTROL_PLANE_FENCE_CURRENT != RESOURCE_FENCE_CURRENT` and `JOB_AUTHORIZED_ONCE != JOB_AUTHORIZED_AT_EXECUTION`: retention destructive operations require rollback-resistant resource-side fence generations and execution-time reauthorization; ambiguous retries reconcile before reacquiring destructive authority.
- `EQUIVALENCE_POLICY_RESTORED != OLD_EQUIVALENCE_POLICY_CURRENT`, `DC_REPLACED != OLD_TICKET_ANCESTRY_SANITIZED`, and `REGION_RECOVERED_FOR_1RTT != REGION_RECOVERED_FOR_RESUMPTION_OR_0RTT`: cross-SNI/PQ/ECH recovery is generation-bound and staged by identity, ticket-admission/revocation, then replay convergence.
- Frozen 40-case RED-first matrix across those five domains.

Primary donors: RFC 9162; Dwork et al. 2015 reusable holdout; Generic Holdout; NIST SP 800-226; RFC 9345; RFC 9846.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact local execution of the complete real-ledger closure.
- Direct shell transport cannot currently resolve `github.com`.
- Connector can read pinned source but this run has no supported non-model connector-to-local-filesystem materialization primitive.
- Complete real-schema LAB-086 tests, unsafe expected-failure seed, full compileall, security reconciliation and branch/main conflict audit remain pending.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093..100 design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against the pinned blob before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

Do not manually copy connector payloads into the executor. If no supported materialization path exists, record the per-run observation and move directly to the next distinct evidence task: **observer recovery-authority membership churn/compromise-overlap and emergency-evidence custody + attestable holdout-provenance roots/generator rollback + privacy spend-witness scope split/merge without floor laundering + retention resource-proxy/delegated-fence rollback and destructive retry fencing + PQ/ECH ticket-key retirement/re-encryption and cross-region ancestry convergence after certificate/DC replacement**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; architecture now additionally covers observer emergency-expiry/replacement under partial recovery-authority compromise, semantic provenance of derived/synthetic holdouts, privacy witness rotation/stale eviction, rollback-resistant retention resource fencing/offline replay, and asymmetric cross-SNI PQ/ECH/DC regional recovery; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen; exact executable gates pending.
