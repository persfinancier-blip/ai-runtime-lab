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
- Fresh compare after this run's research commit: PR #165 branch vs current `main` is `diverged`, ahead 195 / behind 810. Historical conflict conclusions are not sufficient for merge safety.

Completed the recorded distinct fallback and froze `RECOVERY_AUTHORITY_COMPROMISE_WITNESS_RESURRECTION_UNLEARNING_CORRELATION_PRIVACY_CONVERGENCE_PROVIDER_REVOCATION_AUTHORITY_RECURSION_V1_FROZEN` in `research/2026-09-11-recovery-authority-compromise-witness-resurrection-unlearning-correlation-privacy-convergence-provider-revocation-authority-recursion-v1.md`, main commit `721ade72c290497bf28b8f2be435221898b07bfe`; #178 comment `5626733222` records the result.

Key decisions:
- `RECOVERY_PROOF_PREVIOUSLY_ACCEPTED != RECOVERY_AUTHORITY_FOREVER_TRUSTED`: later compromise overlapping issuance reopens affected recovery decisions, but never lowers the learned rollback/equivocation floor; a strictly higher recovery generation must bind prior conflicts, compromise evidence and an independently authorized successor.
- `COMPACT_HISTORY_ACCEPTS_WITNESS_ID != WITNESS_AUTHORIZED_AT_EVENT_EPOCH`: membership compaction must preserve authenticated witness identity, failure-domain, tombstone/reassignment, threshold and interval continuity; replay of old compact roots cannot resurrect tombstoned witnesses.
- `CERTIFIED(A) + CERTIFIED(B) != CERTIFIED(A∪B)` for correlated residual state unless the certificate's theorem permits that composition; untracked shared optimizer/cache/embedding/distillation lineage yields conservative/unknown result.
- Resolver disagreement/split/merge cannot mint fresh privacy budget; cumulative spend/reservation/unknown-loss floor is monotonic and independent of one mutable identity graph.
- Provider finality evidence has separate effect-state and authority-validity dimensions. Later issuer compromise can make a receipt disputed; destructive effects remain `EFFECT_UNKNOWN` absent independent reconciliation, and failover cannot silently finalize predecessor forks.
- `INVENTORY_SIGNED_COMPLETE != AUTHORITY_UNIVERSE_COMPLETE`: authority-inventory completeness is recursive; an inventory issuer recoverable from predecessor authority makes an extinction/GC proof circular until predecessor extinction is independently established.
- Frozen 40-case RED-first matrix across those six domains.

Primary donors: TUF root continuity/rollback model; SLSA provenance trust boundary; NIST privacy-budget definitions; NIST SP 800-88 Rev. 2; recent certified-removal work for guarantee-specific unlearning assumptions.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact local execution of the complete real-ledger closure.
- Direct shell transport cannot currently resolve `github.com`.
- Connector can read pinned source but this run has no supported non-model connector-to-local-filesystem materialization primitive.
- Complete real-schema LAB-086 tests, unsafe expected-failure seed, full compileall, security reconciliation and current-main conflict audit remain pending.
- PR #165 is now at least 810 commits behind current main; do not infer merge safety from historical conflict observations.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093..100 design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against the pinned blob before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and a fresh current-main conflict audit. Fix every observed blocker before changing draft/merge status.

Do not manually copy connector payloads into the executor. If no supported materialization path exists, record the per-run observation and move directly to the next distinct evidence task: **emergency recovery authority whose own recovery root overlaps the compromised predecessor + authenticated checkpoint anchoring for compacted witness membership + revocation/recomputation of certified-unlearning claims after a theorem/profile defect + privacy-accounting convergence when resolver versions fork/rollback + quorum/fork handling for competing provider-finality authorities + fixed-point authority-inventory completeness with unknown or cyclic `CAN_RESTORE` edges**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + current-main conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; architecture now additionally covers recovery-authority compromise after equivocation resolution, witness tombstone resurrection under compaction, correlated certified-unlearning composition, privacy resolver convergence, provider-finality evidence revocation, and recursive authority-inventory issuer recovery; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen; exact executable gates pending.
