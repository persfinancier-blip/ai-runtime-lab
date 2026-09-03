# LAB-090 pre-SQL external commit can strand a committed provider fence

Date: 2026-09-03
Issue: #169 / LAB-090
PR inspected: #175, head `d9a381dd4607a928cd1315adef6431e239995bc1`

## Finding

`SupportedHistoricalSharedAnchorLedger.rotate_provider()` prepares an external activation ticket before entering the authoritative SQLite write transaction. The ticket is provider-owned and the activation identifier is deterministic from the target generation and expected shared-anchor position.

The provider API is independently callable on the same provider capability. `FencedActivationProvider.prepare_activation()` is idempotent for the same pending activation and returns the same ticket; `commit_activation()` then moves that ticket into `committed` while intentionally retaining `ActivationState.pending`, producing `COMMITTED_FENCED`.

If another actor commits the exact prepared ticket before the coordinator's SQLite transaction commits, and the coordinator's SQL path subsequently fails/rolls back, the exception handler observes no durable activation row and calls `provider.abort_activation(ticket)`.

However, `abort_activation()` explicitly treats both `COMMITTED_FENCED` and `RELEASED` as terminal and returns the status without clearing `pending`. The coordinator then re-raises the SQL exception. Result: the external provider remains fenced by a committed activation, but SQLite contains no `provider_generation_activations` row and the durable provider-generation head was not advanced.

On restart, `_recover_pending_activation()` selects activation state only from the durable row for the current generation. With no row, there is no supported reconciliation handle for the stranded provider fence. External increments remain blocked by the provider-owned pending ticket.

## Concrete schedule

1. Durable generation is g1, shared-anchor tail is P.
2. Coordinator starts g1 -> g2 rotation and calls `prepare_activation(P, deterministic_id)`; provider returns ticket T and installs `pending=T`.
3. A concurrent holder of the same provider capability obtains/reuses exact T and calls `commit_activation(T)`; provider state becomes `committed[T.id]=T` plus `pending=T`, status `COMMITTED_FENCED`.
4. Coordinator enters its SQLite rotation transaction, but any fallible SQL step fails before commit (for example a transition/history conflict).
5. SQLite rolls back; there is no durable activation row for T and g1 remains current.
6. Exception cleanup calls `abort_activation(T)`.
7. `abort_activation()` sees `COMMITTED_FENCED` and returns it without clearing `pending`.
8. Coordinator re-raises the original failure.
9. Restart has no activation row from which to recover T; provider increments remain fenced.

## Why this is distinct

This is not the already-recorded post-prepare status-probe or SQLite-connection leak: cleanup is reached here, but cleanup cannot undo the provider state because the reservation was concurrently committed.

It is also not merely the unavailable-abort defect: the provider can be fully reachable and `abort_activation()` still cannot cancel a committed fence.

It composes with LAB-093/LAB-100 capability-authority findings because the same raw provider capability can be held outside the coordinator. Even if the eventual authority design narrows direct lifecycle access, the provider/coordinator protocol should define what happens if provider commitment exists without the matching SQL commit rather than assuming that state is impossible.

## Required regression-first contract

Add an exact-provider concurrency regression:

- prepare T through `rotate_provider()` up to the post-prepare/pre-SQL window;
- concurrently commit exact T through the same provider authority before SQLite commit;
- force the coordinator SQL transaction to fail and roll back;
- pre-fix: demonstrate provider status remains `COMMITTED_FENCED`, no exact durable activation row exists, durable generation remains old, and increments remain fenced;
- post-fix: the system must retain a trusted durable/recoverable ownership record or otherwise reconcile the provider commitment without silently releasing an unacknowledged fence or losing the durable handle.

Restart coverage is mandatory: after the failure, reconstruction must fail closed with recoverable evidence and must not normalize the provider into ordinary writable operation until the exact ticket fate is durably resolved.

## Design constraint

Do not "fix" this by making `abort_activation()` blindly clear `COMMITTED_FENCED`. Provider commitment is intentionally stronger than PREPARED and may represent an externally linearized handoff. The coordinator needs an ownership/recovery protocol that can durably represent a provider commitment whose SQL generation transaction did not commit, or an authority boundary that makes such pre-SQL external commitment impossible and verifiably enforces that fact.

This regression belongs with LAB-090/#169. No duplicate issue is needed.

## Execution evidence

- Exact PR #175 source was read from GitHub at head `d9a381dd4607a928cd1315adef6431e239995bc1`.
- Direct Git transport was probed in this run and failed before repository access with `Could not resolve host: github.com`.
- No exact branch behavioral PASS/RED execution is claimed; this is a source-level concurrency proof pending executable regression.
