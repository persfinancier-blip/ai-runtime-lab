# Current Lab State

Last updated: 2026-09-10

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; current inspection confirms `open`, `draft=true`. Keep draft.
- Other open drafts remain LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues/open PRs; resumed LAB-086 first and re-probed exact source materialization.

Current-run capability observation:
- Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository execution with `Could not resolve host: github.com`.
- GitHub connector reads/writes are available.
- No supported non-model connector-to-local-filesystem byte-exact materialization primitive is exposed in this run. Manual/model reserialization of the security-critical LAB-086 closure remains prohibited by the retained exact-byte gate.
- Therefore no new LAB-086 behavioral, unsafe-seed, compileall, security-reconciliation or conflict PASS is claimed; PR #165 remains draft.

Completed the recorded distinct fallback and froze `DELAYED_COMPROMISE_HOLDOUT_DISTILLATION_PRIVACY_RELINK_RECEIPT_REVOCATION_TICKET_ESCROW_V1_FROZEN` in `research/2026-09-10-delayed-compromise-holdout-distillation-privacy-relink-receipt-revocation-ticket-escrow-v1.md`, main commit `3f36c79bcf32ecf18e51a6a48b78b3f78f62587a`; #178 comment `5623346741` records the result.

Key decisions:
- `SUCCESSOR_QUORUM_VALID_AT_T0 != SUCCESSOR_AUTHORITY_SAFE_AFTER_DELAYED_COMPROMISE_DISCOVERY`: a later-proven predecessor compromise whose interval intersects transition authorization forces historical quorum re-evaluation against stable failure-domain lineage; insufficient remaining authority becomes `DELAYED_AUTHORIZATION_UNCERTAIN`.
- `WITNESS_ATTESTATION_EXPIRED != HISTORICAL_EVIDENCE_INVALID`: compact-root GC retains witness stable identity, key epoch, validity/revocation interval, quorum/conflict set and enough completeness evidence to reconstruct authority after online witness rotation/expiry.
- `LOSSY_TRANSFORM != INFORMATION_INDEPENDENCE`: distillation, quantization/compression, embeddings, statistics, cached scores, ANN indexes/sketches and synthetic data selected through holdout feedback inherit exposure lineage while useful information remains reachable by the adaptive controller.
- `IDENTITY_TOMBSTONED != PRIVACY_LINEAGE_ERASED`: deletion may remove profile data but not the monotonic accounting lineage needed to prevent budget reset; later relink conservatively composes predecessor spend/unknown-loss floors.
- `RECEIPT_SIGNATURE_VALID != RECEIPT_AUTHORITY_VALID_FOR_EVENT_TIME`: receipt revocation/compromise is interval-aware; delayed receipts reconcile by authenticated provider sequence/effect ancestry, not arrival order; incompatible receipts create provider equivocation.
- `LOCAL_KMS_KEY_ABSENT != TICKET_PREDECESSOR_AUTHORITY_EXTINCT`: ticket GC covers external KMS replicas/imports, wrapped copies, backup/DR and credential escrow; late authority discovery reopens extinction proof without lowering the ticket-security-epoch floor and quarantines the affected resumption domain.
- Frozen 40-case RED-first matrix across those six domains.

Primary donors: RFC 9162; Dwork et al. 2015 adaptive holdout reuse; Jagielski et al. 2023 model-distillation membership inference; embedding-inversion research; NIST SP 800-226; TLS 1.3/RFC 9846; NIST SP 800-88 Rev. 2.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact local execution of the complete real-ledger closure.
- Direct shell transport cannot currently resolve `github.com`.
- Connector can read pinned source but this run has no supported non-model connector-to-local-filesystem materialization primitive.
- Complete real-schema LAB-086 tests, unsafe expected-failure seed, full compileall, security reconciliation and branch/main conflict audit remain pending.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093..100 design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against the pinned blob before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

Do not manually copy connector payloads into the executor. If no supported materialization path exists, record the per-run observation and move directly to the next distinct evidence task: **recovery-transition authority after compromise evidence itself is later revoked/overturned + compact-root anti-rollback when witness validity intervals overlap ambiguously + holdout lineage through ensemble aggregation/model merging and retrieval-cache regeneration + privacy-accounting lineage across irreversible identifier redaction with probabilistic relink + provider receipt canonicalization under clock skew/sequence gaps and key-recovery compromise + ticket-security-epoch convergence when escrow/KMS authority is federated across independently administered regions**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; architecture now additionally covers delayed predecessor compromise, witness-key rotation/expiry reconstruction, holdout derivative lineage through distillation/embeddings/ANN, privacy tombstone→relink monotonic accounting, receipt compromise/revocation with delayed ordering, and external-KMS/escrow ticket-authority discovery; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen; exact executable gates pending.
