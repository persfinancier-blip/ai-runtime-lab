# Current Lab State

Last updated: 2026-09-10

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; current connector read confirms `open`, `draft=true`, `mergeable=false`. Keep draft.
- Other open drafts: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues/PRs; resumed LAB-086 first.

Current-run capability observation:
- Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository execution with `Could not resolve host: github.com`.
- GitHub connector reads/writes are available.
- No supported non-model connector-to-local-filesystem materialization primitive is exposed in this run. Manual/model reserialization of the security-critical LAB-086 closure remains prohibited by the retained byte-exact gate.
- Therefore no new LAB-086 behavioral, unsafe-seed, compileall, security-reconciliation or conflict PASS is claimed; PR #165 remains draft.

Completed the recorded distinct fallback and froze `CHECKPOINT_EQUIVOCATION_REDUCER_FLAKINESS_PRIVACY_PARTITION_RETENTION_REKEY_PQ_0RTT_REENABLE_V1_FROZEN` in `research/2026-09-10-checkpoint-equivocation-reducer-flakiness-privacy-partition-retention-rekey-pq-0rtt-reenable-v1.md`, main commit `99b6fced6d9d441d54bd206dcc76f37f2e8927fa`; #178 comment `5611688883` records the result.

Key decisions:
- `QUORUM_SIGNED_CHECKPOINT != UNIQUE_CHECKPOINT_HISTORY`: incompatible threshold-valid heads for one logical generation/sequence are split-view evidence. Anti-entropy cannot select by arrival time, timestamp or post-hoc majority; compaction proofs and equivocation evidence must survive the rows/storage lifecycle they summarize.
- `ONE_REPRODUCTION != STABLE_REPRODUCTION`: nondeterministic delta debugging requires a frozen security predicate, a reproducibility/environment envelope and an auditable repeated-run decision rule. A minimized case that fails via another invariant is a separate finding, not the original witness.
- `REGION_B_DID_NOT_SEE_COMMIT != DISCLOSURE_DID_NOT_HAPPEN`: partition-tolerant privacy disclosure requires globally stable reservations or pre-accounted non-overlapping regional escrow. Ambiguous egress remains charged/unknown; reconciliation is monotonic and cannot lower observed spend.
- `NEW_WITNESS_KEY != CLEAN_HISTORY`: retention witness compromise/rekey creates a successor trust generation plus an explicit degraded interval. New key freshness cannot retroactively authenticate destructive history from the compromised interval; stale revoked witness generations stay revoked across restore.
- `REVOCATION_PUBLISHED != REVOCATION_OBSERVED_BY_ALL_SPEND_AUTHORITIES` and `KEY_ROTATED != OLD_KEY_ERASED`: post-incident TLS/PQ recovery separately tracks revocation-floor convergence, ticket-key erasure evidence across the declared recovery universe, replay-store recovery and a new 0-RTT re-enable transition. Policy-valid 1-RTT may return while 0-RTT remains disabled.
- Frozen 40-case RED-first matrix across checkpoint split-view/compaction, flaky predicate-preserving reducers, privacy partition reconciliation, retention witness rekey and PQ/ECH ticket incident recovery.

Primary donors: etcd disaster-recovery revision bump/mark-compacted semantics; RFC 9162; RFC 5011; RFC 9846; RFC 9849; SLSA provenance/reproducibility guidance; NIST SP 800-226; NIST SP 800-88 Rev. 2.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact local execution of the complete real-ledger closure.
- Direct shell transport cannot currently resolve `github.com`.
- Connector can read exact pinned blobs but this run has no supported non-model connector-to-local-filesystem materialization primitive.
- Complete real-schema LAB-086 tests, unsafe expected-failure seed, full compileall, security reconciliation and branch/main conflict audit remain pending.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093..100 design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: probe once for a newly supported non-model materialization path for pinned connector bytes at exact executable snapshot `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. If available, materialize the exact manifest-listed implementation closure plus all `test_*.py` and the pinned LAB-085 fixture helper; verify every file with `git hash-object` against the pinned blob before import; execute all normal LAB-086 real-schema tests; run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure; run full compileall; then perform final security/reconciliation and branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

Do not manually copy connector payloads into the executor. If no supported materialization path exists, record the per-run observation and move directly to the next distinct evidence task: **checkpoint successor/adjudication authority after equivocation + flaky-test sequential decision bias and rare-event preservation + privacy escrow transfer/rebalance during partitions + retention degraded-interval reconciliation with independent receipts + PQ/ECH incident recovery under partial key-erasure attestation, late edge rejoin and resumption-ticket lifetime bounding**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; capability/evidence architecture now also covers checkpoint-equivocation/compaction-proof survivability, nondeterministic predicate-preserving reducers, partition-safe privacy reservations/escrow, retention witness compromise/rekey, and multi-region TLS/PQ revocation/erasure/0-RTT re-enable recovery; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen; exact executable gates pending.
