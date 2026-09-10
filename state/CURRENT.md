# Current Lab State

Last updated: 2026-09-10

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; current connector reads confirm open/draft. Keep draft.
- Other open drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff, and `prompts/SELF_RESUME.md`; inspected open issues/PRs/branches; resumed LAB-086 first.

Current-run capability observation:
- Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository execution with `Could not resolve host: github.com`.
- GitHub connector reads/writes are available.
- No supported non-model connector-to-local-filesystem materialization primitive is exposed in this run. Manual/model reserialization of the security-critical LAB-086 closure remains prohibited by the retained byte-exact gate.
- Therefore no new LAB-086 behavioral, unsafe-seed, compileall, security-reconciliation, or conflict PASS is claimed; PR #165 remains draft.

Completed the recorded distinct fallback and froze `WITNESS_NONCE_RECOVERY_ADAPTIVE_ORACLE_PRIVACY_REVOCATION_TIME_MEMBERSHIP_PQ_TICKET_EVICTION_V1_FROZEN` in `research/2026-09-10-witness-nonce-recovery-adaptive-oracle-privacy-revocation-time-membership-pq-ticket-eviction-v1.md`, main commit `270214f636f3542e4f69ec50d54efa43ea8ab7c8`; #178 comment `5610654368` records the result.

Key decisions:
- `NONCE_ABSENT_LOCALLY != ACKNOWLEDGEMENT_FRESH`: witness acknowledgement nonce/spend state is authority state and must remain monotonic across snapshot rollback, GC, failover and rebuild. A successor key/quorum requires an authenticated recovery bridge and cannot retroactively repair predecessor assurance after compromise.
- `ADAPTIVE_SEARCH_SCORE_HIGH != SECURITY_COVERAGE_HIGH`: authenticated test evidence separates corpus root, mutation operators, adaptive search algorithm, search budget/stopping rule, reward features, oracle/generator/build provenance, metamorphic relations, differential peers and semantic coverage floor. Common pipeline failures do not count as independent oracle evidence.
- `DELEGATION_REVOKED != IN_FLIGHT_SPEND_ERASED`: privacy-budget delegation uses durable reserve/commit/reconcile semantics. Revocation, credential rotation, subject split/merge, purpose relabeling and restore cannot manufacture new global disclosure budget.
- `CLOCK_STILL_TICKS != TIME_AUTHORITY_STILL_CURRENT`: retention time quorum binds membership epoch, source/key generation, uncertainty, holdover state and transitive failure domains. Cross-epoch vote mixing and destructive actions beyond holdover uncertainty fail closed.
- `ROUTE_CONVERGED != OLD_TICKET_REAUTHORIZED`: DNSSEC/SVCB/ECH recovery does not automatically revive TLS/PQ resumption authority minted under an incompatible route, backend, ALPN, ECH config, PQ/hybrid policy or replay-authority generation. Ticket invalidation must cover edge/mesh/DR authorities.
- Frozen 40-case RED-first matrix across nonce rollback/GC and compromised-key bridges, adaptive oracle collusion/metamorphic checks, privacy delegation revocation races, retention time membership/holdover, and PQ/ECH/SVCB ticket eviction.

Primary donors: RFC 9162; RFC 5011; RFC 6781; RFC 9846; SLSA reproducibility guidance; NIST SP 800-226.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact local execution of the complete real-ledger closure.
- Direct shell transport cannot currently resolve `github.com`.
- Connector can read exact pinned blobs but this run has no supported non-model connector-to-local-filesystem materialization primitive.
- Complete real-schema LAB-086 tests, unsafe expected-failure seed, full compileall, security reconciliation and branch/main conflict audit remain pending.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093..100 design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against the pinned blob before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

Do not manually copy connector payloads into the executor. If no supported materialization path exists, record the per-run observation and move directly to the next distinct evidence task: **nonce checkpoint/compaction anti-entropy and recovery from stale replica promotion + adaptive oracle state poisoning/corpus minimization and failure-preserving reduction + privacy reservation idempotency/double-commit and compensating-disclosure semantics + retention membership-epoch rollback and monotonic recovery counters + PQ/ECH ticket-key compromise, generation revocation propagation and 0-RTT disablement through multi-region recovery**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; capability/evidence architecture now also covers nonce rollback/GC and compromised-key recovery bridges, adaptive oracle independence, privacy delegation revocation races, retention time membership/holdover, and PQ/ECH/SVCB ticket-generation eviction; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen; exact executable gates pending.
