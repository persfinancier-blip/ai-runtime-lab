# Current Lab State

Last updated: 2026-09-10

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; current connector reads confirm open/draft. Keep draft.
- Other open drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff, and `prompts/SELF_RESUME.md`; inspected open issues/PRs; resumed LAB-086 first.

Current-run capability observation:
- Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository execution with `Could not resolve host: github.com`.
- GitHub connector reads/writes are available.
- No supported non-model connector-to-local-filesystem materialization primitive is exposed in this run. Manual/model reserialization of the security-critical LAB-086 closure remains prohibited by the retained byte-exact gate.
- Therefore no new LAB-086 behavioral, unsafe-seed, compileall, security-reconciliation, or conflict PASS is claimed; PR #165 remains draft.

Completed the recorded distinct fallback and froze `NONCE_ANTI_ENTROPY_ORACLE_REDUCTION_PRIVACY_IDEMPOTENCY_RETENTION_EPOCH_PQ_REVOCATION_V1_FROZEN` in `research/2026-09-10-nonce-anti-entropy-oracle-reduction-privacy-idempotency-retention-epoch-pq-revocation-v1.md`, main commit `8eb966347ae179c9adc27e11c07af3d6d69320a0`; #178 comment `5611222639` records the result.

Key decisions:
- `NONCE_NOT_IN_LOCAL_LOG != NONCE_UNSPENT`: compacted/restored/stale replicas must consult an authenticated monotonic spend-checkpoint lineage. Raw nonce GC is allowed only after successor checkpoint coverage; stale promotion fails closed until anti-entropy reaches the accepted floor.
- `MINIMIZED_FAILURE_REPRODUCES != MINIMIZED_FAILURE_PRESERVES_SECURITY_CAUSE`: corpus reducers must preserve the exact violated security predicate. Adaptive search cannot rewrite frozen oracle truth, and correlated oracle/build/parser failure domains do not count as independent evidence.
- `RESERVATION_RETRY != NEW_PRIVACY_BUDGET`: privacy reserve/commit is globally idempotent by protected subject/purpose/request lineage. Ambiguous egress remains charged/unknown until reconciliation; corrective disclosure cannot erase prior privacy loss.
- `VALID_OLD_TIME_ATTESTATION != CURRENT_RETENTION_AUTHORITY`: retention authorization binds membership epoch, key/policy generation, uncertainty/holdover and a monotonic recovery counter. Snapshot/membership rollback cannot roll destructive authority backward.
- `TICKET_KEY_ROTATED != OLD_TICKETS_REVOKED_GLOBALLY`: PQ/ECH resumption compromise recovery requires revocation-generation propagation to every decrypt/spend authority. Regions missing the current revocation/replay floor reject affected 0-RTT; restart/DR replay gaps fail closed.
- Frozen 40-case RED-first matrix across nonce anti-entropy, oracle poisoning/reduction, privacy idempotency, retention epoch rollback, and multi-region ticket revocation.

Primary donors: etcd disaster-recovery revision bump/mark-compacted semantics; RFC 5011; RFC 9846; RFC 9849; SLSA provenance/reproducibility guidance; NIST SP 800-226.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact local execution of the complete real-ledger closure.
- Direct shell transport cannot currently resolve `github.com`.
- Connector can read exact pinned blobs but this run has no supported non-model connector-to-local-filesystem materialization primitive.
- Complete real-schema LAB-086 tests, unsafe expected-failure seed, full compileall, security reconciliation and branch/main conflict audit remain pending.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093..100 design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against the pinned blob before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

Do not manually copy connector payloads into the executor. If no supported materialization path exists, record the per-run observation and move directly to the next distinct evidence task: **checkpoint quorum/anti-entropy equivocation and compaction-proof survivability + reducer nondeterminism and predicate-preserving delta debugging + privacy reservation reconciliation after cross-region partition + retention recovery-counter witness compromise/rekey + PQ/ECH revocation-floor acknowledgement, ticket-key erasure proof and 0-RTT re-enable criteria after incident recovery**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; capability/evidence architecture now also covers nonce anti-entropy/checkpoint continuity, predicate-preserving reduction, privacy idempotent reserve/commit, retention epoch rollback, and multi-region TLS/PQ ticket revocation propagation; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen; exact executable gates pending.
