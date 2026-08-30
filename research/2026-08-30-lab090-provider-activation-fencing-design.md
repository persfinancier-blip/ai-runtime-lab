# LAB-090 — provider-generation activation fencing design

Date: 2026-08-30
Issue: #169

## Problem reproduced by existing issue

The current LAB-082/LAB-086 rotation shape authenticates the candidate provider position before opening the authoritative SQLite writer transaction. SQLite can serialize local SQL writers, but cannot lock an external provider. Therefore the schedule `read position N -> external provider advances to N+1 -> SQL commits generation at durable tail N` is reachable unless the provider itself participates in the handoff.

This is primarily a correctness/availability defect, not an authority escalation: the newly durable provider generation can already be ahead of the durable shared-anchor tail immediately after activation.

## Primary-source mechanisms reviewed

Two production APIs expose the relevant primitive directly:

1. Google Cloud Storage request preconditions support `ifGenerationMatch`: the write proceeds only if the target's immutable generation still equals the expected value; otherwise it fails with HTTP 412. Google explicitly recommends generation/metageneration preconditions to prevent races where the resource changes between observation and mutation.
   Source: https://docs.cloud.google.com/storage/docs/request-preconditions
2. Amazon S3 conditional writes support `If-Match`: the operation proceeds only if the current ETag matches the caller's expected ETag; a changed object fails the precondition. Concurrent conditional writes therefore do not silently act on a stale observation.
   Source: https://docs.aws.amazon.com/AmazonS3/latest/userguide/conditional-writes.html

The transferable mechanism is not the storage API itself; it is **provider-owned compare-and-swap/fencing over the exact observed state**. A local database comparison alone is insufficient because the race occurs outside SQLite.

## Candidate protocol

Introduce a provider-side activation reservation/ticket with an epoch (fencing token):

1. `prepare_activation(expected_position, candidate_generation_id, request_id)` executes atomically at the provider.
2. It succeeds only if the provider is still at `expected_position` and no incompatible activation reservation exists.
3. On success it returns authenticated evidence containing at least:
   - provider identity;
   - candidate generation identity;
   - exact position;
   - monotonically increasing activation epoch/fencing token;
   - request/idempotency identity;
   - expiry or explicit abort semantics if the provider uses leases.
4. While the reservation is live, ordinary operations that could advance the candidate provider must either be rejected or require a strictly newer valid fencing token. This is the critical property that closes `read -> external advance -> SQL commit`.
5. The SQLite generation transition persists the exact activation evidence under `BEGIN IMMEDIATE`, after rechecking the durable shared-anchor tail equals the ticket position and normal LAB-083/LAB-086 authorization succeeds.
6. Provider activation is finalized idempotently with `commit_activation(ticket)`; retries with the same request/ticket must return the already-decided result.
7. After timeout/UNKNOWN, restart reconciles the durable SQL ticket against provider state:
   - same active epoch/generation/position => committed/activated;
   - reservation still pending => retry commit or abort according to the durable SQL decision;
   - provider advanced under a newer epoch => fail closed and require explicit reconciliation; never silently treat the stale generation as current.

## Why a second post-read is not sufficient

`read -> SQL transaction -> read again -> commit` merely moves the race window: the external provider may advance after the second read and before SQL commit. Holding `BEGIN IMMEDIATE` longer does not serialize the external service. The provider must expose a state-changing conditional primitive (reservation/CAS/lease/fencing), or the product contract must require externally enforced quiescence/exclusivity for the candidate generation.

## Quiescence-only alternative

A documented operator promise that the candidate provider is quiescent is weaker unless mechanically enforced. If LAB-090 chooses this route, acceptance should require an externally verifiable exclusive lease/fence, not prose-only operational discipline. Otherwise the existing race remains possible.

## Minimal executable mechanism check performed in this run

A local state-machine simulation modeled provider state `(position, activation_epoch, reservation, active_epoch)` and an atomic `prepare_activation(expected_position)` reservation.

Observed cases:

- start durable tail/provider position = 10; prepare succeeds; concurrent `external_advance()` is rejected as `fenced`; SQL decision + activation commit remains at position 10;
- timeout/UNKNOWN after activation commit reconciles successfully from durable `(epoch, position)` against provider `active_epoch` and current position;
- candidate provider already at 11 while durable tail is 10 causes `prepare_activation(10)` to fail `stale` before SQL mutation.

This is mechanism evidence, not execution of the repository branch or real provider implementation.

## Recommended LAB-090 implementation direction

Prefer a small provider activation interface rather than trying to extend SQLite locking semantics:

- authenticated `prepare_activation(expected_position, candidate_generation_id, request_id)`;
- idempotent `commit_activation(ticket)`;
- idempotent `abort_activation(ticket)` where needed;
- `read_activation(request_id/ticket_id)` for UNKNOWN/restart reconciliation;
- monotonic fencing epoch required on any provider operation that can advance state while activation handoff is in progress.

Persist the authenticated ticket/decision in SQL so recovery never depends on process memory.

## Required regression matrix before DONE

1. exact original race: prepare at N, attempted external advance, SQL rotate;
2. stale candidate already at N+1 before prepare;
3. timeout before SQL decision;
4. timeout after SQL commit but before provider activation acknowledgement;
5. provider activation succeeds but acknowledgement is lost;
6. restart with pending reservation;
7. duplicate commit/abort requests;
8. unrelated shared-anchor SQL activity while a candidate activation ticket exists;
9. competing activation attempts for the same provider/generation;
10. old/stale fencing token cannot advance the provider after a newer epoch exists.

## Decision

Advance LAB-090 using provider-owned conditional activation/fencing. Do not claim that `BEGIN IMMEDIATE`, a second authenticated read, or local generation-history checks close an external-service race. If the actual provider abstraction cannot supply CAS/reservation/fencing, explicitly downgrade the contract to mechanically enforced exclusive/quiescent handoff and test that enforcement.