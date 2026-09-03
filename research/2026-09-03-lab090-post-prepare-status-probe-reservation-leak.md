# LAB-090 audit — post-prepare status probe can strand provider reservation

Date: 2026-09-03
Scope: draft PR #175 (`LAB-090: provider-owned activation fencing primitive`)

## Observation

`SupportedHistoricalSharedAnchorLedger.rotate_provider()` successfully calls `provider.prepare_activation(...)`, validates the returned `ActivationTicket`, and then calls:

```python
if provider.activation_status(ticket) != "PREPARED":
    raise HistoricalVerificationError(...)
```

This status probe occurs **before** the later SQL `q = self._con()` / `try` block whose exception path conditionally calls `provider.abort_activation(ticket)`.

Therefore any exception from the post-prepare status probe leaves the authentic provider-owned `pending` reservation live with no durable `provider_generation_activations` row and no coordinator cleanup attempt.

Concrete schedules include:

1. `prepare_activation()` succeeds and installs `ActivationState.pending`.
2. Provider becomes unavailable before `activation_status(ticket)` (once LAB-090 outage semantics are corrected so status cannot fabricate live evidence while unavailable), or `activation_status()` otherwise raises.
3. `rotate_provider()` exits before entering the cleanup scope.
4. No SQL activation row exists, but provider-side fencing remains live. Restart has no durable activation row from which to discover/reconcile this orphan.

This is the same structural class as the already-recorded post-prepare connection-open leak, but at an **earlier and independent call site**. Fixing only `_con()` cleanup does not cover it.

## Why this matters

The intended LAB-090 contract is that provider prepare is an external linearization/fencing point. Once prepare succeeds, every subsequent pre-durability failure must either:

- prove and perform safe ownership-bound cancellation, or
- durably preserve enough evidence for recovery/reconciliation.

A cleanup scope that starts only after the status probe violates that invariant.

The recently recorded provider-unavailability defect makes this especially important: once `activation_status()` correctly refuses authoritative evidence while the provider is unreachable, this exact schedule becomes a deterministic orphan-reservation path unless cleanup/recovery ownership is redesigned.

## Required regression

Add a RED test at the supported coordinator surface:

- exact valid candidate/new runtime;
- `prepare_activation()` returns a genuine PREPARED ticket and installs provider `pending`;
- inject a failure specifically on the first post-prepare `activation_status(ticket)` call;
- assert no provider-generation history/head mutation and no durable activation row;
- pre-fix: provider reservation remains stranded;
- post-fix: no untracked live reservation remains.

The post-fix assertion must not be satisfied by blindly aborting an untrusted ticket. Cleanup must be tied to a provider-owned reservation/ownership handle that the coordinator can trust, or equivalent durable recovery evidence must exist before any fallible post-prepare operation.

## Design implication

Treat successful `prepare_activation()` as entering a resource-ownership scope immediately. All fallible operations after that point — ticket/status validation, connection acquisition, SQL begin/checks, history rotation — need one coherent cleanup/recovery discipline. The scope boundary should not begin only after SQLite connection acquisition.

## Validation status

This run re-fetched the exact PR #175 patches for `activation.py` and `supported.py` and inspected the call ordering. Direct Git transport was also reprobed and failed before repository access with `Could not resolve host: github.com`; therefore no exact branch behavioral execution is claimed in this note.
