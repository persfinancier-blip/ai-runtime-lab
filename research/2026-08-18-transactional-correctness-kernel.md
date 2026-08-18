# LAB-015 — Transactional correctness kernel

Date: 2026-08-18

## Question
What minimal transactional contract prevents concurrent workers, stale fences, duplicate delivery, rollback gaps, and evidence/completion races from violating the correctness kernel established in LAB-005..014?

## Primary donor mechanisms

### PostgreSQL concurrency control
Primary docs:
- https://www.postgresql.org/docs/17/explicit-locking.html
- https://www.postgresql.org/docs/18/transaction-iso.html
- https://www.postgresql.org/docs/18/mvcc.html

Transferable mechanisms:
- row-level `FOR UPDATE` locks serialize conflicting writers on the same authoritative row until transaction end;
- Serializable isolation rejects executions that cannot be placed into a valid serial order; applications must retry serialization failures (`SQLSTATE 40001`);
- deadlocks are resolved by aborting a transaction, so retry is part of the application contract;
- transactions should be short and acquire locks in consistent order.

### Restate log-first durable execution
Primary docs:
- https://docs.restate.dev/references/architecture
- https://docs.restate.dev/guides/request-lifecycle
- https://docs.restate.dev/guides/databases

Transferable mechanisms:
- durable log append defines the committed step boundary;
- duplicate invocation identity is recorded before execution;
- retries replay committed journal entries instead of re-executing them;
- attempts use monotonically increasing epochs and events from superseded epochs are rejected (fencing);
- conditional/versioned database updates are the external-store analogue of optimistic concurrency.

### Transactional outbox
Primary pattern reference:
- https://microservices.io/patterns/data/transactional-outbox.html

Transferable mechanism: never split authoritative state mutation from the durable intent to publish/execute the corresponding external effect. The message/effect may be published later, but state and publication intent are committed atomically and deduplicated by stable identity.

## Prototype schema
`work(work_id, phase, generation, fence, owner, lease_until, effect_key, effect_receipt, done_evidence_id)` is the authoritative run row. `evidence` stores versioned validity. `outbox` stores deduplicated publication/effect intent.

## Transaction boundaries
- `claim`: one write transaction checks lease and atomically increments fence + generation;
- `prepare_intent`: current fence check + phase change + outbox insert in one transaction;
- `complete`: current fence + confirmed-effect + current evidence-validity check + `DONE` write in one transaction;
- invalidation is a write transaction and therefore serializes against completion in SQLite's single-writer approximation;
- stale attempts fail ownership/fence checks before mutation.

## Failure injection evidence
Unsafe split design deliberately checks valid evidence in transaction A, allows invalidation, then writes `DONE` in transaction B. Observed test failure:

`AssertionError: unsafe split transaction committed invalid DONE`

Corrected matrix: **12/12 tests passed**. Covered: claim race, stale fence, completion/invalidation ordering, duplicate delivery, crash between intent/confirmation, rollback, lock-conflict retry, atomic generation+fence, restart, unsafe split race, corrected rejection, and state+outbox atomicity.

`python -m compileall -q experiments/transactional_kernel` passed.

## Production contract
For PostgreSQL, preserve the semantics but replace SQLite's database-wide single-writer behavior with row-level locking/conditional `UPDATE ... WHERE generation=? AND fence=?`, short transactions, uniqueness constraints for idempotency, and retry on serialization/deadlock errors. Lease/fence epochs must be monotonically authoritative at the storage boundary. `DONE` must be derived inside a transaction that reads authoritative evidence validity/version and writes completion atomically.

## Limits
SQLite demonstrates invariants but not PostgreSQL MVCC, distributed clock/lease correctness, network partitions, consensus, or external-system exactly-once delivery. Transactional outbox makes intent durable; external publication still needs idempotency/reconciliation.

## Integration implications
LAB-005 generation/fence semantics move into atomic SQL predicates; LAB-007 evidence validity becomes transactionally authoritative for completion; LAB-014 authority order gains a storage boundary: advisory layers cannot outrank a failed transactional invariant.

## Stop-condition assessment
The required donor mechanisms were compared, the unsafe race was reproduced, and the corrected failure/concurrency matrix passes. Remaining work is repository audit/integration rather than broader research.
