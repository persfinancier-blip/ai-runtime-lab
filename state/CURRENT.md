# Current Lab State

Last updated: 2026-09-10

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; current connector read confirms `open`, `draft=true`, `mergeable=false`. Keep draft.
- Other open drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff, `prompts/SELF_RESUME.md`; inspected open issues/PRs and PR #165; resumed LAB-086 first.

Current-run capability/state:
- Direct exact-source transport was re-probed with `git ls-remote https://github.com/persfinancier-blip/ai-runtime-lab.git HEAD` and failed before repository execution with `Could not resolve host: github.com`.
- GitHub connector reads/writes are available.
- No supported non-model connector-to-local-filesystem materialization primitive is exposed in this run. Manual/model reserialization of the security-critical LAB-086 closure remains prohibited by the retained byte-exact gate.
- Therefore no new LAB-086 behavioral, unsafe-seed, compileall, security-reconciliation, or conflict PASS is claimed; PR #165 remains draft.

Completed the recorded distinct fallback and froze `WITNESS_FINALIZATION_CORPUS_ORACLE_SCHEMA_BUDGET_RETENTION_FRESHNESS_PQ_DNS_V1_FROZEN` in `research/2026-09-10-witness-finalization-corpus-oracle-schema-budget-retention-freshness-pq-dns-v1.md`, main commit `39c1b69189e13fd9ec2f315f67bd30f536809c9d`; #178 comment `5608870828` records the result.

Key decisions:
- `RECOVERY_QUORUM_ACTIVATED != RECOVERY_HISTORY_FINALIZED`: activation and finalization are separate authenticated events; competing successor activations are split-view and cannot erase each other or degraded predecessor evidence.
- `CORPUS_REPRODUCES != SECURITY_SEMANTICS_COVERED`: verifier corpora bind generator/oracle provenance, semantic coverage and mutation operators; oracle compromise degrades historical verdict generation rather than rewriting it.
- `PER_VERIFIER_PRIVACY_BUDGET_OK != GLOBAL_DISCLOSURE_BUDGET_OK`: disclosure accounting composes across verifiers for a protected subject/window; exhausted budget returns insufficient disclosure, never fabricated independence.
- `VALID_HOLD_SIGNATURE != FRESH_HOLD_AUTHORITY`: retention hold/release/revocation/root rollover bind freshness and lineage; uncertain freshness blocks destructive deletion; offline-root recovery creates a successor generation without backdating conclusions.
- `DNS_ROUTE_AUTHENTICATED != TLS_RESUMPTION_AUTHORITY_CONTINUOUS` and `CLIENT_LACKS_PQ_CAPABILITY != AUTHORITY_TO_DOWNGRADE_SERVER_POLICY`: SVCB/ECH/DNS transitions and heterogeneous clients cannot silently reduce the current PQ/hybrid floor or transfer ticket/replay authority across endpoints.
- Frozen 40-case RED-first matrix across witness finalization, corpus/oracle recovery, schema privacy composition, retention freshness/offline root and PQ/ECH/SVCB DNS downgrade resistance.

Primary donors: RFC 9162; SLSA provenance/reproducibility guidance; NIST SP 800-53 AU family; RFC 9460; RFC 9848; RFC 9849.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact local execution of the complete real-ledger closure.
- Direct shell transport cannot currently resolve `github.com`.
- Connector can read exact pinned blobs but this run has no supported non-model connector-to-local-filesystem materialization primitive.
- Complete real-schema LAB-086 tests, unsafe expected-failure seed, full compileall, security reconciliation and branch/main conflict audit remain pending.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093..100 design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against the pinned blob before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

Do not manually copy connector payloads into the executor. If no supported materialization path exists, record the per-run observation and move directly to the next distinct evidence task: **witness finalization rollback/reopen and cross-generation acknowledgement equivocation + corpus mutation-operator provenance/coverage-floor retirement + privacy-budget anti-sybil verifier identity and budget-ledger recovery + retention clock-source compromise/time rollback and cross-policy precedence + PQ/ECH authenticated DNS transition rollback, stale negative caching and capability-stripping intermediaries**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; capability/evidence architecture now also covers recovery finalization split-view, verifier corpus/oracle recovery, global disclosure-budget composition, retention freshness/offline-root recovery and PQ/ECH/SVCB DNS downgrade resistance; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen; exact executable gates pending.
