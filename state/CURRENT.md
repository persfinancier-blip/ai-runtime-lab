# Current Lab State

Last updated: 2026-09-10

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; current inspection shows open/draft. Keep draft.
- Other open drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected current open issues and active PRs; resumed LAB-086 first and re-probed exact source materialization.

Current-run capability observation:
- Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository execution with `Could not resolve host: github.com`.
- GitHub connector reads/writes are available.
- No supported non-model connector-to-local-filesystem byte-exact materialization primitive is exposed in this run. Manual/model reserialization of the security-critical LAB-086 closure remains prohibited by the retained exact-byte gate.
- Therefore no new LAB-086 behavioral, unsafe-seed, compileall, security-reconciliation or conflict PASS is claimed; PR #165 remains draft.

Completed the recorded distinct fallback and froze `ATTESTATION_TRANSPARENCY_HOLDOUT_WITNESS_PRIVACY_POISONING_RETENTION_IDEMPOTENCY_TICKET_ERASURE_V1_FROZEN` in `research/2026-09-10-attestation-transparency-holdout-witness-privacy-poisoning-retention-idempotency-ticket-erasure-v1.md`, main commit `8f08ea3c7bcafefb721190e1367762f8d382e23f`; #178 comment `5619359174` records the result.

Key decisions:
- `ATTESTATION_SIGNATURE_VALID != DOMAIN_CLAIM_INDEPENDENT`: domain-attestation independence follows authenticated issuer/root/operator lineage; compromise-window uncertainty survives key/member replacement and successor-root admission must commit predecessor/compromise evidence.
- `COMPACT_ROOT_AUTHENTIC != DISCLOSURE_HISTORY_COMPLETE`: holdout provenance GC requires deterministic predecessor coverage plus independent witness quorum; witness loss carries the maximum surviving exposure floor plus `UNKNOWN`, never zero.
- `RESOLVER_SAYS_DISTINCT != PRIVACY_SUBJECTS_PROVEN_DISJOINT`: adversarial/faulty identity resolution cannot clone privacy budget; semantic subject overlap conservatively carries cumulative spend/reservation/unknown floors through resolver split/merge/recovery.
- `IDEMPOTENCY_TOKEN_EQUAL != LOGICAL_OPERATION_EQUAL`: destructive operation identity binds resource/action/parameters/policy/delegation/membership epoch; possible external effects remain `EFFECT_UNKNOWN` until reconciled or predecessor execution authority is fenced.
- `KEY_REMOVED_FROM_ACTIVE_KMS != KEY_UNRECOVERABLE`: ticket-key retirement covers active KMS/HSM, wrapped/backup/DR/external recovery domains and rollback-restored material; successor tickets/re-encryption cannot reset total ancestry lifetime or current admission floors.
- Frozen 40-case RED-first matrix across those five domains.

Primary donors: RFC 9162; NIST SP 800-226; NIST SP 800-88r2; RFC 9846; RFC 9325.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact local execution of the complete real-ledger closure.
- Direct shell transport cannot currently resolve `github.com`.
- Connector can read pinned source but this run has no supported non-model connector-to-local-filesystem materialization primitive.
- Complete real-schema LAB-086 tests, unsafe expected-failure seed, full compileall, security reconciliation and branch/main conflict audit remain pending.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093..100 design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against the pinned blob before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

Do not manually copy connector payloads into the executor. If no supported materialization path exists, record the per-run observation and move directly to the next distinct evidence task: **attestation transparency-log witness equivocation and recovery-root inclusion proofs + reusable-holdout witness compromise threshold changes + privacy resolver poisoning detection/dual-resolver reconciliation + retention external-system receipt authenticity and exactly-once impossibility boundaries + ticket ancestry cutoff after root CA/DC/PQ-policy emergency rotation and cross-region replay-state loss**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; architecture now additionally covers issuer-compromise transparency/revocation, holdout witness anti-rollback recovery, adversarial privacy identity-resolution poisoning, retention idempotency/external-effect ambiguity, and ticket-key erasure/KMS rollback/ancestry floors; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen; exact executable gates pending.
