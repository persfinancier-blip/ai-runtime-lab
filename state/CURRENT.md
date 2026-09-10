# Current Lab State

Last updated: 2026-09-10

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and conflict audit passes.

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

Completed the recorded distinct fallback and froze `PROVENANCE_POISONING_WITNESS_CANONICALIZATION_UNLEARNING_PRIVACY_TOMBSTONE_RECEIPT_FORK_KMS_ENUMERATION_V1_FROZEN` in `research/2026-09-10-provenance-poisoning-witness-canonicalization-unlearning-lineage-privacy-tombstones-receipt-forks-kms-enumeration-v1.md`, main commit `8a14c6a2fb7bc251545e814bb2e07eb011d3b578`; #178 comment `5624887659` records the result.

Key decisions:
- `SIGNED_ASSESSMENT != TRUSTWORTHY_ASSESSMENT_PROVENANCE`: compromise/recovery assessments authenticate their evidence inputs, collector, policy/engine version, issuer/key epoch, independence claims and event cutoff; re-signing poisoned evidence under a successor key does not cleanse it.
- `N_VALID_SIGNATURES != N_INDEPENDENT_WITNESSES`: cross-signed overlapping keys are canonicalized to stable witness/failure-domain identity before quorum counting; circular successor cross-signing cannot bootstrap authority from zero.
- `COMPONENT_DELETED != HOLDOUT_INFLUENCE_PROVEN_ABSENT`: machine unlearning, component deletion, adapter removal, cache rebuild or ensemble surgery preserves predecessor holdout lineage unless a sound deletion proof establishes unreachable influence; empirical MIA success alone is not enough.
- `SAME_TOMBSTONE != SAME_SUBJECT`: privacy tombstone collision/false-relink handling isolates identity data but never mints privacy-budget credit; split/merge oscillation keeps cumulative spend floors monotonic.
- `VALID_RECEIPT != SINGLE_CANONICAL_EFFECT_HISTORY`: same-predecessor signed receipt forks are explicit provider equivocation/fork state; sequence-gap compaction preserves unresolved gaps; idempotency-key reuse with a different semantic payload is a conflict.
- `ALL_KNOWN_DOMAINS_ACKED != ALL_AUTHORITY_DOMAINS_ENUMERATED`: ticket-security-epoch GC requires authenticated enumeration provenance across KMS/HSM/backup/DR/escrow/offline recovery/replica/replay-state authority classes; late discovery re-quarantines affected resumption without lowering the epoch floor.
- Frozen 40-case RED-first matrix across those six domains.

Primary donors: SLSA v1.1 threat model; Sigstore threat/security model and Rekor monitoring model; RFC 9162; TUF root/threshold metadata; Pawelczyk et al. 2024, Chourasia & Shah 2022, Cohen et al. 2026 machine-unlearning work; NIST SP 800-226; HTTPAPI Idempotency-Key draft; NIST SP 800-88 Rev. 2.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact local execution of the complete real-ledger closure.
- Direct shell transport cannot currently resolve `github.com`.
- Connector can read pinned source but this run has no supported non-model connector-to-local-filesystem materialization primitive.
- Complete real-schema LAB-086 tests, unsafe expected-failure seed, full compileall, security reconciliation and branch/main conflict audit remain pending.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093..100 design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against the pinned blob before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

Do not manually copy connector payloads into the executor. If no supported materialization path exists, record the per-run observation and move directly to the next distinct evidence task: **provenance-root rollback/split-view for assessment evidence + witness canonical-identity collision/reassignment across membership epochs + exact-vs-approximate unlearning attestation composition through ensembles/distillation + privacy tombstone namespace rotation/collision recovery + provider fork-choice/finality and compact receipt proofs + authority-domain inventory issuer compromise/partial discovery and recursive recovery-authority enumeration before ticket-epoch GC**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; architecture additionally covers poisoned assessment provenance, cross-signed witness canonicalization, machine-unlearning holdout lineage, privacy tombstone collision/relink isolation, provider receipt forks/gap compaction, and complete authority-domain enumeration for ticket GC; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen; exact executable gates pending.
