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
- Fresh compare: PR #165 branch vs current `main` is `diverged`, ahead 195 / behind 815. Historical conflict conclusions are not sufficient for merge safety.

Completed the recorded distinct fallback and froze `RECOVERY_FORK_JOINT_BRIDGE_UNLEARNING_REANCHOR_RESOLVER_EQUIVOCATION_FINALITY_OVERLAP_SCC_INVALIDATION_V1_FROZEN` in `research/2026-09-11-recovery-fork-joint-bridge-unlearning-reanchor-resolver-equivocation-finality-overlap-scc-invalidation-v1.md`, main commit `ac369c9775efa2b947ee66f075af071cb74d0847`; #178 comment `5628485321` records the result.

Key decisions:
- Competing emergency successors with different partially compromised canonical-domain intersections remain an explicit `RECOVERY_FORK`; no timestamp/raw-key-majority winner. Resolution requires a higher generation committing both fork heads, the last uncontested predecessor, interval-scoped compromise evidence, and an independently sufficient admissible quorum while preserving the rollback/equivocation floor.
- Joint witness-membership/checkpoint-authority rotation is one canonical bridge. If bridge authority is revoked after retention starts, replacement must commit the revoked bridge plus the already-reached retention floor and preserve enough evidence for supported stale verifiers; prematurely deleted required predecessor evidence is unrecoverable and fails closed.
- Unlearning theorem/profile roots are part of the certificate trust path. Root compromise taints dependent certificates across the supersession DAG; re-signing is not re-proof, and a weaker independently re-established guarantee must be recorded as an explicit downgrade.
- Resolver assertions bind source log head, cutoff, source-set digest, namespace epoch and accounting floor. Source-log equivocation forces a conservative join of privacy spend/reservations and blocks budget reset until a recovered source generation commits both conflicting heads and their uncontested ancestor.
- Provider-finality generation handoff evaluates time-scoped admissible failure-domain overlap. Effects spanning an interval where overlap is insufficient remain `EFFECT_UNKNOWN`/forked; failover cannot manufacture finality.
- `CAN_RESTORE` authority extinction is a snapshot-bound SCC/fixed-point proof. Edge additions/removals/reclassification, inventory expansion, or issuer revocation invalidate the affected dependency cone; destructive GC requires recomputation on the new authenticated snapshot.
- Frozen 40-case RED-first matrix across those six domains.

Primary donors: TUF root continuity/rollback defense; RFC 9162 append-only consistency/split-view auditing; certified machine-unlearning theorem-scoped guarantees; NIST SP 800-226 cumulative privacy-budget composition; NIST SP 800-88 Rev. 2 cryptographic-erasure/key-copy assurance.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact local execution of the complete real-ledger closure.
- Direct shell transport cannot currently resolve `github.com`.
- Connector can read pinned source but this run has no supported non-model connector-to-local-filesystem materialization primitive.
- Complete real-schema LAB-086 tests, unsafe expected-failure seed, full compileall, security reconciliation and current-main conflict audit remain pending.
- PR #165 is now at least 815 commits behind current main; do not infer merge safety from historical conflict observations.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093..100 design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against the pinned blob before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and a fresh current-main conflict audit. Fix every observed blocker before changing draft/merge status.

Do not manually copy connector payloads into the executor. If no supported materialization path exists, record the per-run observation and move directly to the next distinct evidence task: **recovery-fork convergence when the higher recovery authority itself is later partially compromised + retirement/expiry of stale-verifier obligations after joint membership/checkpoint retention + safe garbage collection of revoked/superseded unlearning proofs without losing re-anchor provenance + decomposing conservative privacy joins after source-log recovery without refunding cumulative spend + retroactive compromise of one provider-finality generation after successor activation + linearizable graph-snapshot/epoch rules preventing `CAN_RESTORE` inventory mutation from racing destructive GC**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + current-main conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; architecture now additionally covers explicit recovery-fork resolution under partial compromise, post-retention joint-bridge revocation/recovery, unlearning trust-root compromise/re-anchoring, resolver/source-log equivocation, time-scoped provider-finality overlap, and dynamic `CAN_RESTORE` SCC proof invalidation; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen; exact executable gates pending.
