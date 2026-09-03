# LAB-092 — explicit migration trusts an unverified shared-anchor tail before external mutation

Date: 2026-09-03

## Scope

Fallback source audit of draft PR #177 (`lab-092-activation-schema-provenance`) while LAB-086 exact publication remains blocked by unavailable direct git/network transport.

No exact PR behavioral execution is claimed in this run.

## Finding

`_install_and_reserve_prepared()` manually constructs the LAB-092 migration PREPARED entry inside `shared_anchor_intents` before any `SupportedSharedAnchorLedger.verify_durable()` pass authenticates the shared-ledger tail/continuity invariants.

The function verifies LAB-081 provider-generation history (`provider_history._verify_durable_locked`) and the activation DDL/marker state, but it does not verify the inherited LAB-080 durable ledger invariants before trusting `shared_anchor_meta.reserved_position` and appending the migration entry.

The inherited LAB-080 verifier is materially stronger: it requires exactly one valid `shared_anchor_meta` row, `len(shared_anchor_intents) == reserved_position`, contiguous positions/predecessors, at most one PREPARED row at the tail, provider-generation consistency, and valid component watermarks.

After `_install_and_reserve_prepared()` commits, LAB-092 builds another uninitialized `_reservation_surface()` and calls `confirmation.execute(_completion_intent())`. Because the migration row already exists, inherited `reserve()` returns that row without running the constructor-time durable verification. `execute()` may therefore call `catch_up_one()` and reauthenticate/confirm the marker against an externally mutated anchor before `SupportedHistoricalSharedAnchorLedger.__init__()` eventually runs the inherited durable verification.

So a malformed/tampered shared-anchor tail can be used as the basis for a consequential provider advance and migration completion attempt before the durable ledger is authenticated.

## Concrete adversarial state

A deterministic regression can start from an otherwise valid legacy database and, before explicit migration, tamper only LAB-080 durable-tail metadata/history, for example:

- make `shared_anchor_meta.reserved_position` disagree with the number/continuity of `shared_anchor_intents`; or
- create a gap/non-contiguous predecessor chain while retaining a query-compatible tail value.

Keep provider-generation history, activation-schema absence, and the runtime provider otherwise valid.

Pre-fix path:

1. `_classify()` accepts `LEGACY_ABSENT` because it does not authenticate LAB-080 durable history.
2. `_install_and_reserve_prepared()` reads the unverified `reserved_position`, inserts a new migration PREPARED row, advances `shared_anchor_meta`, and commits.
3. `confirmation.execute()` can perform provider-side `catch_up_one()` / request-result mutation and may confirm the migration receipt.
4. Only later does normal supported-ledger construction execute the inherited durable verification and discover the malformed history.

That is fail-closed too late: external authority may already have advanced and local migration provenance may already have changed.

## Why this is distinct from retained LAB-092 findings

This is not the already-recorded schema-object/marker TOCTOU: no concurrent mutation is required.

It is not the provenance-carrier schema-authentication gap: the carrier table may have the exact schema.

It is not the pre-seedable generic migration-marker confused deputy: no historical caller needs to mint the marker.

The missing predicate here is inherited LAB-080 durable-ledger authentication before LAB-092 trusts its tail to create or externally confirm migration provenance.

## Regression-first contract

Add deterministic cases for malformed LAB-080 durable state before `migrate_activation_schema_v1()`:

1. `reserved_position`/row-count mismatch;
2. non-contiguous position/predecessor history;
3. invalid or non-tail PREPARED history where practical;
4. invalid component watermark where practical.

For every case, post-fix behavior must fail closed before:

- activation DDL installation;
- insertion/update of the migration marker;
- `shared_anchor_meta` tail mutation;
- provider `catch_up_one()` / request-result mutation;
- historical receipt mutation;
- component watermark mutation.

The migration path should reuse one authenticated inherited durable-ledger predicate at the same serialization/authority boundary rather than reimplementing only selected LAB-080 checks.

## Design constraint

Do not solve this by merely constructing `SupportedHistoricalSharedAnchorLedger` before migration, because ordinary LAB-090 construction may initialize/mutate activation schema and perform recovery side effects that LAB-092 is explicitly trying to gate. The safe design needs a read-only/full LAB-080 durable verification primitive (plus provider-history/activation checks as required) that can be invoked before migration mutation, and must remain bound to the transaction/serialization boundary that consumes the verified tail.

## Runtime evidence

Direct git transport was re-probed in this run and failed before repository execution with:

`Could not resolve host: github.com`

Connector source reads succeeded; no exact branch test PASS is claimed.
