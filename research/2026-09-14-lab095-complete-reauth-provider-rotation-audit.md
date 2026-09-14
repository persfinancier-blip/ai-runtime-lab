# LAB-095 COMPLETE reauthentication across provider rotation — audit

Date: 2026-09-14
Issue: #180
PR: #187 (`lab-095-database-identity-red-intent`)

## Question

The LAB-095 COMPLETE-state fix removed the local early return and now requires every repeated `migrate_database_identity()` call to drive the existing identity intent through `ledger.execute()` before trusting the locally stored logical database identity digest.

A fresh audit asked whether that rule becomes invalid after a legitimate provider-generation rotation. Plain `SharedAnchorLedger._reauthenticate()` requires the durable entry's `(provider_id, provider_generation)` to equal the *current* runtime provider generation. Therefore an identity intent anchored at generation 1 would no longer reauthenticate through the plain ledger after a legitimate move to generation 2.

## Source audit

`experiments/shared_anchor_intent_ledger/protocol.py`:

- `execute()` calls `_reauthenticate(entry)` when an entry is already CONFIRMED.
- the plain `_reauthenticate()` requires the entry provider generation to equal the current runtime provider generation.
- `_row_entry()` separately verifies provider-generation shape, exact predecessor/position adjacency, deterministic request identity, status, and receipt shape.

`experiments/provider_generation_history/supported.py` deliberately overrides this behavior for the supported historical surface:

1. `SupportedHistoricalSharedAnchorLedger._reauthenticate()` first calls `_stored_receipt(entry)`.
2. `_stored_receipt()` loads the historical receipt by the exact request id and verifies its provider id, generation, position, and request id against the ledger entry.
3. When that stored historical evidence exists, `_reauthenticate()` returns its stable binding without requiring the historical entry's generation to equal the current provider generation.
4. Only when no historical receipt exists does the implementation require the entry to belong to the current durable generation, authenticate it against the live provider, and then persist the resulting `HistoricalReceipt`.

Therefore the supported historical path has exactly the mechanism needed by the LAB-095 COMPLETE-state rule: the original identity intent can remain externally authenticated after later legitimate provider rotations because its first exact signed provider observation is retained as historical evidence.

## Decision

Do **not** revert or weaken the COMPLETE-state external reauthentication fix.

For the supported LAB-081/LAB-090/LAB-092 composition, repeated LAB-095 identity verification after provider rotation is expected to succeed through persisted historical-receipt evidence rather than through the plain current-generation-only reauthentication rule.

The generic migration helpers are intentionally structurally duck-typed for focused tests, but plain `SharedAnchorLedger` after a provider rotation is not sufficient authority for this cross-generation property. Integration acceptance must therefore be demonstrated on `SupportedHistoricalSharedAnchorLedger`, not inferred from the fake migration ledger.

## Required retained gate

Before LAB-095 integration, add/execute a downstream cross-generation regression on the exact supported closure:

1. construct the supported historical ledger/history on generation 1;
2. install and fully CONFIRM LAB-095 logical database identity;
3. verify the identity intent has persisted historical receipt evidence;
4. legitimately rotate provider authority to generation 2 through the supported coordinator path;
5. invoke repeated identity migration/startup verification;
6. require the original logical database identity digest to remain unchanged and require reauthentication to use the stored generation-1 receipt evidence;
7. corrupt/remove that historical receipt and require fail-closed behavior rather than silently trusting local COMPLETE custody.

This regression belongs with the already-required LAB-080/LAB-081/LAB-090/LAB-092 downstream gates.

## Runtime observations

- LAB-086 materialization was probed first this run; shell GitHub DNS still failed with `Could not resolve host: github.com`, exit 128. No LAB-086 execution PASS is claimed.
- GitHub connector reads remain available.
- PR #187 REST state was rechecked directly and is `mergeable=true`, `rebaseable=true`, `mergeable_state=clean`; one higher-level connector summary transiently reported `mergeable=false`, so the direct REST result is the retained observation for this run.
- No full LAB-095 exact-closure GREEN is claimed in this audit.
