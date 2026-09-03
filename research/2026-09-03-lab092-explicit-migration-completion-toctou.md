# LAB-092 explicit migration completion TOCTOU

Date: 2026-09-03

## Scope

Fallback source audit of draft PR #177 (`lab-092-activation-schema-provenance`, observed head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`) while LAB-086 exact publication remains blocked by the lack of a supported byte-preserving connector-response -> machine patch/hash handoff.

This note strengthens existing issue #176; it is not a new issue.

## Finding

`ProvenancedHistoricalSharedAnchorLedger.migrate_activation_schema_v1()` contains a consequential check/use window after the migration has atomically committed exact activation DDL plus a deterministic PREPARED completion marker, but before that marker is externally authenticated and changed to CONFIRMED.

Current sequence in `experiments/provider_generation_history/activation_schema_provenance.py`:

1. `_classify(path)` accepts a recoverable legacy/unmarked/PREPARED state.
2. `_install_and_reserve_prepared(...)` runs under `BEGIN IMMEDIATE`, verifies provider-generation authority, installs/verifies exact activation table+trigger if needed, inserts the deterministic PREPARED migration intent, advances `shared_anchor_meta.reserved_position`, rechecks DDL + PREPARED, and commits.
3. The method then releases that transaction/connection.
4. A fresh, **unbound** `_reservation_surface(...)` is created.
5. `_verify_confirmation_authority(...)` and `_verify_confirmation_activation_integrity(...)` are read-only checks.
6. `confirmation.execute(_completion_intent())` is called.
7. Only after that returns CONFIRMED does the method construct `cls(path, ...)`, whose startup classifier would notice that provenance/DDL no longer match.

The inherited shared-anchor `execute()` path does not re-check LAB-092 activation-schema provenance at the consequential mutation boundary. For a PREPARED entry it may:

- call `attested.catch_up_one(...)`, advancing the external monotonic anchor;
- reconcile the exact request;
- on the LAB-081 historical path, store signed historical receipt evidence;
- change the migration row from PREPARED to CONFIRMED in SQLite.

Therefore this schedule is possible:

1. explicit migration commits exact DDL + PREPARED marker;
2. a second same-privilege SQLite actor deletes or changes the activation trigger/table after `_install_and_reserve_prepared()` returns;
3. the unbound `confirmation.execute()` advances/reconciles external authority and confirms the migration completion intent without proving the activation DDL is still exact at that serialization boundary;
4. the subsequent `cls(...)` fails closed because `_classify()` now sees CONFIRMED provenance with missing/mismatched DDL.

The eventual startup failure is too late. The authenticated completion marker and/or external provider position may already assert successful migration completion for a database whose activation schema was not complete at confirmation time.

## Why this is distinct from the retained LAB-092 regressions

The retained constructor/restart TOCTOU starts from an already COMPLETE local state and races between startup classification and `confirmation.execute()`.

The retained post-construction TOCTOU races ordinary live operations after a successful provenance check.

This finding is the **explicit migration transition itself**: `DDL+PREPARED commit -> externally authenticated CONFIRMED completion`. It can manufacture a false CONFIRMED provenance claim during first migration/recovery, before a valid LAB-092 object has ever been constructed.

## Required regression

Add a deterministic RED test around `migrate_activation_schema_v1()`:

1. start from legitimate legacy state;
2. pause immediately after `_install_and_reserve_prepared()` has committed exact DDL + PREPARED marker but before `confirmation.execute()` performs provider mutation;
3. from a second SQLite connection delete the activation trigger (and separately test table/definition mutation where practical);
4. resume migration;
5. require fail-closed **before** any new external provider position/request-result, historical receipt, CONFIRMED migration marker, shared-anchor durable advancement beyond the PREPARED reservation, watermark, or provider-history mutation;
6. prove the damaged DDL is not auto-repaired.

A second variant should pause after the read-only confirmation checks but before the first consequential action inside `execute()` to ensure another pre-check cannot merely move the TOCTOU window.

## Fix constraint

Do not fix this by adding one more unsynchronized `_classify()` immediately before `confirmation.execute()`. That only narrows/moves the race.

The activation-schema completion predicate must be bound to the same serialization/authority boundary that performs the consequential provider/receipt/CONFIRMED mutation, or the migration protocol must use an equivalent mechanism that makes loss of exact DDL impossible to race with completion authentication.

The final invariant is: a LAB-092 CONFIRMED completion marker may be produced only if exact activation DDL is still authoritative at the completion linearization boundary.

## Validation status

This is a source-audit finding only. Exact checkout/source execution remains unavailable in this run, so no behavioral RED/PASS is claimed.
