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

Completed the recorded distinct fallback and froze `PROVENANCE_RECOVERY_WITNESS_TOMBSTONE_UNLEARNING_BUDGET_PRIVACY_MAPPING_PROVIDER_FAILOVER_AUTHORITY_INVENTORY_V1_FROZEN` in `research/2026-09-11-provenance-recovery-witness-tombstone-unlearning-budget-privacy-mapping-provider-failover-authority-inventory-v1.md`, main commit `9342de3b4b4dbff5c5662c3684cb4b3795c8fb05`; #178 comment `5626199533` records the result.

Key decisions:
- `RECOVERY_ROOT_SIGNED != EQUIVOCATION_RESOLVED`: same-generation incompatible provenance roots remain unresolved until a strictly higher-generation recovery proof binds both roots, the last undisputed predecessor, cutoff and an independent recovery authority; rejected branches cannot later lower the rollback floor.
- `NEW_WITNESS_KEY != NEW_WITNESS_IDENTITY`: witness reassignment and tombstoning are evaluated through stable canonical identity/failure-domain lineage across overlapping membership epochs; cross-signing cannot create extra votes.
- `MULTIPLE_UNLEARNING_ATTESTATIONS != EXACT_DELETION_PROOF`: exact/certified/empirical/unknown proof strengths compose conservatively through ensembles, merge, distillation, embeddings, caches, ANN indexes, adapters and shards.
- `MAPPING_PROOF_EXPIRED != PRIVACY_HISTORY_EXPIRED`: privacy namespace rotation, mapping expiry/deletion, splits and later relinks cannot reduce cumulative spend/reservation/unknown-loss floors.
- `FAILOVER_PROVIDER_CURRENT != PREDECESSOR_RECEIPT_FORK_FINALIZED`: provider failover does not resolve predecessor receipt forks, sequence gaps or timeout-after-send; compensation remains a new external effect.
- `ALL_ENUMERATED_DOMAINS_ACKED != AUTHORITY_UNIVERSE_COMPLETE`: epoch GC requires recursive authenticated enumeration of KMS/HSM/wrapped-key/backup/DR/escrow/offline-recovery/dormant-region/replay-state and parent recovery authorities; shared roots/cross-signing collapse independence.
- Frozen 40-case RED-first matrix across those six domains.

Primary donors: SLSA v1.1 threat model; Sigstore/Rekor transparency model; NIST SP 800-88 Rev. 2; NIST privacy-loss guidance.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact local execution of the complete real-ledger closure.
- Direct shell transport cannot currently resolve `github.com`.
- Connector can read pinned source but this run has no supported non-model connector-to-local-filesystem materialization primitive.
- Complete real-schema LAB-086 tests, unsafe expected-failure seed, full compileall, security reconciliation and current-main conflict audit remain pending.
- Prior state reported PR #165 diverged from current main; do not infer merge safety from historical conflict observations.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093..100 design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against the pinned blob before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and a fresh current-main conflict audit. Fix every observed blocker before changing draft/merge status.

Do not manually copy connector payloads into the executor. If no supported materialization path exists, record the per-run observation and move directly to the next distinct evidence task: **recovery-authority compromise after equivocation resolution + witness tombstone resurrection/replay across compacted membership history + soundness of certified-unlearning bound composition under correlated components + privacy accounting merge/split convergence under resolver disagreement + provider finality evidence revocation after failover + recursive authority-inventory discovery proofs when inventory issuers themselves are recoverable from predecessor authority**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + current-main conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; architecture additionally covers canonical recovery after provenance equivocation, stable witness reassignment/tombstoning, typed unlearning-proof budgets, privacy mapping-proof lifecycle, provider failover/fork finality and recursive authority-inventory completeness; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen; exact executable gates pending.
