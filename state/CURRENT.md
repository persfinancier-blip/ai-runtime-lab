# Current Lab State

Last updated: 2026-09-10

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; inspected this run and still open/draft. Keep draft.
- Other open drafts remain LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues and active PRs; resumed LAB-086 first and re-probed exact source materialization.

Current-run capability observation:
- Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository execution with `Could not resolve host: github.com`.
- GitHub connector reads/writes are available.
- No supported non-model connector-to-local-filesystem byte-exact materialization primitive is exposed in this run. Manual/model reserialization of the security-critical LAB-086 closure remains prohibited by the retained exact-byte gate.
- Therefore no new LAB-086 behavioral, unsafe-seed, compileall, security-reconciliation or conflict PASS is claimed; PR #165 remains draft.

Completed the recorded distinct fallback and froze `OVERTURNED_COMPROMISE_WITNESS_INTERVAL_ENSEMBLE_PRIVACY_RELINK_RECEIPT_SEQUENCE_TICKET_FEDERATION_V1_FROZEN` in `research/2026-09-10-overturned-compromise-witness-interval-ensemble-lineage-privacy-relink-receipt-sequence-ticket-federation-v1.md`, main commit `7b0aef304bf0b923c42f1b2f040e13a8e68bb132`; #178 comment `5624144667` records the result.

Key decisions:
- `COMPROMISE_EVIDENCE_REVOKED != PREVIOUS_AUTHORIZATION_AUTOMATICALLY_VALID`: compromise assessments are versioned evidence; overturning permits a new recovery evaluation but never rewrites prior authorization or lowers a monotonic uncertainty floor.
- `SIGNATURE_VERIFIES_NOW != WITNESS_AUTHORIZED_AT_EVENT_CUTOFF`: witness authority is interval/membership-epoch aware; overlapping key epochs for one stable witness count once; ambiguous event-time authority fails closed.
- `MULTIPLE_MODELS != MULTIPLE_INDEPENDENT_HOLDOUTS`: ensembles, model merging, adapters, distillation and regenerated retrieval caches union reachable holdout-exposure lineage.
- `IDENTIFIER_REDACTED != ACCOUNTING_SUBJECT_FORGOTTEN`: irreversible identifier redaction retains non-reconstructive accounting tombstones; probabilistic relink cannot mint budget credit and graph oscillation never decreases spend floors.
- `ARRIVAL_ORDER != EFFECT_ORDER`, `SIGNED_TIMESTAMP != TRUSTED_EFFECT_TIME`, `SEQUENCE_GAP != SAFE_TO_INFER_NO_EFFECT`: external receipts reconcile by authenticated provider sequence/effect ancestry; gaps block blind retry; recovered old receipt keys do not regain current authority.
- `REGIONAL_EPOCH_ACK != GLOBAL_PREDECESSOR_AUTHORITY_EXTINCT`: federated KMS/HSM/backup/DR/escrow authority must converge before ticket-epoch retirement; late predecessor-authority discovery re-quarantines affected resumption without lowering the global epoch floor; lost replay state separately blocks 0-RTT.
- Frozen 40-case RED-first matrix across those six domains.

Primary donors: RFC 9162; NIST SP 800-57; withdrawn SP 800-102 used only as a narrow historical donor for trusted-time reasoning; Jagielski et al. 2023 distillation membership inference; NIST SP 800-226; RFC 8446/RFC 9846 TLS 1.3; RFC 9813 resumption authorization-context fallback.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact local execution of the complete real-ledger closure.
- Direct shell transport cannot currently resolve `github.com`.
- Connector can read pinned source but this run has no supported non-model connector-to-local-filesystem materialization primitive.
- Complete real-schema LAB-086 tests, unsafe expected-failure seed, full compileall, security reconciliation and branch/main conflict audit remain pending.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093..100 design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against the pinned blob before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

Do not manually copy connector payloads into the executor. If no supported materialization path exists, record the per-run observation and move directly to the next distinct evidence task: **assessment-provenance poisoning and issuer compromise for overturned recovery evidence + witness membership/validity proof canonicalization across cross-signed overlapping intervals + holdout lineage under machine unlearning/component deletion from ensembles + privacy tombstone collision/false-relink isolation without budget laundering + provider receipt sequence forks/gap compaction/recovery-key rollback + federated KMS/escrow membership churn and proof of complete authority-domain enumeration before ticket-epoch GC**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; architecture additionally covers overturned compromise assessments, interval-aware witness authority, ensemble/model-merge holdout lineage, identifier-redaction/probabilistic-relink accounting, sequence-aware external receipts, and federated ticket-authority convergence; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen; exact executable gates pending.
