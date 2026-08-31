# LAB-092 — DDL-before-provenance ordering correction

Date: 2026-08-31
Issue: #176

## Finding

The previously recorded idea "confirm one authenticated migration intent, then create the LAB-090 activation table/trigger" is insufficient for deletion detection.

If the authenticated marker is confirmed before DDL, then the durable state `marker=CONFIRMED, activation objects absent` is ambiguous between:

1. a legitimate crash after marker confirmation but before first DDL installation; and
2. post-install deletion of an already-installed activation table/trigger.

An explicit recovery API that repairs both states would therefore also repair the deletion case and destroy the fail-closed signal LAB-092 is intended to preserve.

## Existing mechanism inspected

`experiments/shared_anchor_intent_ledger/protocol.py` already supports exactly the durable primitive needed:

- `Intent.intent_type="migration"` is an allowed authenticated intent type;
- `Intent.payload_digest` canonically binds component/type/payload;
- `reserve()` assigns a deterministic request id from exact position + intent identity/content and persists one PREPARED tail;
- `execute()` is idempotent for the same intent id/content, advances the external provider, reauthenticates the RECONCILE result, then confirms the row with a receipt binding;
- a PREPARED copy can therefore be resumed by invoking `execute()` with the same deterministic intent.

`SupportedHistoricalSharedAnchorLedger._init_activation_schema()` currently creates and verifies `provider_generation_activations` plus `block_intent_during_provider_activation` under one `BEGIN IMMEDIATE`, so the local DDL phase already has a coherent atomic installation primitive.

## Corrected contract

Use a single deterministic *completion* intent, but confirm it **after** exact activation DDL installation, not before it.

Canonical proposal:

- component_id: `provider-generation-activation-schema`
- intent_id: `migration:provider-generation-activation-schema:v1`
- intent_type: `migration`
- payload: `{ "schema": "provider-generation-activation", "version": 1 }`

The exact strings are API constants, not caller-controlled configuration.

### `migrate_activation_schema_v1()`

This is an explicit migration/recovery API; ordinary constructor startup must not silently invoke migration when provenance is incomplete.

1. Inspect marker state and exact sqlite_master object state before mutation.
2. If marker is CONFIRMED:
   - exact table + exact trigger => idempotent success;
   - either object missing/mismatched => fail closed as post-completion tamper; never recreate.
3. If marker is absent and both objects are absent (legitimate legacy candidate):
   - `BEGIN IMMEDIATE`;
   - create table + trigger;
   - verify exact canonical definitions in the same transaction;
   - commit;
   - call existing `execute(canonical_migration_intent)` to obtain authenticated completion provenance.
4. If marker is absent and both objects already exist with exact definitions (crash after DDL commit, before marker reservation):
   - do not mutate DDL;
   - execute the canonical completion intent.
5. If marker is PREPARED and both objects are exact (crash during provider/receipt confirmation):
   - execute the same canonical intent; existing `reserve()`/`execute()` semantics resume it idempotently.
6. Marker absent/PREPARED plus partial or mismatched DDL => fail closed; do not repair ambiguous local tamper.
7. After intent confirmation, re-open under `BEGIN IMMEDIATE`, re-read the exact CONFIRMED marker and exact DDL definitions, then commit the verification-only transaction. This closes local races between external confirmation and return.

## Ordinary startup classification

The normal constructor should only accept:

- CONFIRMED completion marker + exact canonical table + exact canonical trigger.

For migration compatibility, a legacy database with marker absent + both objects absent should raise a dedicated migration-required condition rather than auto-installing. This prevents ordinary restart from converting evidence absence into a repair path.

All other partial states fail closed.

A compatibility wrapper may explicitly call `migrate_activation_schema_v1()` during a controlled upgrade, but that action must remain distinguishable from ordinary runtime startup.

## Why DDL-first is stronger

Once the completion marker is CONFIRMED, code has already passed an exact local DDL verification before provider-backed marker confirmation. Therefore a later missing/mismatched object is unambiguously *after completion* and can be treated as tamper.

The only crash-recovery states before completion have marker absent/PREPARED. They are recoverable only when both local objects are already exact; partial/mismatched local states remain fail closed.

This avoids a second unauthenticated local marker table and uses the existing authenticated shared-anchor history as the durable provenance authority.

## Required RED regressions

### 1. Legitimate legacy first migration

Seed a valid pre-LAB-090 DB with no activation table, no activation trigger, and no completion intent. Ordinary startup must report migration-required. Explicit `migrate_activation_schema_v1()` must install exact DDL, confirm the canonical migration intent, and make subsequent ordinary startup succeed.

### 2. Completed installation followed by table deletion

Run migration to completion, verify the completion intent is CONFIRMED, then `DROP TABLE provider_generation_activations` (which also removes dependent trigger in SQLite). Subsequent ordinary startup and explicit migration API must both raise a historical/durability verification error. Neither may recreate the table.

### 3. Crash after DDL commit before marker

Seed exact canonical table+trigger with marker absent. Ordinary startup must report migration-recovery-required. Explicit migration must leave DDL bytes unchanged, confirm the canonical intent, then succeed.

### 4. Crash with PREPARED marker

Seed exact DDL plus the exact canonical migration intent in PREPARED state with provider state compatible with existing `execute()` reconciliation. Explicit migration must resume the same intent_id/content and reach CONFIRMED without reserving a second migration intent.

### 5. Partial local objects without confirmed provenance

Marker absent/PREPARED with only table, only trigger, or mismatched SQL must fail closed. Migration must not drop/recreate or normalize these objects.

### 6. Race around completion

After local DDL commit but before marker confirmation, a competing shared-ledger writer may legitimately serialize first; this can delay the migration intent but must not permit ambiguous DDL mutation. After marker confirmation, final verification under `BEGIN IMMEDIATE` must reject any concurrent DDL tamper visible before return.

## Smallest implementation surface

Prefer a LAB-092 subclass/module over changing LAB-090 constructor semantics in-place until regressions are proven. The minimum new public surface is one explicit `migrate_activation_schema_v1()` plus a startup classifier/verification helper. Reuse LAB-090 canonical `_ACTIVATION_TABLE_SQL`, `_ACTIVATION_TRIGGER_SQL`, `_normalized_sql` and existing `SharedAnchorLedger.execute()` semantics; do not add another metadata table, PRAGMA marker, or caller-supplied migration identity.

## Decision

Supersede the marker-before-DDL ordering from the previous LAB-092 research note. Retain the single authenticated migration-intent idea, but make it a post-DDL **completion provenance** marker. This is the smallest ordering that makes `CONFIRMED marker + missing object` an unambiguous deletion/tamper signal while preserving deterministic crash recovery before completion.
