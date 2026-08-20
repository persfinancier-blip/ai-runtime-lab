# Current Lab State

Last updated: 2026-08-20

## Active objective

LAB-061 — bound live transition-history storage by safely pruning an authenticated/checkpointed prefix while preserving deterministic restart and separately auditable archive evidence.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-060.
- Completed Issue #111 / LAB-060.
- Merged PR #112 / LAB-060 as `a4560fa11a8d23030b7b3f73192b89c6165c0fe6`.
- Next: Issue #113 / LAB-061 — READY.
- Active branch: none yet.
- Active PR: none.

## Last completed step

LAB-060 added an authenticated prefix-checkpoint layer over LAB-059. A checkpoint is created only after full bootstrap→head verification while a write-excluding transaction is held. It binds schema/protocol version, bootstrap-derived history identity, sequence, derived root/recovery content IDs, a rolling prefix commitment, external-anchor identity and signer identity. Restart verifies the checkpoint and then only the suffix using the same LAB-059 threshold-signature/payload/digest rules.

An audit found and fixed a mixed-SQL-snapshot race: checkpoint validation, suffix verification and final head comparison now occur in one consistent read transaction. An explicit O(N) `audit_checkpoint_prefix()` was added for forensic/archive verification without putting prefix rereads back onto the normal O(suffix) restart path. Strict checkpoint type/hex validation was also added.

## Evidence produced

- `experiments/transition_history_checkpoints/protocol.py`
- `experiments/transition_history_checkpoints/tests/test_protocol.py`
- `experiments/transition_history_checkpoints/tests/unsafe_cache_expected_failure.py`
- `experiments/transition_history_checkpoints/README.md`
- `research/2026-08-20-authenticated-history-checkpoints.md`
- Corrected exact-source suite: 14/14 passed.
- Unsafe seed: failed as expected because an unauthenticated derived-state cache was accepted.
- Compileall: passed.
- Protocol Git blob `b28fb47a86bcc9d72f5ed5565090a2ea3854607d`.
- Corrected-test Git blob `37d963a2e2f55e401a95116c7ab66561f6a4f11d`.
- Unsafe-seed Git blob `dbd162a4f93929f6aac8eec3242629aad87bd0b0`.
- PR #112 remote patch-audited and squash-merged as `a4560fa11a8d23030b7b3f73192b89c6165c0fe6`.

## Known blockers / constraints

- No active blocker.
- LAB-060 bounds restart verification work by suffix length but does not reduce O(N) storage growth of the live `transitions` table.
- Normal bounded restart deliberately trusts the authenticated checkpoint summary and does not reread archived prefix bytes; explicit prefix commitment audit remains available when forensic verification is needed.
- A local checkpoint watermark cannot detect rollback of the entire internally consistent database snapshot. LAB-034–037 external monotonic-anchor work remains authoritative for whole-store freshness.
- Pruning/deleting live SQL rows must not be described as forensic erasure.
- Local SQL compaction is not distributed consensus/fork prevention across independently writable replicas.

## Exact next action

Start Issue #113 / LAB-061. Extend LAB-060 rather than creating an unrelated snapshot system. Build a deterministic compaction layer that authorizes destructive prefix pruning only from the current authenticated checkpoint, exports/binds an exact canonical archive artifact/manifest, and atomically records a new live-history base `(base_sequence, root_id, recovery_id, prefix/archive commitment)` with deletion of the checkpointed prefix. Prove restart from compacted base + suffix equals the pre-prune terminal state, that new transitions and a second compaction remain valid, and that crash/partial-prune, stale checkpoint, archive substitution/tamper, retained suffix gaps and head mismatch fail closed. Keep whole-store freshness delegated to LAB-034–037.

## Backlog

- #113 / LAB-061 — authenticated history pruning and archival-boundary conformance — READY.
- Reliable gossip transport, Byzantine consensus, and fork prevention remain out of scope unless evidence makes them the next correctness bottleneck.
- Crash-resilient scavenging for named credential-file fallback — candidate follow-up.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
