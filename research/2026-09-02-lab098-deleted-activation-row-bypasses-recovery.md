# LAB-098 — deleted activation row bypasses provider-handoff recovery

Date: 2026-09-02

## Scope

Fallback source audit of draft PR #175 (`d9a381dd4607a928cd1315adef6431e239995bc1`) while LAB-086 remains blocked on byte-preserving publication tooling.

## Source finding

`SupportedHistoricalSharedAnchorLedger.__init__()` performs:

1. activation schema installation/verification;
2. runtime-vs-durable-head verification;
3. `_recover_pending_activation()`;
4. `_verify_activation_records()`.

Recovery asks for one activation row by the current durable generation. If no row exists, it returns immediately.

`_verify_activation_records()` then selects only rows that currently exist in `provider_generation_activations` and validates each returned row. It does not prove that every non-bootstrap provider-generation transition that requires LAB-090 activation has a corresponding activation row.

Therefore deletion of an activation row is not itself detected.

## Concrete failure mode

Start from a valid provider rotation to g2 where durable provider-generation history/head points at g2 and the activation row for g2 is `SQL_COMMITTED` (or `COMMITTED`). Delete only the g2 row from `provider_generation_activations`, leaving provider history/head and activation schema intact.

On restart with runtime provider g2:

- runtime/head matching can succeed;
- `_recover_pending_activation()` finds no row and performs no reconciliation;
- `_verify_activation_records()` receives no g2 row to validate and therefore does not reject the omission.

For an unresolved `SQL_COMMITTED` handoff, this is materially worse than ordinary evidence loss: the deleted row also removes the trigger predicate that blocks new shared-anchor intents, while the external provider may still hold a PREPARED or COMMITTED_FENCED reservation. The coordinator has lost the durable ticket needed to reconcile that fence.

## Isolated SQLite semantics probe

A file-backed SQLite probe reproduced the exact omission shape used by the current queries:

- before deletion: g2 activation row exists with `SQL_COMMITTED`;
- durable generation head remains g2 after deleting only the activation row;
- current-generation activation lookup returns `None`;
- the verification SELECT over activation rows returns `[]`.

This probe demonstrates the relational/query condition only; it is not claimed as an exact PR #175 behavioral test because exact branch checkout/execution is unavailable in this runtime.

## Required regression-first contract

1. Build valid g1 -> g2 provider-generation history using LAB-090 activation.
2. Preserve durable provider-generation history/head at g2.
3. Delete only g2's activation row.
4. Restart with runtime provider g2.
5. Pre-fix: demonstrate startup accepts the missing row or otherwise reaches recovery/verification without detecting the omission.
6. Post-fix: fail closed before any provider or SQLite mutation and leave the tampered state unchanged.

Required variants:

- deleted current `SQL_COMMITTED` row while provider remains PREPARED;
- deleted current `SQL_COMMITTED` row while provider is COMMITTED_FENCED;
- deleted historical `COMMITTED` activation row for an earlier non-bootstrap generation;
- deletion must not be normalized by recreating an activation row from current runtime state.

## Design constraint

Presence must be proven from authenticated provider-generation transition history, not by treating the activation table as self-authoritative. For every generation transition governed by LAB-090, verification should derive the expected activation identity from authenticated generation history plus the committed transition context and require exactly one matching activation record. A missing record is evidence loss/tamper, not a fresh state.

This should compose with LAB-092 schema-installation provenance and LAB-097 provider-history deletion provenance rather than adding an unrelated ad-hoc marker.

## Distinction from existing issues

- LAB-090/#169 currently covers ordering, external activation fencing/recovery, and stranded prepare reservations.
- LAB-092/#176 covers deletion/recreation of the activation schema itself.
- LAB-097/#182 covers provider-generation history deletion/rebootstrap.
- LAB-098 concerns deletion of activation *records* while authenticated provider-generation history/head survives and still proves that a handoff occurred.

## Status

READY — source-proved and SQLite query semantics reproduced; exact repository RED/GREEN pending. Does not supersede LAB-086 priority.