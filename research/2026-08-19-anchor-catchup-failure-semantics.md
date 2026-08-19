# LAB-035 — External monotonic-anchor catch-up and failure semantics

Date: 2026-08-19  
Issue: #67  
Branch: `lab/035-anchor-catchup`

## Question

How can a durable agent safely recover when a database commit advances its authenticated sequence but the independent anti-rollback anchor has not yet been observed at the same position?

LAB-034 intentionally failed closed whenever `anchor != DB global_sequence`. LAB-035 preserves that rule for consequential continuation and adds a recovery protocol for the legitimate one-step `DB commit -> anchor advance` gap.

## Primary-source mechanisms

### TPM NV counter: increment, then read

`tpm2_nvincrement` documents the TPM NV counter operation as an increment of an NV index configured as a counter, and its example reads the index after increment using `tpm2_nvread`.

Primary source: https://tpm2-tools.readthedocs.io/en/stable/man/tpm2_nvincrement.1/

Transferable mechanism: model the independent anchor as a monotonic `+1` counter rather than assuming an arbitrary absolute-value write. If the outcome of an increment is unknown, current position must be observed before another increment is considered.

### Cloud Spanner UNKNOWN commit outcome: observe current state

Google Cloud Spanner documents that `Commit` can rarely return `UNKNOWN`; its guidance is to perform another read to determine the state as it exists now rather than assuming success or failure.

Primary source: https://cloud.google.com/spanner/docs/reference/rest/v1/projects.instances.databases.sessions/commit

Transferable mechanism: unknown external outcomes are reconciliation states. A retry protocol should query durable observable state first instead of repeating a side effect blindly.

### Spanner transaction retries and external side effects

Spanner transaction documentation warns that transaction bodies may execute multiple times and external side effects can therefore occur multiple times when embedded in retryable transaction code.

Primary source: https://cloud.google.com/spanner/docs/transactions

Transferable mechanism: the external monotonic increment remains outside the DB transaction, with its own durable intent and explicit reconciliation semantics.

## Minimal state machine

```text
DB ALIGNED(sequence=N, anchor=N)
  -> atomic DB publication/rotation
     stores authenticated anchor intent for N+1 as PENDING
     DB sequence becomes N+1

PENDING(sequence=N+1, anchor=N)
  -> read anchor
       anchor > DB       => ROLLBACK_ALARM / BLOCK
       anchor < DB - 1   => UNSUPPORTED_GAP / BLOCK
       anchor == DB      => confirm intent, ALIGNED
       anchor == DB - 1  => increment(expected=N)
             success     => re-check DB authority/sequence, confirm intent
             UNKNOWN     => leave PENDING; later retry starts with read
             conflict    => another supervisor may have won; re-read/reconcile
       unavailable       => leave PENDING / BLOCK consequential continuation
```

There is deliberately only one pending anchor intent. This caps the recoverable gap at one and prevents a transient anchor outage from accumulating unauthenticated/skipped positions.

## Authority/key rotation

An audit of the first prototype found that changing authority/key metadata without advancing/anchoring a new sequence would diverge from LAB-034 and could make the new authority state externally unauthenticated. The corrected design treats rotation as a new global sequence. It creates a `PENDING` anchor intent authenticated under the new key generation. Consequential continuation remains blocked until that rotation sequence is externally anchored.

An older confirmed record cannot substitute for the rotation intent because the current intent must match the current authority epoch and key generation.

## Failure experiment

Unsafe baseline:

```text
test_blind_retry_overshoots ... FAIL
AssertionError: 2 != 1 : blind retry double-incremented anchor
```

The first increment committed but returned an unknown outcome. Blind retry incremented again and moved the external anchor from 1 to 2 while the DB expected sequence 1.

Corrected observed validation:

```text
Ran 13 tests in 0.195s
OK
```

`python -m compileall -q experiments` also passed.

Covered scenarios include successful catch-up, restart recovery, UNKNOWN reconciliation without second increment, duplicate/concurrent catch-up, rollback detection, forged/missing proof rejection, one-pending-intent enforcement, rotation fencing and anchoring, old-proof rejection after rotation, transient anchor unavailability, and evidence without anchor/key secrets.

## Boundary distinctions

**Anchor unavailable** means freshness cannot currently be established. It is not proof of rollback.

**Anchor ahead of DB** is a rollback/restore signal because the independent monotonic trust domain remembers a position newer than the DB snapshot.

**DB authenticity** is separate again: HMAC-authenticated durable intent proves that the DB state is authorized for catch-up, but does not by itself prove freshness if the entire DB and its watermarks were rolled back.

## Integration with prior LABs

- LAB-033 authenticates durable records and separates authentication from replay freshness.
- LAB-034 makes DB publication + internal watermark atomic and requires external anchor equality before consequential continuation.
- LAB-035 adds the recovery bridge from a legitimate one-step DB lead back to equality without weakening LAB-034's continuation rule.

Production-shaped contract:

`atomic DB intent -> independent monotonic advance -> read/reconcile -> DB confirm -> consequential continuation`

## Non-goals and limits

- No real TPM/KMS monotonic provider was observed in this runtime.
- No arbitrary sequence skipping; the reference permits only one-step catch-up.
- No distributed consensus or cross-system atomic transaction.
- SQLite is a semantic approximation, not PostgreSQL locking/performance validation.

## Stop-condition assessment

The required crash/retry/reconciliation matrix passes after a seeded unsafe blind-retry failure and a separate audit fix to authority/key rotation semantics. Remaining work is remote patch audit and integration, not broader research.
