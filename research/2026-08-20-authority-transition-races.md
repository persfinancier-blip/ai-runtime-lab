# LAB-058 — Atomic root/recovery transition serialization and race conformance

## Result

An authority-changing commit must bind the exact predecessor pair `(root_id, recovery_authority_id)` at the storage boundary. Signature validity alone is insufficient: recovery rotation and root recovery can both be individually authorized from the same predecessor while being mutually incompatible successors.

The corrected reference implementation stores the pair in one authoritative head row and uses a single SQLite `BEGIN IMMEDIATE` transaction to re-read it, verify the relevant threshold signatures, persist successor authority material and durable transition evidence, and CAS-update the head. A timeout after commit is treated as `UNKNOWN`; reconciliation is keyed by `proposal_id + transition_digest`.

The unsafe check-then-write seed demonstrates the bug directly: two proposals can both pass the check and both be recorded as accepted if validation and activation are separate critical sections.

## Donors

SQLite documents atomic commit as all-or-nothing and `BEGIN IMMEDIATE` as beginning the write transaction immediately; another writer cannot simultaneously begin a write transaction. PostgreSQL Serializable is the production analogue for a multi-client SQL service: conflicting transactions must be equivalent to a serial execution or one aborts with a serialization failure and the application retries.

## Boundary

This proves one successor for one local authoritative SQL store. It is not distributed consensus and does not prevent independently writable replicas from committing different successors. That remains a separate split-view/consensus problem.
