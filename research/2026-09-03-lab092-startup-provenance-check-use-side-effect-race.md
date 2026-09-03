# LAB-092 — startup provenance check/use race can mutate before fail-closed

Date: 2026-09-03

## Scope

Fallback source audit of draft PR #177 (`activation_schema_provenance.py`) while LAB-086 exact publication remains blocked by the lack of a supported byte-preserving connector-response -> machine patch/hash path.

## Observation

`ProvenancedHistoricalSharedAnchorLedger.__init__()` first calls `_classify(path)` and accepts only `COMPLETE`. It then builds an unbound base `SupportedHistoricalSharedAnchorLedger` via `_reservation_surface(...)`, performs provider-history and activation-integrity checks, and finally calls `confirmation.execute(_completion_intent())` before `super().__init__()` and before `_bind_live_provider_history_provenance(self)`.

The confirmation object is intentionally the LAB-090 base surface, not the provenance-bound LAB-092 surface. Therefore there is no second provenance check tied to the external/durable effects of `execute()`.

Inherited `SharedAnchorLedger.execute()` is consequential even for this startup confirmation path:

- for a CONFIRMED entry it externally re-authenticates the request;
- LAB-090 overrides `_reauthenticate()` and, when no historical receipt exists yet, authenticates the provider observation and persists it through `provider_history.store_receipt(...)`;
- for a marker that becomes absent after the initial `_classify()`, inherited `reserve()` may create a replacement PREPARED entry, then `execute()` can call `catch_up_one()`, re-authenticate, and confirm it.

## Concrete race

1. DB starts in genuine LAB-092 `COMPLETE` state.
2. Constructor executes `_classify(path) == COMPLETE`.
3. A second SQLite writer deletes or changes the confirmed migration marker or activation DDL before `confirmation.execute(...)`.
4. Constructor continues using the unbound LAB-090 confirmation object.
5. Depending on the mutation, `execute()` can perform provider I/O and/or write a historical receipt / replacement marker before later construction re-checks eventually fail closed.

For marker deletion specifically, base `reserve()` does not re-run LAB-092 provenance classification. It can reserve a new marker at the then-current tail and `catch_up_one()` may advance the external anchor. Later `super().__init__()` / durable verification can still reject the corrupted local ledger, but the security property required here is stronger: provenance loss must be detected **before** any new external or durable authority mutation.

This is distinct from the already-recorded post-construction TOCTOU: it exists during constructor/restart confirmation before the live provider-history handle is provenance-bound.

## Required regression

Add a deterministic startup race test:

1. create a valid COMPLETE migrated DB;
2. start `ProvenancedHistoricalSharedAnchorLedger(...)` and pause after the first successful `_classify()` / authority checks but before `confirmation.execute(_completion_intent())`;
3. from a second SQLite connection delete the confirmed migration marker (and separately test activation DDL deletion/mismatch);
4. resume constructor;
5. require failure before any of the following change:
   - external provider position;
   - provider request-result set;
   - `historical_provider_receipts`;
   - `shared_anchor_intents` / `shared_anchor_meta`;
   - component watermarks or provider-generation history.

A second test should cover the narrower CONFIRMED-marker/no-receipt case and prove startup does not persist a receipt after provenance becomes incomplete.

## Fix constraint

Do not solve this with another free-standing `_classify()` immediately before `execute()`; that only narrows the race. Startup confirmation must be bound to the same serialization/authority boundary as the consequential operation. Acceptable directions include a provenance-aware confirmation primitive that acquires the SQLite writer reservation, re-validates exact DDL+marker state at that boundary, and guarantees no external/durable mutation occurs after provenance loss.

## Status

Strengthens LAB-092 / #176. No duplicate issue created. No behavioral PASS claimed because exact source execution is unavailable in this run.
