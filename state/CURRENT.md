# Current Lab State

Last updated: 2026-09-11

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and current-main conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`. Keep draft.
- Other open drafts inspected: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues and active PRs; resumed LAB-086 first and re-probed exact source materialization.

Current-run capability observation:
- Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository execution with `Could not resolve host: github.com`.
- GitHub connector reads/writes are available.
- No supported non-model connector-to-local-filesystem byte-exact materialization primitive is exposed in this run. Manual/model reserialization of the security-critical LAB-086 closure remains prohibited by the retained exact-byte gate.
- Therefore no new LAB-086 behavioral, unsafe-seed, compileall, security-reconciliation or conflict PASS is claimed; PR #165 remains draft.
- Fresh compare: PR #165 branch vs current `main` is `diverged`, ahead 195 / behind 817. Historical conflict conclusions are not sufficient for merge safety.

Completed the recorded distinct fallback and froze `RECOVERY_COMPROMISE_RETENTION_UNLEARNING_GC_PRIVACY_DEJOIN_FINALITY_RETROCOMPROMISE_LINEARIZABLE_GC_V1_FROZEN` in `research/2026-09-11-recovery-compromise-retention-unlearning-gc-privacy-dejoin-finality-retrocompromise-linearizable-gc-v1.md`, main commit `dc404a2b1ab6c9379008d2965891e9635bf36b92`; #178 comment `5628927586` records the result.

Key decisions:
- If a fork-resolving recovery generation is later partially compromised, evaluate compromise against the signing interval and canonical failure domains. If surviving admissible domains no longer meet threshold/intersection, that generation becomes `RECOVERY_AUTHORITY_UNCERTAIN`; rollback/equivocation floors remain monotonic and only a strictly higher independently sufficient generation may recover continuity.
- Joint membership/checkpoint retention obligations retire only through an authenticated retirement record binding bridge, retention floor, verifier profile/version, and monotonic expiry/retirement evidence. Wall-clock expiry alone cannot authorize predecessor-evidence GC.
- Revoked/superseded unlearning proofs may be compacted only if an authenticated tombstone/commitment preserves theorem/profile root, supersession/revocation path, re-proof/re-anchor provenance, guarantee class and deleted-data lineage. Re-signing is not re-proof.
- Privacy resolver de-join after source-log recovery may release only proven-unused reservations/unknown-loss margins. Consumed cumulative privacy loss is never refunded; unresolved attribution retains the conservative accounting upper bound.
- Retroactive compromise of a provider-finality authority changes confidence in receipts/attestations, not the external side effect itself. Affected destructive effects revert to `EFFECT_UNKNOWN` absent independent reconciliation; successor activation cannot manufacture predecessor finality.
- Destructive `CAN_RESTORE` GC is a linearizable protocol bound to an authenticated immutable graph snapshot + GC epoch. Authority-inventory mutations serialize with GC admission; mutation discovered after proof evaluation belongs to a higher epoch and cannot silently validate the stale proof.
- Frozen 40-case RED-first matrix with explicit negative seeds for recovery-quorum collapse, unauthenticated retention expiry, unlearning-provenance GC loss, privacy-spend refund, blind retry after finality retro-compromise, and inventory-edge insertion racing GC.

Primary donors: TUF sequential predecessor/successor root continuity and rollback defense; RFC 9162 append-only consistency proofs; theorem/assumption-scoped certified machine-unlearning guarantees; NIST SP 800-226 cumulative privacy-budget composition; NIST SP 800-88 Rev. 2 cryptographic-erasure/key-copy assurance.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact local execution of the complete real-ledger closure.
- Direct shell transport cannot currently resolve `github.com`.
- Connector can read pinned source but this run has no supported non-model connector-to-local-filesystem materialization primitive.
- Complete real-schema LAB-086 tests, unsafe expected-failure seed, full compileall, security reconciliation and current-main conflict audit remain pending.
- PR #165 is now at least 817 commits behind current main; do not infer merge safety from historical conflict observations.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093..100 design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against the pinned blob before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and a fresh current-main conflict audit. Fix every observed blocker before changing draft/merge status.

Do not manually copy connector payloads into the executor. If no supported materialization path exists, record the per-run observation and move directly to the next distinct evidence task: **post-resolution compromise-evidence rollback/cutoff poisoning + compact checkpoint/tombstone continuity across verifier-profile retirement + unlearning re-proof GC when multiple current certificates share a revoked ancestor + reservation-release races with new privacy analyses during resolver de-join + finality-revalidation cache invalidation after retroactive authority compromise + crash-consistent/distributed GC barriers when authority-inventory replicas disagree on the graph epoch**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + current-main conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; architecture now additionally covers recovery-authority retro-compromise, authenticated stale-verifier retirement, provenance-preserving unlearning-proof GC, privacy de-join without spend refund, provider-finality retro-compromise, and linearizable `CAN_RESTORE` GC epochs; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen; exact executable gates pending.
