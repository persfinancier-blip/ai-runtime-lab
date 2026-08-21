# LAB-072 — Concurrent broker request serialization and transactional effect journal

## Research question

How should LAB-071's broker serialize concurrent/restarted workers so that one logical request has one durable identity, credential rotation cannot race unresolved old-generation work, timeout/UNKNOWN recovery does not duplicate an external effect, and no durable reservation can bypass kernel-observed sender authority?

## Donor mechanisms

### SQLite transaction boundary

Primary source: https://www.sqlite.org/lang_transaction.html

SQLite permits multiple simultaneous readers but only one simultaneous write transaction. `BEGIN IMMEDIATE` starts the write transaction immediately rather than waiting for the first write. The reference journal uses this as a deterministic local serialization boundary for request reservation and credential rotation.

### PostgreSQL serializable transactions

Primary source: https://www.postgresql.org/docs/current/transaction-iso.html

PostgreSQL Serializable isolation provides the production analogue: concurrent transactions must have an outcome equivalent to some serial execution, and applications must be prepared to retry serialization failures. LAB-072 does not claim SQLite's single-writer behavior is a production concurrency/performance model for PostgreSQL.

### LAB-071 sender authority

LAB-071 established that possession of a Unix socket FD is not authority. Each message is attributed by kernel `SCM_CREDENTIALS`, then bound to the exact live process instance through PID + `/proc` starttime + fresh pidfd evidence.

LAB-072 now places journal reservation behind that exact process-instance check. A failed sender check creates neither journal reservation nor sink effect.

## Journal model

The local journal stores:

- current credential generation;
- canonical request digest;
- stable effect key;
- request status `INTENT`, `UNKNOWN`, or `CONFIRMED`;
- non-secret receipt only after confirmation.

Reservation and rotation execute under `BEGIN IMMEDIATE`. The external side-effect simulator has its own UNIQUE stable `effect_key`, so a committed-but-unobserved effect can be reconciled instead of issued under a new identity.

A deliberately unsafe check-then-act implementation lets two workers both observe a missing request and apply the side effect twice.

## Audit finding 1 — rotation cannot outrun unresolved old-generation intent

The first corrected draft let credential rotation commit while an old-generation `INTENT` or `UNKNOWN` remained unresolved. That is semantically unsafe unless the broker also retains the corresponding old raw credential generation: after rotation, completing the already-authorized intent with the new credential would bind the wrong secret material.

The corrected rule blocks rotation while current-generation `INTENT`/`UNKNOWN` records exist. This produces only two accepted reservation-vs-rotation serial outcomes:

- rotation wins first -> old-generation reservation is stale;
- reservation wins first -> rotation is blocked until reconciliation/confirmation.

## Audit finding 2 — do not create two generation authorities

A naive integration would use LAB-071's durable JSON `CredentialBroker.generation` and LAB-072's SQL `credential_generation` simultaneously. Coordinating their rotation would itself require a cross-store transaction and could leave a split-brain generation after crash.

The integration therefore treats LAB-072 SQL as the **single durable credential-generation authority**. LAB-071 is reused only for kernel process-instance identity. `bind_sender_to_journal_generation()` obtains the current SQL generation, binds it to a PID/starttime permit, and installs LAB-071's pidfd authority. New operations after rotation require a newly bound permit; exact already-committed retries with the older permit remain digest-bound and reconcilable.

Promotion into a shared runtime should expose LAB-071's side-effect-free sender reacquisition/validation primitives as public APIs; this experiment intentionally reuses the exact existing private implementation rather than copying weaker PID logic.

## Process-level integration experiment

A real Linux sender process sends two datagrams through one credential-enabled Unix socket. Two distinct broker worker processes receive one message each, independently reacquire the sender process via pidfd/starttime, and contend on one SQLite journal + one idempotent sink.

Required outcomes encoded in the published test:

- two identical authorized requests -> both callers receive the same receipt, sink row count = 1;
- same `request_id` with different payloads -> exactly one winner, one `RequestConflict`, sink row count = 1;
- forged sender PID -> sender validation fails before any journal row exists;
- committed exact retry after journal rotation -> returns existing receipt, no duplicate effect;
- new operation after rotation -> succeeds only after binding a new generation permit;
- substitution after rotation -> remains fail-closed.

A local **interface-compatible smoke reconstruction** of the process test passed the identical-request, substitution, and new-generation-permit scenarios. This is supporting evidence only; it is not exact-source evidence for PR #136.

## Exact evidence already established for first slice

- published first-slice protocol blob `6066d90b3032eeefc0f2dbbd272c09a9a716b5b2` matched locally executed bytes before the authority integration commits;
- first-slice corrected suite: 13/13 passed;
- 20 repeated reservation-vs-rotation races produced only safe serial outcomes;
- unsafe concurrent seed failed because two identical requests produced two side effects;
- compileall passed.

## Remaining merge gate

The current authority/process integration is published but has not yet received an exact-source execution because direct GitHub checkout is unavailable in this runtime. Before LAB-072 can be DONE:

1. reconstruct exact PR #136 head bytes through the GitHub connector and verify Git blob IDs locally;
2. execute LAB-072 unit + process integration suites on those exact bytes;
3. execute exact LAB-071, LAB-015, and LAB-031 regressions plus compileall;
4. perform a fresh full remote patch audit and fix any finding;
5. only then mark the PR ready and integrate.

## Boundary

This is local SQL serialization plus an idempotent external adapter. It is not distributed consensus and does not prove universal exactly-once side effects. An external system that cannot expose stable idempotency/reconciliation semantics requires a different fail-closed policy for UNKNOWN outcomes.
