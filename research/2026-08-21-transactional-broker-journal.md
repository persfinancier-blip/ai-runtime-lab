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

LAB-071 established that possession of a Unix socket FD is not authority. Each message is attributed by kernel `SCM_CREDENTIALS`, then bound to the exact live process instance through PID + `/proc` starttime + fresh pidfd evidence. LAB-072 places journal reservation behind that exact process-instance check. A failed sender check creates neither journal reservation nor sink effect.

## Journal model

The local journal stores current credential generation, canonical request digest, stable effect key, request status `INTENT`/`UNKNOWN`/`CONFIRMED`, and a non-secret receipt only after confirmation. Reservation and rotation execute under `BEGIN IMMEDIATE`. The external side-effect simulator has its own UNIQUE stable `effect_key`, so a committed-but-unobserved effect can be reconciled instead of issued under a new identity.

A deliberately unsafe check-then-act implementation lets two workers both observe a missing request and apply the side effect twice.

## Audit finding 1 — rotation cannot outrun unresolved intent

The first corrected draft let credential rotation commit while an old-generation `INTENT` or `UNKNOWN` remained unresolved. That could allow already-authorized work to continue with the wrong secret generation. The corrected rule blocks rotation while current-generation `INTENT`/`UNKNOWN` records exist. Therefore either rotation wins first and a new old-generation reservation is stale, or reservation wins first and rotation waits for reconciliation/confirmation.

## Audit finding 2 — one durable generation authority

A naive integration used LAB-071 durable JSON generation and LAB-072 SQL generation simultaneously. Coordinating those stores would itself create a crash window. LAB-072 SQL is therefore the **single durable credential-generation authority**; LAB-071 contributes only kernel process-instance/task/scope authority.

## Audit finding 3 — process permits must not reintroduce generation authority

A later cross-layer audit found that `KernelAuthorizedBrokerWorker.authorize()` still required request generation to equal the generation copied into the process permit. That broke the intended restart semantics: after rotation, a freshly reacquired current-generation process permit could no longer reconcile an exact historical request that had already committed under the old generation.

The corrected boundary is:

- process permit proves sender PID/starttime/pidfd plus task/scope;
- SQL journal decides whether the request is an existing exact retry or a new operation;
- an existing exact `request_id + request_digest` returns/reconciles its prior effect independently of later rotation;
- a new request with a stale credential generation is rejected by the journal before any sink effect.

This preserves one generation authority while retaining safe historical idempotency.

## Process-level integration experiment

A real Linux sender process sends two datagrams through one credential-enabled Unix socket. Two distinct broker worker processes receive one message each, independently reacquire the sender via pidfd/starttime, and contend on one SQLite journal plus one idempotent sink.

Covered outcomes:

- identical authorized requests -> one sink effect and the same receipt to both callers;
- same `request_id` with different payloads -> one winner and one `RequestConflict`;
- forged sender PID -> no journal reservation and no sink effect;
- committed exact retry after journal rotation -> prior receipt, no duplicate;
- freshly reacquired current-generation process permit -> can reconcile an older committed request;
- fresh permit + genuinely new old-generation request -> `StaleCredential`;
- new current-generation operation after rotation -> succeeds with a newly bound permit;
- substitution after rotation -> remains fail-closed.

## Exact validation

Direct shell checkout was unavailable because the runtime could not resolve `github.com`, so exact published files were reconstructed through the GitHub connector and verified locally with `git hash-object` against GitHub blob IDs.

Observed exact-source results after the final authority fix:

- LAB-072 corrected suite: **26/26 passed** (journal, reopen, real process integration, restart/rotation authority regressions);
- LAB-071 regressions: **18/18 passed**;
- LAB-015 transactional-kernel regressions: **13/13 passed**;
- LAB-031 lifetime/pidfd regressions: **8/8 passed**;
- compileall passed;
- unsafe concurrent seed remains intentionally failing because check-then-act can apply the same logical effect twice.

## Boundary

This is local SQL serialization plus kernel sender authority and an idempotent external adapter. It is not distributed consensus and does not prove universal exactly-once side effects. An external system that cannot expose stable idempotency/reconciliation semantics requires a different fail-closed policy for UNKNOWN outcomes.
