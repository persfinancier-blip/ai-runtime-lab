# Current Lab State

Last updated: 2026-09-09

## Active objective
LAB-086 — finish the exact executable/security gate for asymmetric break-glass history migration, then reconcile/merge only if every real-schema regression and conflict audit passes.

## Active issue / branch / PR
- Priority #1: #163 / LAB-086 — IN_PROGRESS; draft PR #165 at head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; keep draft and do not merge without the exact retained gate.
- Other open drafts remain: LAB-088/#167 PR #172; LAB-091/#170 PR #173; LAB-090/#169 PR #175; LAB-092/#176 PR #177.
- Frozen design follow-up: LAB-093/#178 plus LAB-094..100/#179..185.

## Last completed step
Re-read `AGENTS.md`, this handoff and `prompts/SELF_RESUME.md`; inspected open issues and active draft PRs; resumed LAB-086 first.

Current-run capability/state:
- PR #165 remains `open`, `draft`, `mergeable=false` at exact head `ee210a47221b6df53f3518aa3af74f76c5b0122b`; no draft/merge-state change was attempted.
- GitHub connector reads/writes are available and were used for durable research/state writes.
- The retained exact LAB-086 gate still requires byte-exact local reconstruction/execution of the LAB-080→086 closure, unsafe expected-failure seed, full compileall and final security/reconciliation/conflict audit. No supported connector operation in this run materialized that exact executable closure into a local runtime, so no new LAB-086 behavioral/compile PASS is claimed and no large security-critical source was manually/model reserialized.

Completed the recorded distinct fallback and froze `SINK_FENCE_RESTORE_PARSER_SCHEMA_TOMBSTONE_PQ_DR_V1_FROZEN` in `research/2026-09-09-sink-fence-restore-parser-schema-tombstone-pq-dr-v1.md`, main commit `3c9bedbc9aecd998240c6e0029075a06b57ab063`; #178 comment `5605121253` records the result.

Key decisions:
- `RESTORED_SINK_STATE != AUTHORITY_TO_REUSE_OLD_FENCE`: snapshot/rollback recovery must preserve or independently re-establish the highest accepted fencing floor; snapshot integrity is not freshness authority. Restored sinks without a sufficient monotonic floor fail closed for consequential writes.
- `VERIFIER_A_ACCEPTS && VERIFIER_B_ACCEPTS != SAME_SEMANTICS`: dual-verifier transitions require equality of canonical semantic projections, not merely two successful signature/parser decisions. Duplicate JSON/CBOR keys, number coercion, Unicode/default handling and unknown critical fields are fail-closed parser boundaries.
- `OLDER_VERIFIER_IGNORES_FIELD != FIELD_OPTIONAL`: dependency-attestation schemas are generation-bound with explicit mandatory/critical authority fields. An older verifier that cannot interpret a newly mandatory dependency edge is unsupported, not green; schema compatibility is not downgrade authority.
- `PRIMARY_ROW_ABSENT != DELETION_CONVERGED`: deletion is a versioned tombstone transition covering primary state plus derived indexes/caches/materialized views/queues/replicas/backups. Pre-delete restore/import cannot resurrect a predecessor object beneath a later tombstone.
- `TICKET_DECRYPTS != TICKET_SPEND_AUTHORITY_OWNED_HERE`: PQ/TLS regional DR may replicate ticket decryption keys without duplicating consequential 0-RTT spend authority. Ambiguous ownership/failover disables consequential 0-RTT or falls back until old-owner fencing/new authority generation is proven.
- frozen 40-case RED-first matrix across sink restore fencing, parser/canonicalization differential, security-schema evolution, tombstone reintroduction and PQ/TLS resumption disaster recovery.

Primary donors: etcd disaster-recovery revision bump/mark-compacted; Consul session/lock fencing semantics; RFC 8785 JCS; RFC 8949/9052 CBOR/COSE deterministic/duplicate-key rules; Protocol Buffers schema-evolution guidance; DynamoDB global-table delete propagation; RFC 9846 TLS 1.3 single-use ticket and single-authoritative-zone anti-replay semantics.

## Known failures / blockers
- LAB-086 remains priority #1. Remaining blocker is exact source execution of the complete real-ledger closure.
- GitHub connector can read/write repository content, but the current run still did not expose a supported automated connector-to-local materialization path for the full exact executable closure. Manual/model reserialization of the large security-critical closure remains prohibited by the retained byte-hash gate.
- PR #165 must remain draft until branch-local dependency-blob verification, complete real-schema LAB-086 tests, unsafe expected-failure seed, compileall, security reconciliation and branch/main conflict audit execute on exact source.
- Keep PRs #165/#172/#173/#175/#177 draft until their retained exact gates execute.
- LAB-093 and LAB-094..100 design freezes do not substitute for executable RED/GREEN proof.

## Exact next action
LAB-086 first: if an automated exact-source path becomes available, reconstruct/check out pinned executable source `1fa85a0e34c9ae67da57f1e64dadccf211feacc0` / PR head lineage, verify every dependency/test blob against `research/2026-08-27-lab086-exact-gate-manifest.md`, execute every normal LAB-086 real-schema test, run `unsafe_legacy_promotion_expected_failure.py` separately and require the intended failure, run full compileall, then perform final security/reconciliation + branch/main conflict audit. Fix every observed blocker before changing draft/merge status.

If exact execution remains unavailable, next distinct evidence task is **fence-floor authority compromise/recovery + semantic-projection hash-algorithm migration and verifier-quorum independence + schema-registry equivocation/split-view + tombstone-GC witness/backup-discovery completeness + PQ ticket-policy state under client-side ticket caching, server-identity rollover and cross-service SNI/ALPN rebinding**.

If exact source execution becomes available for other pending work first: run LAB-088 supported/downstream gates and LAB-091 full supported-surface gates, then implement tests first for frozen LAB-090..100 contracts and execute their RED matrices before production refactors.

## Backlog
- #163 / LAB-086 — IN_PROGRESS; exact complete real-ledger gate + unsafe seed + full compileall + conflict/security audit pending.
- #167 / LAB-088 — IN_PROGRESS; supported/downstream execution pending.
- #169 / LAB-090 — IN_PROGRESS; exact RED/GREEN pending.
- #170 / LAB-091 — IN_PROGRESS; real-stack behavioral gates pending.
- #176 / LAB-092 — IN_PROGRESS; exact RED/full gate pending.
- #178 / LAB-093 — READY; capability/evidence architecture now also covers sink-fence rollback/restore persistence, semantic dual-verifier equivalence, mandatory-field schema anti-downgrade, tombstone reintroduction prevention and single-authority PQ/TLS resumption across regional DR; exact RED/GREEN pending.
- #179..185 / LAB-094..100 — READY/design-frozen as recorded in their issues; exact executable gates pending.
