# LAB-034 — Trusted replay watermark durability and rollback resistance

Date: 2026-08-19

## Question

How far can ordinary transactional SQL carry authenticated-record freshness, and where does anti-rollback require an independently monotonic trust source?

## Primary donor mechanisms

### SQLite atomic commit and isolation

Primary sources:
- https://www.sqlite.org/atomiccommit.html
- https://www.sqlite.org/isolation.html

Transferable mechanisms:
- updates in one transaction appear all-or-nothing, including crash recovery;
- writes are serialized, so a monotonic row can be advanced under one writer at a time;
- record publication and watermark advancement belong in the same transaction.

Boundary: these guarantees describe the database's transaction history. Restoring the whole database file to an older valid snapshot restores an older internally consistent history; the database cannot infer that an external rollback occurred.

### TPM-style NV counter as external monotonic anchor

Reference mechanism:
- TPM2 NV counter / `TPM2_NV_Increment` as exposed by tpm2-tools documentation: a non-volatile index configured as a counter can only be incremented.

Transferable mechanism: an anti-rollback anchor must have monotonic state whose trust domain is independent from the rollback-prone database. LAB-034 models only the interface (`read`, monotonic `advance`) and does not claim a TPM exists in the current runtime.

## Transactional model

Durable SQL state contains:
- current authority epoch;
- current key generation;
- global monotonic sequence;
- per-task accepted sequence + authenticated record identity.

Publication is a single transaction:

`BEGIN IMMEDIATE -> read current epoch/key/sequence -> create authenticated record -> conditional global sequence advance -> per-task watermark advance -> COMMIT`

Rotation atomically advances authority epoch, key generation, and global sequence, so records from the previous authority are fenced immediately after commit.

## Unsafe baseline

The deliberately unsafe design commits the authenticated record first and advances its freshness watermark later. A crash between those writes leaves a durable record with stale freshness state. The seeded test fails with `watermark 0 != expected 1`.

## Corrected experiment

Observed locally:
- corrected deterministic suite: 11/11 passed;
- compileall: passed;
- unsafe split-commit seed: failed as expected.

Covered matrix:
1. monotonic advance survives restart;
2. stale writer rejected;
3. two concurrent expected-sequence writers -> exactly one wins;
4. older authenticated record rejected after a newer record commits;
5. authority/key rotation fences old records;
6. duplicate verification of the current record is idempotent;
7. simulated crash inside transaction rolls record/watermark changes back together;
8. lagging external anchor blocks consequential continuation until it catches up;
9. full database snapshot rollback is **not detected by SQL alone**;
10. the same rollback is detected when an independent anchor remains ahead;
11. evidence contains only public anchor position/status, never key/anchor secret material.

## Exact guarantee boundary

SQL alone can protect against split commits inside the DB, lost/stale concurrent writers when updates are conditional/serialized, restart after incomplete transactions, and stale records relative to a newer state still present in that DB.

SQL alone cannot prove that its entire durable state was not replaced by an older valid snapshot. If the record, task watermark, authority epoch and global sequence all roll back together, the snapshot is internally consistent.

An external monotonic anchor can detect that condition by retaining a value greater than the restored DB sequence. This still is not a distributed atomic commit with the DB. Safe sequencing is DB commit first, anchor advance second, but **consequential continuation remains blocked while the anchor is behind**. Once the anchor reaches the DB sequence, rollback of the database to an earlier sequence leaves the anchor ahead and verification fails closed. Production design must define recovery when anchor advancement itself is unavailable.

## Audit findings

- Authentication, database atomicity and anti-rollback are three separate properties; none substitutes for the others.
- A first implementation incorrectly allowed use of DB state while the external anchor lagged. That creates an unprotected rollback window. The corrected verifier requires anchor == DB sequence when external anti-rollback is required.
- The external anchor value is not a secret. Authentication keys/anchor authorization secrets must never enter evidence.
- The SQLite prototype approximates transactional semantics, not PostgreSQL performance or locking behavior.
- The anchor abstraction demonstrates the trust boundary; it is not hardware attestation.

## Integration with LAB-033 / LAB-032

Order for restart continuation becomes:

`authenticate launch record -> compare transactional authority/key/task watermark -> require external anti-rollback anchor equality when configured -> fresh LAB-032 pidfd/starttime reconciliation -> allow consequential continuation`

A fresh process identity check cannot repair a replayed authority record; likewise a valid signed record cannot prove database freshness.
