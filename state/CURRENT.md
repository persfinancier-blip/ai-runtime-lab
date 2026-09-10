# Current Lab State

Last updated: 2026-09-10

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; current connector read confirms `open`, `draft=true`, `mergeable=false`. Keep draft.
- Other open drafts remain LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues, open PRs and repository branches; resumed LAB-086 first.

Current-run capability observation:
- Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository execution with `Could not resolve host: github.com`.
- GitHub connector reads/writes are available.
- No supported non-model connector-to-local-filesystem materialization primitive is exposed in this run. Manual/model reserialization of the security-critical LAB-086 closure remains prohibited by the retained byte-exact gate.
- Therefore no new LAB-086 behavioral, unsafe-seed, compileall, security-reconciliation or conflict PASS is claimed; PR #165 remains draft.

Completed the recorded distinct fallback and froze `OBSERVER_ECLIPSE_REUSABLE_HOLDOUT_PRIVACY_ROOT_RECOVERY_RETENTION_DELEGATION_PQ_CROSS_SNI_V1_FROZEN` in `research/2026-09-10-observer-eclipse-reusable-holdout-privacy-root-recovery-retention-delegation-pq-cross-sni-v1.md`, main commit `72d7cab337cc2622b40bd09d180188c4dd325e76`; #178 comment `5614068220` records the result.

Key decisions:
- `ENOUGH_SIGNATURES_ON_ONE_VIEW != SUFFICIENT_OBSERVER_COVERAGE`: authenticated observer-set epochs bind identities, independent failure domains, admissions/removals and cutoff. Missing required domains produce `OBSERVER_COVERAGE_INCOMPLETE`; late authenticated conflicts append evidence and can reopen finality.
- `HOLDOUT_QUERY_LIMIT_NOT_EXCEEDED != HOLDOUT_REMAINS_INDEPENDENT`: every confirmation exposure is accounted by generation/candidate family/statistic/analyst state. Outcome-driven ranking/mutation/pruning burns ordinary holdout independence; fresh post-selection confirmation remains default unless a justified reusable-validation mechanism exists.
- `NEW_RECONCILIATION_ROOT_VALID != OLD_SPEND_HISTORY_REAUTHORIZED`: privacy root recovery carries forward the last monotonic spend floor, unresolved reservations/transfers and fenced authorities. Old signed roots remain evidence but lose current authority; rollback cannot mint budget.
- `PRINCIPAL_NOT_LISTED_AS_WRITER != PRINCIPAL_LACKS_DESTRUCTIVE_AUTHORITY`: retention writer inventory is the authenticated transitive closure of direct, delegated/subdelegated, break-glass, queued/offline and DR destructive capabilities for each membership epoch.
- `CROSS_SNI_CERT_COVERAGE != CROSS_SNI_RESUMPTION_AUTHORITY`: ticket descendants retain certificate/delegated-credential, PQ/hybrid, ECH-source, backend/route, ticket-key, revocation and replay ancestry. Cross-SNI resumption needs explicit current service-equivalence policy; stale regional issuers remain fenced.
- Frozen 40-case RED-first matrix across observer eclipse resistance, reusable holdout accounting, privacy root recovery, retention delegation closure and PQ/ECH cross-SNI ancestry.

Primary donors: RFC 9162; Generic Holdout (arXiv:1809.05596); TUF rollback/root-rotation semantics; RFC 9345; RFC 8446/RFC 9846.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact local execution of the complete real-ledger closure.
- Direct shell transport cannot currently resolve `github.com`.
- Connector can read exact pinned blobs but this run has no supported non-model connector-to-local-filesystem materialization primitive.
- Complete real-schema LAB-086 tests, unsafe expected-failure seed, full compileall, security reconciliation and branch/main conflict audit remain pending.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093..100 design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against the pinned blob before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

Do not manually copy connector payloads into the executor. If no supported materialization path exists, record the per-run observation and move directly to the next distinct evidence task: **observer-set compromise/recovery and minimum-independent-domain threshold evolution + reusable-holdout mechanism selection/accounting under repeated candidate families + privacy successor-root quorum compromise/dual-control recovery + retention capability revocation propagation and offline-job fencing + PQ/ECH cross-SNI resumption after delegated-credential compromise, parent-certificate reissue and service-equivalence-policy rollover**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; architecture now also covers authenticated observer admission/removal with eclipse-resistant failure-domain thresholds, reusable-holdout exposure accounting, compromise-safe privacy reconciliation-root succession, transitive retention writer-capability closure, and PQ/ECH cross-SNI ticket ancestry; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen; exact executable gates pending.
