# LAB-090 overlapping provider-rotation audit

Date: 2026-08-30

## Scope

Narrow source audit of draft PR #175 at head `9e53c6ed0340c8a3c77c22b23eb7c0340240294e`, following the durable handoff instruction to look only for a concretely reproducible restart/concurrency defect while exact-head execution is blocked by direct git DNS failure.

## Finding

The current LAB-090 protection blocks new `shared_anchor_intents` while a row in `provider_generation_activations` remains `SQL_COMMITTED`, but `rotate_provider()` itself does not reject a second provider-generation rotation while such an unresolved activation exists.

The relevant ordering in `SupportedHistoricalSharedAnchorLedger.rotate_provider()` is:

1. candidate provider `prepare_activation()` fences its own exact position;
2. coordinator opens `BEGIN IMMEDIATE`;
3. coordinator checks only unresolved `shared_anchor_intents` and current shared-anchor tail;
4. coordinator inserts a new `SQL_COMMITTED` activation row and rotates provider generation history/head;
5. after SQL commit it performs provider commit/reconcile and durable acknowledgement.

Because step 3 does not check for an existing unresolved activation, a distinct second candidate can pass through the same SQL critical section after the first rotation has committed generation history/head but before the first provider activation is acknowledged. The intent trigger does not help because it guards only `INSERT ON shared_anchor_intents`.

## Concrete schedule

Starting at generation G1 / tail N:

- rotation A prepares provider G2 at N;
- rotation A commits SQLite generation head G2 plus activation row A=`SQL_COMMITTED`;
- before A completes provider commit/acknowledgement, rotation B prepares a distinct provider G3 at N;
- rotation B obtains `BEGIN IMMEDIATE`; there is no PREPARED anchor intent and the tail still equals N;
- without an activation-table exclusion check, B can insert activation row B=`SQL_COMMITTED` and advance durable generation head to G3;
- activation A is now an older unresolved `SQL_COMMITTED` record. The constructor recovery path only looks up the activation row for the current durable generation, so it cannot repair A by normal restart reconciliation.

This is a correctness/availability protocol defect. It is not an authority escalation, but it violates the intended invariant that provider-generation activation is fully resolved before the next generation handoff becomes durable.

## Minimal correction

Inside the same `BEGIN IMMEDIATE` transaction used for provider rotation, before inserting the new activation row, count unresolved activation rows:

```sql
SELECT COUNT(*) FROM provider_generation_activations WHERE status='SQL_COMMITTED'
```

If non-zero, raise `PendingRotationBlocked("previous provider activation commit is unresolved")`. Because the check and new activation insert occur under the same SQLite write transaction, concurrent rotations serialize: after the first commits `SQL_COMMITTED`, the second observes it and aborts its provider reservation through the existing exception path.

Add a regression that forces rotation A to stop after SQL commit (for example provider unavailable on first activation commit), then attempts rotation B on the still-live coordinator. Expected behavior after the fix: B raises `PendingRotationBlocked`, B's provider reservation is aborted, durable generation remains G2, and only activation A remains unresolved.

## Runtime observation

Direct git transport was probed again in this run and failed before repository-code execution with `Could not resolve host: github.com`. Therefore no exact-head executable PASS/RED is claimed here. GitHub connector reads were sufficient to audit the exact PR-head source.

## Decision

Keep PR #175 draft. This defect should be fixed before widening the executable gate or considering readiness. The correction is intentionally narrow and does not expand the activation protocol state machine.
