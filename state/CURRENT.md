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
- Therefore no new LAB-086 behavioral, unsafe-seed, compileall, security-reconciliation or conflict PASS is claimed; PR #165 remains draft/open/non-mergeable.
- Fresh compare: PR #165 branch vs current `main` is `diverged`, ahead 195 / behind 813. Historical conflict conclusions are not sufficient for merge safety.

Completed the recorded distinct fallback and froze `RECOVERY_INTERSECTION_CHECKPOINT_ROTATION_UNLEARNING_SUPERSESSION_RESOLVER_CUTOFF_FINALITY_GENERATION_AUTHORITY_SCC_V1_FROZEN` in `research/2026-09-11-recovery-intersection-checkpoint-rotation-unlearning-supersession-resolver-cutoff-finality-generation-authority-scc-v1.md`, main commit `460b564bcd72aa1f7adffec0ebea03567f68c8cf`; #178 comment `5627939326` records the result.

Key decisions:
- Recovery/finality continuity counts admissible canonical failure-domain intersection after interval-scoped compromise/correlation filtering, not raw key overlap. Partial compromise may leave continuity admissible only if threshold and required intersection still hold; otherwise independent recovery/reconciliation is required.
- Simultaneous witness-membership and checkpoint-authority rotation is one authenticated bridge over one canonical payload. Compaction/GC must retain enough predecessor evidence for every supported stale verifier; equivocation in either role disputes the whole bridge.
- Certified-unlearning theorem/profile versions form an acyclic supersession/revocation DAG. Later stronger profiles do not retroactively strengthen old certificates; revoked assumptions propagate through dependent descendants unless independently re-proved; unsupported correlated composition degrades to UNKNOWN.
- Privacy resolver assertions bind evidence cutoff and source-set digest. Resolver/source rollback cannot lower the monotonic accounting floor; fork convergence is a cutoff-aware conservative join and disjointness only separates future accounting within its proof scope.
- Provider-finality authority generations must commit predecessor UNKNOWN/gaps/forks/compensation-pending operations. Competing successors create `FINALITY_GENERATION_FORK`; revoking receipt authority changes receipt trust, not external effect truth.
- Authority extinction is evaluated on an authenticated snapshot-bound `CAN_RESTORE` graph: collapse SCCs, treat unknown/disputed restoration paths as live, iterate a fixed point from externally grounded dead components, and recompute if the graph changes before GC.
- Frozen 40-case RED-first matrix across those six domains.

Primary donors: TUF root continuity/rollback defense; RFC 9162 consistency proofs and split-view auditing; Guo et al. certified data removal; NIST SP 800-226 privacy-budget composition; NIST SP 800-88 Rev. 2 cryptographic-erasure assurance/key-copy coverage; quorum-intersection literature as structural donor.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact local execution of the complete real-ledger closure.
- Direct shell transport cannot currently resolve `github.com`.
- Connector can read pinned source but this run has no supported non-model connector-to-local-filesystem materialization primitive.
- Complete real-schema LAB-086 tests, unsafe expected-failure seed, full compileall, security reconciliation and current-main conflict audit remain pending.
- PR #165 is now at least 813 commits behind current main; do not infer merge safety from historical conflict observations.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093..100 design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against the pinned blob before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and a fresh current-main conflict audit. Fix every observed blocker before changing draft/merge status.

Do not manually copy connector payloads into the executor. If no supported materialization path exists, record the per-run observation and move directly to the next distinct evidence task: **recovery-fork resolution when competing emergency successors retain different partially compromised domain intersections + revocation/recovery of a joint membership/checkpoint bridge after stale-verifier retention has begun + root-of-trust compromise inside an unlearning supersession DAG and proof re-anchoring + resolver evidence-cutoff attestations under source-log equivocation + provider-finality generation handoff when overlap is only partially admissible across time + incremental/SCC proof invalidation when `CAN_RESTORE` inventory edges are added, removed, or reclassified during a GC epoch**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + current-main conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; architecture now additionally covers partial-compromise quorum intersection, joint membership/checkpoint-authority rotation and retention, unlearning supersession/revocation DAGs, resolver evidence/source cutoff rollback, provider-finality authority-generation transitions, and snapshot-bound dynamic `CAN_RESTORE` SCC/fixed-point proofs; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen; exact executable gates pending.
