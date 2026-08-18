# LAB-016 — Correctness-kernel overhead and safe batching

Date: 2026-08-18
Issue: #30

## Question

How much local execution overhead is introduced by LAB-015 correctness controls, and which transaction boundaries can be collapsed without weakening durable intent, fencing, evidence freshness or terminal correctness?

## Method and environment

The benchmark uses the existing standard-library SQLite transactional kernel. Environment observed in this run: Python 3.13.5, SQLite 3.46.1, Linux x86_64, 5 visible CPUs. SQLite WAL mode is used by the kernel. Results are local-runtime measurements only.

A pilot run was discarded during audit because each measured task recreated `Kernel(path)` and re-ran schema initialization. The corrected benchmark moves setup and warmup outside the measured task path. The committed results are from that corrected run only.

Uncontended cases use 120 measured tasks after 10 warmups. Contention uses 4 worker threads × 30 tasks. Payloads are 32 bytes and 65,536 bytes. Metrics include median/p95 task latency, known write-transaction count, conflict/retry count and approximate database/WAL/SHM byte growth.

## Primary-source grounding

SQLite documents that explicit transactions persist until COMMIT/ROLLBACK and that `BEGIN IMMEDIATE` starts a write transaction immediately; in WAL mode a commit is represented by appending a commit record to the WAL. These mechanics make transaction count and writer contention material in this approximation:

- https://www.sqlite.org/lang_transaction.html
- https://www.sqlite.org/wal.html

PostgreSQL documentation likewise distinguishes durable synchronous commit from faster weaker settings and notes that commit durability has real overhead. That supports measuring batching, but it does **not** justify mapping the SQLite numbers to PostgreSQL latency:

- https://www.postgresql.org/docs/current/non-durability.html
- https://www.postgresql.org/docs/17/wal-async-commit.html

## Results

### Uncontended median latency

| payload | minimal (1 tx) | full (6 tx) | batched2 (2 tx) | batched2 vs full |
|---|---:|---:|---:|---:|
| 32 B | 1.58 ms | 16.51 ms | 6.57 ms | -60.2% |
| 64 KiB | 1.93 ms | 15.36 ms | 5.94 ms | -61.3% |

The full correctness path is about 10.5× the unsafe minimal median for 32 B and 8.0× for 64 KiB in this environment. Most of that gap is fixed transaction/connection/commit work rather than evidence payload size.

### Four-worker contention

| payload | full throughput | batched2 throughput | gain | full p95 | batched2 p95 |
|---|---:|---:|---:|---:|---:|
| 32 B | 94.5 tasks/s | 266.2 tasks/s | 2.82× | 40.30 ms | 12.61 ms |
| 64 KiB | 93.3 tasks/s | 213.4 tasks/s | 2.29× | 37.81 ms | 21.75 ms |

Observed lock/conflict retries fell from 5→1 for 32 B and 6→1 for 64 KiB. SQLite scheduling/WAL effects make contended per-task medians non-comparable to uncontended medians; throughput, p95 and retry counts are the useful contention signals here.

Approximate database growth was dominated by the 64 KiB evidence payload itself. Both correctness variants wrote essentially the same payload bytes; safe batching mainly reduced commit/lock boundaries, not logical data volume.

## Optimization decision

**Supported:** collapse the current six-transaction local path into two authoritative transaction phases when the surrounding adapter can preserve the external-effect boundary:

1. transaction A: claim/fence + durable intent + outbox identity; commit;
2. perform/reconcile external side effect with stable idempotency identity;
3. transaction B: confirm receipt + append evidence + read authoritative evidence validity + terminal completion; commit.

This preserved the tested invariants and materially reduced local overhead.

**Rejected:** one transaction spanning the whole workflow. Keeping a database transaction open across an external side effect is both operationally expensive and semantically wrong for recovery; alternatively committing only after the side effect loses durable intent before an `UNKNOWN` outcome.

**Rejected:** caching evidence validity or fence ownership across the terminal decision. These are authoritative commit-time checks and must be fresh in transaction B.

## Correctness re-validation

The safe batching candidate has explicit tests for:

- durable `INTENT` existing before confirmation;
- valid evidence completing in transaction B;
- invalid evidence causing transaction-B rollback back to `INTENT`;
- stale fence rejection.

Observed: 4/4 tests passed. `python -m compileall -q experiments/correctness_overhead` also passed.

## Non-negotiable commit-time invariants

- ownership/fence must be checked in the deciding transaction;
- side-effect intent/outbox must be durable before externally visible work;
- receipt confirmation, evidence insertion/reference and terminal decision must be transactionally consistent;
- evidence validity/current version must be read authoritatively in the terminal transaction;
- terminal `DONE` must remain monotonic under duplicate delivery;
- lock/serialization failures trigger retry, never weaker checks.

## Limits

SQLite has a different concurrency and WAL implementation from PostgreSQL and effectively serializes writers more aggressively. Hardware, filesystem, fsync policy, connection pooling and PostgreSQL row-level locking will change absolute and relative costs. The result supports the **transaction-boundary hypothesis**, not a production latency claim.

## Stop-condition assessment

Stable local measurements were obtained, a safe batching candidate was validated against explicit invariants, and a tempting one-transaction optimization was rejected on correctness grounds. LAB-016 can close after repository patch audit/integration.
