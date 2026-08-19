# Current Lab State

Last updated: 2026-08-19

## Active objective

Advance from rollback detection to recoverable external-anchor catch-up semantics. LAB-034 is complete; LAB-035 must make the DB-commit -> independent-anchor-advance gap safely resumable under crash, timeout/unknown outcome, concurrency and transient anchor unavailability without reopening rollback windows.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-034.
- Completed Issue #65 / LAB-034.
- Merged PR #66 / LAB-034, squash merge `c04e028ee037c5c476e7c392def3d1062ecd457e`.
- Active next: Issue #67 / LAB-035 — READY.
- Active branch: none yet.
- Active PR: none.

## Last completed step

LAB-034 built an SQLite transactional replay-watermark reference. Authenticated record publication and authority/key/global/per-task watermark advancement occur inside one transaction; stale/concurrent expected-sequence writers are rejected. A simulated full database snapshot rollback demonstrated the exact limit of SQL-only freshness: an older internally valid snapshot is accepted without an independent anchor, but is rejected when a monotonic external anchor remains ahead.

A separate remote audit found an unsafe first design that allowed consequential continuation while the external anchor lagged the DB. That creates an unprotected rollback window. The corrected verifier requires `anchor == DB global_sequence` whenever external anti-rollback protection is configured; `anchor > DB` is rollback detection and `anchor < DB` is unanchored state, both fail closed.

## Evidence produced

- `experiments/replay_watermark/protocol.py`
- `experiments/replay_watermark/tests/test_protocol.py`
- `experiments/replay_watermark/tests/unsafe_split_expected_failure.py`
- `research/2026-08-19-replay-watermark-rollback-resistance.md`
- Unsafe split-commit seed: expected failure (`watermark 0 != 1`).
- Corrected deterministic suite: 11/11 passed.
- `python -m compileall -q experiments` passed.
- Concurrent expected-sequence writers: one success, one stale rejection.
- Primary mechanisms: SQLite atomic commit/isolation; TPM2 NV monotonic-counter mechanism as an example independent anchor trust domain.
- PR #66 remote patch-audited and squash-merged as `c04e028ee037c5c476e7c392def3d1062ecd457e`.

## Known blockers / constraints

- Local shell DNS to GitHub remains unavailable/unreliable; GitHub connector plus local execution is the supported path.
- SQLite is a transactional semantics approximation, not PostgreSQL performance/locking validation.
- An ordinary database cannot prove the entire DB was not restored to an older valid snapshot; external anti-rollback requires an independently monotonic trust source.
- DB and external anchor do not share one atomic transaction. LAB-034 therefore fails closed while the anchor lags; LAB-035 must define safe catch-up/reconciliation rather than weakening that rule.
- No real TPM/KMS monotonic provider has been proven available in the current runtime; LAB-035 should use a deterministic adapter abstraction unless a real capability is observed.
- LAB-032 fresh pidfd/starttime reconciliation remains mandatory after launch-record authenticity and freshness checks.

## Exact next action

Start Issue #67 / LAB-035. Reuse LAB-034 replay-watermark concepts and build `experiments/anchor_catchup/`. Reproduce unsafe blind anchor retry; then implement durable proof-bound catch-up with DB-commit-before-anchor sequencing, restart recovery, timeout/UNKNOWN reconciliation, duplicate/concurrent catch-up, ahead/behind/unavailable anchor states, authority/key rotation fencing, and evidence without anchor/key secrets. Research primary monotonic-counter retry/reconciliation mechanisms where available, run deterministic tests and separate audit, then integrate only on observed validation.

## Backlog

- #67 / LAB-035 — external monotonic-anchor catch-up and failure semantics — READY.
- Crash-resilient scavenging for named credential-file fallback — candidate follow-up.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
