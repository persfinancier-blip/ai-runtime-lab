# LAB-072 — Concurrent broker request serialization and transactional effect journal

## Research question

How should LAB-071's broker serialize concurrent/restarted workers so that one logical request has one durable identity, credential rotation cannot race unresolved old-generation work, and timeout/UNKNOWN recovery does not duplicate an external effect?

## Donor mechanisms

### SQLite transaction boundary

Primary source: https://www.sqlite.org/lang_transaction.html

SQLite permits multiple simultaneous readers but only one simultaneous write transaction. `BEGIN IMMEDIATE` starts the write transaction immediately rather than waiting for the first write. The reference journal uses this as a deterministic local serialization boundary for request reservation and credential rotation.

### PostgreSQL serializable transactions

Primary source: https://www.postgresql.org/docs/current/transaction-iso.html

PostgreSQL Serializable isolation provides the production analogue: concurrent transactions must have an outcome equivalent to some serial execution, and applications must be prepared to retry serialization failures. LAB-072 does not claim SQLite's single-writer behavior is a production concurrency/performance model for PostgreSQL.

### Prior lab mechanisms

LAB-005 established durable intent, stable idempotency identity, explicit UNKNOWN, reconciliation, generation, and fencing as separate correctness concepts. LAB-015 established that state transitions which decide authority must be atomic at the storage boundary rather than coordinated only by caller discipline. LAB-071 established the per-message sender/pidfd authority boundary and rotation-safe exact retry ordering.

## First experiment

The local journal stores:

- current credential generation;
- canonical request digest;
- stable effect key;
- request status `INTENT`, `UNKNOWN`, or `CONFIRMED`;
- non-secret receipt only after confirmation.

Reservation and rotation execute under `BEGIN IMMEDIATE`. The external side-effect simulator has its own UNIQUE stable `effect_key`, so a committed-but-unobserved effect can be reconciled instead of issued under a new identity.

A deliberately unsafe check-then-act implementation lets two threads both observe a missing request and apply the side effect twice.

## Audit finding: rotation cannot outrun unresolved old-generation intent

The first corrected draft let credential rotation commit while an old-generation `INTENT` or `UNKNOWN` remained unresolved. That is semantically unsafe unless the broker also retains the corresponding old raw credential generation: after rotation, completing the already-authorized intent with the new credential would bind the wrong secret material.

The corrected reference rule therefore blocks rotation while current-generation `INTENT`/`UNKNOWN` records exist. They must first be reconciled/confirmed (or a future protocol would need an explicit retained-generation secret lifecycle). This produces a deterministic serial outcome in a rotation-vs-reservation race:

- rotation wins first -> old-generation reservation is stale;
- reservation wins first -> rotation is blocked by pending effects.

## Current local evidence

- corrected deterministic suite: 13/13 passed;
- 20 repeated reservation-vs-rotation races produced only the two safe serial outcomes;
- unsafe concurrent seed fails because two identical requests produce two side effects;
- UNKNOWN after sink commit reconciles without duplication;
- concurrent retries after UNKNOWN share one sink receipt;
- journal and sink database bytes contain no raw credential;
- compileall passed.

## Remaining integration gate

This first slice isolates transaction/effect semantics. Before LAB-072 can be DONE, the journal must sit behind LAB-071's actual kernel-observed `SCM_CREDENTIALS` + pidfd/starttime sender authority, rather than accepting an abstract `Request` alone. Exact published-source execution, process-level concurrency, relevant LAB-071/LAB-015/LAB-031 regressions, and a second remote audit are still required.

## Boundary

This is local SQL serialization plus an idempotent external adapter. It is not distributed consensus and does not prove universal exactly-once side effects. An external system that cannot expose stable idempotency/reconciliation semantics requires a different fail-closed policy for UNKNOWN outcomes.
