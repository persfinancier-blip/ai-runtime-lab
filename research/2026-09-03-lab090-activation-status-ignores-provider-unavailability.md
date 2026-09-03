# LAB-090 audit — activation status remains readable while provider is unavailable

Date: 2026-09-03
Scope: draft PR #175 (`lab-090-provider-activation-fencing`, observed head `d9a381dd4607a928cd1315adef6431e239995bc1`)

## Finding

`FencedActivationProvider.activation_status()` does not check `self.available` before reading provider-owned `ActivationState`. This is semantically inconsistent with the same provider's activation mutations (`prepare_activation`, `commit_activation`, `release_activation`) and inherited provider I/O, all of which treat `available=False` as an unreachable external provider.

This matters because `SupportedHistoricalSharedAnchorLedger._recover_pending_activation()` and `_commit_or_reconcile_activation()` use `provider.activation_status(ticket)` as authoritative recovery/reconciliation evidence. During an outage, the coordinator can therefore learn `PREPARED`, `COMMITTED_FENCED`, `RELEASED`, or `ABSENT` from in-process state even though the modeled external provider is declared unreachable.

The previous LAB-090 finding about `abort_activation()` is one mutation-side instance of the same missing transport/reachability boundary. This status-read defect is separately important because even if abort is changed to fail while unavailable, restart/recovery would still be able to infer external reservation/commit state without contacting the provider.

## Concrete fail-closed scenario

1. A valid activation reaches durable SQLite `SQL_COMMITTED` (or a restart begins with such a row).
2. The external provider becomes unavailable (`available=False`).
3. Coordinator recovery calls `activation_status(ticket)`.
4. Current implementation returns a provider lifecycle status from local `ActivationState` instead of `ProviderUnavailable`.
5. Coordinator may consequently mark SQLite `COMMITTED`, attempt release, or classify the activation as prematurely released/lost based on evidence that could not have been obtained from the unreachable provider.

This does not necessarily create an immediate writer-authority bypass by itself because later mutation paths such as `commit_activation` / `release_activation` do enforce availability. It does, however, break the evidence model: recovery state is being accepted from an unreachable authority.

## Regression-first contract

Add exact-provider outage coverage, not a subclass/fake-provider test:

- create an authentic activation reservation and durable `SQL_COMMITTED` row;
- set the exact provider unavailable before restart/recovery;
- pre-fix: prove `activation_status()` still returns lifecycle state and the coordinator proceeds into reconciliation logic based on that state;
- post-fix: status/reconcile must fail closed with provider-unavailable semantics and must not mutate durable activation state based on unavailable-provider evidence;
- after provider availability returns, reconciliation may resume idempotently from the preserved durable ticket/state;
- include both `PREPARED` and `COMMITTED_FENCED` outage windows, plus already-durable-`COMMITTED`/release recovery.

## Design constraint

Do not solve this by treating the coordinator's in-process `ActivationState` object as a durable cache that is authoritative during provider outage. The LAB-090 contract models provider-owned external durability. If an offline/status cache is intentionally supported, it needs an explicit authenticated freshness/epoch contract and must not be confused with a live provider read.

Compose this with the existing unavailable-abort finding: outage semantics should be coherent across `activation_status`, `abort_activation`, `commit_activation`, `release_activation`, and the restart recovery state machine.

## Execution evidence

Source audit only. Direct Git transport was re-probed first in this run and failed before repository access with `Could not resolve host: github.com`; no exact-branch behavioral PASS is claimed.
