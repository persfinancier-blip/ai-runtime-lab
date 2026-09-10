# Current Lab State

Last updated: 2026-09-10

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; current connector inspection still shows it open/draft. Keep draft.
- Other open drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected current open issues/PRs; resumed LAB-086 first and re-probed exact source materialization.

Current-run capability observation:
- Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository execution with `Could not resolve host: github.com`.
- GitHub connector reads/writes are available.
- No supported non-model connector-to-local-filesystem byte-exact materialization primitive is exposed in this run. Manual/model reserialization of the security-critical LAB-086 closure remains prohibited by the retained exact-byte gate.
- Therefore no new LAB-086 behavioral, unsafe-seed, compileall, security-reconciliation or conflict PASS is claimed; PR #165 remains draft.

Completed the recorded distinct fallback and froze `OBSERVER_CHURN_HOLDOUT_ROOT_PRIVACY_SCOPE_RETENTION_PROXY_PQ_TICKET_RETIREMENT_V1_FROZEN` in `research/2026-09-10-observer-churn-holdout-root-privacy-scope-retention-proxy-pq-ticket-retirement-v1.md`, main commit `19c03a15989d294c850bb8c603cdad6748ee43b4`; #178 comment `5617027095` records the result.

Key decisions:
- `NEW_MEMBER_IDS != NEW_FAILURE_DOMAINS` and `NEW_RECOVERY_EPOCH != INDEPENDENT_RECOVERY_AUTHORITY`: observer recovery admission tracks stable authority/failure-domain lineage across membership churn and compromise overlap, while emergency-member expiry removes only future voting authority and never erases already-observed evidence.
- `NEW_DATASET_HASH != NEW_INFORMATION`, `GENERATOR_VERSION_ROLLED_BACK != HOLDOUT_EXPOSURE_ROLLED_BACK`, and `PROVENANCE_ROOT_SIGNED != PROVENANCE_ROOT_CURRENT`: reusable-holdout decisions bind an attestable provenance DAG plus monotonic freshness, so dataset/generator/controller rollback or synthetic re-derivation cannot reset disclosure lineage.
- `SCOPE_SPLIT != BUDGET_MULTIPLICATION` and `SCOPE_MERGE != FLOOR_MINIMUM`: privacy scope split/merge must conserve remaining capacity, carry charged/unknown ancestry and conservatively compose predecessor floors; scope IDs, regrouping and witness rotation never launder cumulative privacy loss.
- `PROXY_FENCE_CURRENT != RESOURCE_FENCE_CURRENT` and `RETRY_AFTER_TIMEOUT != SAFE_TO_REAUTHORIZE`: destructive retention execution validates the complete policy->delegation->proxy-fence->resource-fence->operation chain at execution time; timeout after possible effect becomes `EFFECT_UNKNOWN` and reconciles before any successor destructive authority.
- `CERTIFICATE_REPLACED != OLD_TICKET_KEY_RETIRED`, `TICKET_REENCRYPTED != TICKET_REAUTHORIZED`, and `REGION_HAS_NEW_KEY != REGION_REJECTS_OLD_ANCESTRY`: TLS/PQ/ECH/DC identity recovery advances ticket-admission ancestry and explicitly retires/fences old ticket authority; re-encryption preserves ancestry, descendant tickets cannot refresh stale ancestry away, and late regions rejoin in resumption quarantine until current floors converge.
- Frozen 40-case RED-first matrix across those five domains.

Primary donors: RFC 9162; RFC 5011; Dwork et al. reusable holdout / adaptive data-analysis work; NIST SP 800-226; RFC 9345; RFC 8446.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact local execution of the complete real-ledger closure.
- Direct shell transport cannot currently resolve `github.com`.
- Connector can read pinned source but this run has no supported non-model connector-to-local-filesystem materialization primitive.
- Complete real-schema LAB-086 tests, unsafe expected-failure seed, full compileall, security reconciliation and branch/main conflict audit remain pending.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093..100 design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against the pinned blob before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

Do not manually copy connector payloads into the executor. If no supported materialization path exists, record the per-run observation and move directly to the next distinct evidence task: **authenticate failure-domain/authority-lineage claims used by observer recovery and handle attestation-root rollback + compact reusable-holdout provenance without losing disclosure ancestry/completeness + define privacy semantic-scope overlap/equivalence under ambiguous or changing subject sets without budget duplication + extend retention delegated fencing across multi-hop proxies/resource replicas and rollback of acknowledgement floors + define ticket-key retirement acknowledgement durability, descendant-ticket ancestry under regional partial rollback, and convergence proof after PQ/ECH/DC identity recovery**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; architecture now additionally covers observer recovery membership churn/compromise overlap, rollback-resistant holdout provenance roots, privacy scope split/merge without floor laundering, delegated resource/proxy destructive fencing, and ticket-key retirement/re-encryption after certificate/DC/PQ/ECH replacement; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen; exact executable gates pending.
