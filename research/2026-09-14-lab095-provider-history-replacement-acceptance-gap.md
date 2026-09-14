# LAB-095 provider-history replacement acceptance gap

Date: 2026-09-14

## Context

LAB-086 remained the mandatory first executable probe. Direct `git clone` from the executable runtime again failed before repository execution with `Could not resolve host: github.com` (exit 128). No LAB-086 behavioral PASS is claimed.

LAB-095/#180 is therefore the permitted fallback. PR #187 currently makes `ledger.path` and the existing `ledger.provider_history.path` construction-bound through `CanonicalDatabaseBinding`.

## Finding

The current LAB-095 patch does **not** yet satisfy the stronger acceptance criterion that the composed supported ledger/history authority cannot diverge between DB A and DB B.

`SupportedHistoricalSharedAnchorLedger.__init__()` still assigns the history strategy to ordinary public mutable attribute `self.provider_history`. There is no property/slot guard preventing a later assignment such as:

```python
ledger.provider_history = CoordinatorOnlyProviderHistory(db_b, bootstrap)
```

The new object is itself correctly path-bound to DB B, but replacing the whole strategy object bypasses the path-rebinding protection on the original DB-A history object.

This matters because the inherited LAB-081 integration dispatches security-relevant operations through `self.provider_history` after construction:

- `_require_runtime_matches_durable_head()` calls `provider_history.current()`;
- `_runtime_matches_entry()` calls `provider_history.current()`;
- `_reauthenticate()` uses `current()`, `load_receipt()` and `store_receipt()`;
- `reserve()` and `rotate_provider()` call `_current_locked(q)` / `_rotate_locked(q)` using the ledger's already-open SQLite connection;
- `verify_durable()` calls `_verify_durable_locked(q)` and `_load_receipt_locked(q)` using the ledger connection.

Therefore replacement creates a split-authority graph: ordinary history methods reopen the replacement object's DB-B path, while locked helpers consume the DB-A connection supplied by the ledger. The behavior can depend on which history method is reached, even though neither individual object's `path` attribute was rebound.

## Relationship to LAB-096

This is the concrete overlap with LAB-096/#181, which already tracks immutability of the provider-history strategy/capability slot. It is not necessary to create a duplicate issue.

However, for LAB-095 completion this is not merely optional follow-up work: #180 explicitly requires preventing ledger/history DB divergence in supported composition. Path immutability alone cannot prove that property while the history strategy object remains replaceable.

## Decision

Treat LAB-096's construction-bound provider-history strategy as a prerequisite/composed slice for closing LAB-095 acceptance.

The eventual implementation should preserve one construction-bound authority graph:

1. ledger canonical DB path is immutable;
2. provider-history canonical DB path is immutable and equal to the ledger path at construction;
3. the provider-history strategy object itself cannot be rebound through the supported surface;
4. all internal history operations use that same private strategy object;
5. any public introspection is read-only / least-capability and does not expose a replaceable authority slot.

Do not attempt to solve this only by checking path equality inside LAB-095 migration helpers: normal reserve/execute/rotate/verify paths also consume the strategy object after construction.

## Validation status

This is connector-side source/security analysis, not a behavioral PASS. The exact no-stub LAB-095 executable gate remains pending because no supported byte-preserving connector-to-filesystem materialization path is exposed in this run.

PR #187 must remain draft.
