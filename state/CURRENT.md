# Current Lab State

Last updated: 2026-09-11

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`. Keep draft.
- Other open drafts remain LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues and active PRs; resumed LAB-086 first and re-probed exact source materialization.

Current-run capability observation:
- Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository execution with `Could not resolve host: github.com`.
- GitHub connector reads/writes are available.
- No supported non-model connector-to-local-filesystem byte-exact materialization primitive is exposed in this run. Manual/model reserialization of the security-critical LAB-086 closure remains prohibited by the retained exact-byte gate.
- Therefore no new LAB-086 behavioral, unsafe-seed, compileall, security-reconciliation or conflict PASS is claimed; PR #165 remains draft.
- Fresh compare against current `main` reports PR #165 `diverged`, ahead by 195 commits and behind by 806; merge-base remains `d2c9781f5a60dc9b8b94fc8dba651f804a73e509`. This is conflict-risk evidence only, not a completed conflict audit.

Completed the recorded distinct fallback and froze `PROVENANCE_ROOT_ROLLBACK_WITNESS_REASSIGNMENT_UNLEARNING_COMPOSITION_PRIVACY_NAMESPACE_RECEIPT_FINALITY_AUTHORITY_INVENTORY_V1_FROZEN` in `research/2026-09-11-provenance-root-rollback-witness-reassignment-unlearning-composition-privacy-namespace-receipt-finality-authority-inventory-v1.md`, main commit `1bbd52793e31e6d95100c8c600194c0838947ae6`; #178 comment `5625611673` records the result.

Key decisions:
- `VALID_PROVENANCE_SIGNATURE != CURRENT_CANONICAL_PROVENANCE_ROOT`: assessment evidence binds monotonic root generation, predecessor digest, transitive evidence closure, policy/collector/issuer identity and event cutoff; stale-root replay is rollback and same-generation incompatible roots are explicit equivocation.
- `KEY_IDENTITY_CHANGED != FAILURE_DOMAIN_CHANGED`: witness quorum canonicalizes stable witness/failure-domain identity across rotation, cross-signing, collision, reassignment and membership epochs; circular successor cross-signing cannot bootstrap authority.
- `UNLEARNING_ATTESTED != HOLDOUT_INFLUENCE_PROVEN_ABSENT`: deletion evidence has explicit proof strength (`EXACT_DELETION_PROOF`, `CERTIFIED_BOUND`, `EMPIRICAL_APPROXIMATION`, `UNKNOWN`) and composes conservatively through ensembles, merge, distillation, caches, embeddings and approximate indexes.
- `TOMBSTONE_NAMESPACE_ROTATED != PRIVACY_ACCOUNTING_RESET`: namespace rotation/collision/split/relink recovery keeps cumulative spend/reservation/unknown-loss floors monotonic while avoiding unnecessary identity disclosure.
- `VALID_SIGNED_RECEIPT != FINAL_CANONICAL_EXTERNAL_EFFECT_HISTORY`: provider sequence forks remain unresolved until provider-specific authenticated finality evidence exists; compaction preserves gaps/forks/revocations/compensations.
- `INVENTORY_ATTESTED != AUTHORITY_UNIVERSE_COMPLETE`: ticket-security-epoch GC requires recursively auditable enumeration of KMS/HSM/backup/DR/escrow/offline recovery/replica/replay-state and recovery-authority domains; later compromise/discovery reopens extinction proof and quarantines affected resumption without lowering the epoch floor.
- Frozen 40-case RED-first matrix across those six domains.

Primary donors: SLSA v1.1 threat model; Sigstore Rekor/security/sharding model; NIST SP 800-88 Rev. 2.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact local execution of the complete real-ledger closure.
- Direct shell transport cannot currently resolve `github.com`.
- Connector can read pinned source but this run has no supported non-model connector-to-local-filesystem materialization primitive.
- Complete real-schema LAB-086 tests, unsafe expected-failure seed, full compileall, security reconciliation and branch/main conflict audit remain pending.
- PR #165 is now 806 commits behind current main; do not infer merge safety from prior conflict observations.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093..100 design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against the pinned blob before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and current-main conflict audit. Fix every observed blocker before changing draft/merge status.

Do not manually copy connector payloads into the executor. If no supported materialization path exists, record the per-run observation and move directly to the next distinct evidence task: **canonical recovery after provenance-root equivocation + witness-identity reassignment authorization and tombstoning across overlapping membership epochs + proof-budget composition for approximate/certified unlearning chains + privacy namespace mapping-proof expiry/deletion without accounting loss + provider fork finality under provider failover/recovery + recursive authority-inventory completeness when discovery/attestation issuers cross-sign or share recovery roots**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + current-main conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; architecture additionally covers canonical provenance-root rollback/equivocation, witness collision/reassignment, typed unlearning-proof composition, privacy tombstone namespace rotation, provider fork finality/compact proofs and recursive authority-domain inventory assurance; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen; exact executable gates pending.
