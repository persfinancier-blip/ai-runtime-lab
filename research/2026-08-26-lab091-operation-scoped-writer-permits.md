# LAB-091 — transaction-wide boolean writer authority is too broad

## Finding

The first LAB-091 real integration protects mutable shared-anchor SQL with a connection-local `lab091_writer_authorized()` boolean. That is useful against ordinary raw DML from an unauthorized connection, but it is not yet an *exact transition* capability.

Inside a legitimate `_authorized_txn()` the current triggers accept classes of writes wider than the operation being executed. A focused SQLite counterexample using the published trigger predicates demonstrated:

- unauthorized `UPDATE shared_anchor_meta` is blocked;
- once `lab091_writer_authorized()==1`, `reserved_position` can be changed directly from `0` to `999`;
- an authorized watermark update can jump directly from `1` to `999`.

The production methods currently issue fixed/CAS SQL and do not intentionally perform those jumps. The problem is authority scope: any bug, alternate internal write path, or re-entrant SQL executed while the boolean is true inherits the entire transaction-wide write class.

## Security/correctness implication

LAB-091's intended claim is stronger than "the broker connection may mutate these tables." It is to constrain the broker-owned writable handle to the exact DML transition that was already authorized by the higher-level operation.

A boolean transaction permit does not meet that claim. It is defense-in-depth, but it is too coarse to be the final supported writer boundary.

## Required correction

Replace the transaction-wide boolean capability with an operation-scoped permit. The connection-local state should bind, at minimum:

- operation kind (`intent_insert`, `meta_advance`, `receipt_insert`, `intent_confirm`, `watermark_set`);
- exact identity/key (`intent_id`, `request_id`, `component_id`, singleton);
- exact expected old/new values or a canonical digest of the row transition.

SQLite trigger predicates should call a connection-local function with `OLD`/`NEW` fields and succeed only when they match the active one-shot permit. The permit must be installed immediately before the single intended DML statement and cleared immediately afterward, still inside the enclosing `BEGIN IMMEDIATE` transaction. External provider calls remain outside any SQL permit.

A permit must not be reusable for a second statement, a different key, or a different new value. Rollback/exception paths must clear it.

## Regression requirement

The final integration must prove that even while the broker transaction is active:

1. a meta jump to an unpermitted tail is rejected;
2. a watermark jump to an unpermitted position is rejected;
3. a receipt for another request is rejected;
4. a second DML using an already consumed permit is rejected;
5. the exact intended DML succeeds once;
6. exception/rollback clears both transaction and operation permit state.

## Boundary

This remains subordinate to LAB-087. A same-privilege connection that can redefine UDFs/drop triggers is outside LAB-091's standalone claim; the broker/process/filesystem boundary must ensure workers cannot obtain an unrestricted writable handle.
