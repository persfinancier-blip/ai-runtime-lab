# Current Lab State

Last updated: 2026-09-10

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; current connector read confirms `open`, `draft=true`, `mergeable=false`. Keep draft.
- Other open drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff, and `prompts/SELF_RESUME.md`; inspected open issues and PR #165; resumed LAB-086 first.

Current-run capability/state:
- Direct exact-source transport was re-probed with local `git clone --no-checkout` and failed before repository execution with `Could not resolve host: github.com`.
- GitHub connector reads/writes are available.
- No supported non-model connector-to-local-filesystem materialization primitive is exposed in this run. Manual/model reserialization of the security-critical LAB-086 closure remains prohibited by the retained byte-exact gate.
- Therefore no new LAB-086 behavioral, unsafe-seed, compileall, security-reconciliation, or conflict PASS is claimed; PR #165 remains draft.

Completed the recorded distinct fallback and froze `WITNESS_REOPEN_MUTATION_RETIREMENT_PRIVACY_ANTISYBIL_RETENTION_TIME_PQ_DNS_ROLLBACK_V1_FROZEN` in `research/2026-09-10-witness-reopen-mutation-retirement-privacy-antisybil-retention-time-pq-dns-rollback-v1.md`, main commit `4192b1e512007c07e811d234d3260ca48503cd4e`; #178 comment `5609492935` records the result.

Key decisions:
- `FINALIZED_GENERATION != HISTORY_CAN_NEVER_BE_REOPENED`: reopening is an authenticated successor lifecycle event; predecessor finalization evidence is preserved. Competing successor acknowledgements of incompatible predecessor heads are split-view, never last-writer-wins.
- `CORPUS_HASH_VALID != TEST_GENERATION_TRUSTWORTHY` and `OLD_CORPUS_PASS != CURRENT_COVERAGE_PASS`: corpus/oracle/mutation-operator/build provenance and a versioned semantic coverage floor are explicit security inputs; silent operator retirement is prohibited.
- `NEW_VERIFIER_ID != NEW_PRIVACY_BUDGET` and `BACKUP_RESTORE != PRIVACY_SPEND_ROLLBACK`: disclosure spend composes by protected subject/purpose/policy/window across verifier identities and survives credential rotation and storage restore; unknown global spend state blocks consequential disclosure.
- `LOCAL_TIME_AFTER_EXPIRY != DELETE_AUTHORIZED` and `TIME_ROLLBACK != POLICY_ROLLBACK`: destructive retention actions require acceptable authenticated freshness/time; policy conflicts use versioned deterministic precedence or an explicit unresolved state rather than invented legal conclusions.
- `ENDPOINT_REACHABLE != CURRENT_CRYPTO_FLOOR_SATISFIED` and `OLD_CONFIG_SIGNATURE_VALID != CURRENT_CONFIG_AUTHORIZED`: SVCB/ECH/DNS fallback, negative caching, retry, or intermediaries cannot silently strip required PQ/ECH capability or resurrect stale route/resumption authority.
- Frozen 40-case RED-first matrix across witness reopen/finalization, mutation provenance/retirement, privacy anti-sybil/restore, retention time/precedence, and PQ/ECH/DNS rollback/capability stripping.

Primary donors: RFC 9162; SLSA provenance/reproducibility guidance; NIST SP 800-226; NIST verified timestamping work; RFC 9460; RFC 9849.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact local execution of the complete real-ledger closure.
- Direct shell transport cannot currently resolve `github.com`.
- Connector can read exact pinned blobs but this run has no supported non-model connector-to-local-filesystem materialization primitive.
- Complete real-schema LAB-086 tests, unsafe expected-failure seed, full compileall, security reconciliation and branch/main conflict audit remain pending.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093..100 design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against the pinned blob before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

Do not manually copy connector payloads into the executor. If no supported materialization path exists, record the per-run observation and move directly to the next distinct evidence task: **witness reopen quorum key compromise and acknowledgement replay windows + semantic coverage claims under generated/adaptive mutation search + privacy-budget delegation/transfer and subject-merging/splitting attacks + retention time-source quorum/common-mode failure and leap/epoch handling + PQ/ECH/SVCB multi-resolver disagreement, DNSSEC key rollover and resumption after route-policy convergence**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; capability/evidence architecture now also covers witness reopen/split-view, mutation coverage retirement, privacy anti-sybil/ledger recovery, retention time rollback/precedence, and PQ/ECH/DNS rollback/capability stripping; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen; exact executable gates pending.
