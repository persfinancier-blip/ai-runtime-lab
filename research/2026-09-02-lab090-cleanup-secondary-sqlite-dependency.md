# LAB-090 — cleanup depends on a second SQLite read before provider abort

Date: 2026-09-02

## Scope

Follow-up audit of draft PR #175 (`d9a381dd4607a928cd1315adef6431e239995bc1`). This strengthens existing LAB-090/#169; it is not a separate issue.

## Source finding

After a valid provider activation reservation is prepared, the fresh-rotation path enters the SQL transaction. If a later SQL step raises, the exception handler rolls back and then calls `_activation_row(activation_id=ticket.activation_id)` **before** deciding whether to call `provider.abort_activation(ticket)`.

`_activation_row()` opens a separate SQLite connection. Therefore cleanup of an external provider-side reservation depends on a second fallible SQLite operation succeeding after the primary SQL failure.

Failure schedule:

1. `prepare_activation()` returns a valid PREPARED ticket; provider fence is installed.
2. post-prepare SQL connection/transaction is acquired.
3. a SQL operation fails before durable activation commit; rollback succeeds.
4. exception handler calls `_activation_row(...)` to determine whether SQL actually committed.
5. that secondary connection/read raises (I/O/open/locking/fault injection).
6. `provider.abort_activation(ticket)` is never reached.
7. no durable activation row need exist, while provider remains PREPARED/fenced and restart has no coordinator record from which to reconcile it.

This is distinct from the already-recorded failure on the *first* post-prepare `_con()` acquisition: here the primary SQL path has already been entered and cleanup itself introduces another database dependency before provider cleanup.

## Executed mechanism probe

A minimal control-flow simulation matching the current exception-handler ordering was executed locally. The primary SQL failure was followed by an injected failure in the secondary activation-row lookup. Observed result:

- raised exception: secondary SQLite lookup failure;
- provider pending reservation remained installed;
- `abort_activation()` call count remained zero.

This is mechanism/control-flow evidence only; no exact PR-head behavioral PASS is claimed.

## Required regression contract

Add a pre-fix RED that:

- creates a valid newly-owned PREPARED reservation;
- enters the post-prepare SQL path;
- injects a primary SQL failure before durable activation commit;
- injects failure in the exception-handler `_activation_row()` lookup;
- proves current code strands provider state.

Post-fix cleanup must not require an additional SQLite read before releasing a reservation that this attempt can prove it newly owns. If ambiguity remains because `prepare_activation()` may idempotently return a pre-existing reservation, the provider protocol needs an explicit attempt/ownership result (for example `created_new` or a provenance token) so cleanup can be exact without risking abort of another attempt's reservation.

Any reconciliation read used to detect an unknown SQL commit outcome must itself have a failure policy that preserves a recoverable durable/provider state; it cannot be an unguarded prerequisite for the only provider abort path.

## Status

LAB-090 remains draft/pending exact RED/GREEN execution. No production code changed in this audit.
