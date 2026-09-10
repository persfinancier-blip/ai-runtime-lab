# Current Lab State

Last updated: 2026-09-10

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; current inspection shows `open`, `draft=true`, `mergeable=false`. Keep draft.
- Other open drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected current open issues and active PRs; resumed LAB-086 first and re-probed exact source materialization.

Current-run capability observation:
- Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository execution with `Could not resolve host: github.com`.
- GitHub connector reads/writes are available.
- No supported non-model connector-to-local-filesystem byte-exact materialization primitive is exposed in this run. Manual/model reserialization of the security-critical LAB-086 closure remains prohibited by the retained exact-byte gate.
- Therefore no new LAB-086 behavioral, unsafe-seed, compileall, security-reconciliation or conflict PASS is claimed; PR #165 remains draft.

Completed the recorded distinct fallback and froze `OBSERVER_ISSUER_LINEAGE_HOLDOUT_GC_PRIVACY_IDENTITY_RETENTION_PARTIAL_EFFECT_TICKET_CHURN_V1_FROZEN` in `research/2026-09-10-observer-issuer-lineage-holdout-gc-privacy-identity-retention-partial-effect-ticket-churn-v1.md`, main commit `54a62f5d223ab86d765f4898b533790eb231499d`; #178 comment `5618599378` records the result.

Key decisions:
- `ATTESTATION_CROSS_SIGNED != FAILURE_DOMAIN_INDEPENDENT`: cross-signatures from overlapping issuer/root/operator lineages do not manufacture independent quorum domains; lineage merges/recovery carry unresolved predecessor compromise evidence.
- `COMPACT_ROOT_AUTHENTIC != COMPACT_ROOT_COMPLETE`: holdout provenance GC requires an authenticated deterministic coverage proof over the predecessor event range/DAG; missing restored provenance stays `PROVENANCE_INCOMPLETE`, never zero exposure.
- `IDENTITY_MATCH_PROBABILITY_BELOW_ONE != SUBJECTS_DISJOINT`: probabilistic identity uncertainty does not create independent privacy capacity; possible overlap and subject migration conservatively carry cumulative spend/reservation/unknown floors.
- `SOME_REPLICAS_ACKED != GLOBAL_EFFECT_COMPLETE`: partial destructive success remains one unresolved logical operation until every predecessor executor is reconciled or fenced; membership removal does not erase possible predecessor effects.
- `CURRENT_REGION_QUORUM_ACKED != ALL_PREDECESSOR_TICKET_SPEND_AUTHORITY_RETIRED`: ticket retirement spans predecessor spend authorities across region churn; old-key erasure evidence includes backup/DR/HSM/external recovery domains; re-encryption or successor tickets cannot reset bounded total ancestry lifetime.
- Frozen 40-case RED-first matrix across those five domains.

Primary donors: RFC 9162; Generic/Reusable Holdout work; NIST SP 800-226; RFC 8446; RFC 9345; RFC 9325; NIST SP 800-88r2.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact local execution of the complete real-ledger closure.
- Direct shell transport cannot currently resolve `github.com`.
- Connector can read pinned source but this run has no supported non-model connector-to-local-filesystem materialization primitive.
- Complete real-schema LAB-086 tests, unsafe expected-failure seed, full compileall, security reconciliation and branch/main conflict audit remain pending.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093..100 design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against the pinned blob before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

Do not manually copy connector payloads into the executor. If no supported materialization path exists, record the per-run observation and move directly to the next distinct evidence task: **transparency/revocation for domain-attestation issuer compromise windows and successor-root admission + holdout compact-root witness quorum/anti-rollback recovery after partial witness loss + privacy identity-resolver poisoning/adversarial linkage and irreversible spend-floor reconciliation + retention idempotency-token collision/external side-effect reconciliation across membership epochs + ticket-key erasure attestation rollback/KMS restore and ancestry-floor enforcement after disaster recovery**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; architecture now additionally covers issuer-lineage compromise/cross-signing, compact-root completeness/GC recovery, probabilistic privacy identity overlap, multi-replica partial-effect anti-replay, and ticket-retirement churn/erasure/ancestry bounds; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen; exact executable gates pending.
