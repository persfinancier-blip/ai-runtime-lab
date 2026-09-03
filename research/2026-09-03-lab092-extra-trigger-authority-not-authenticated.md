# LAB-092 audit — additional persistent triggers are outside the authenticated provenance surface

Date: 2026-09-03

## Scope

Fallback source audit of draft PR #177 (`lab-092-activation-schema-provenance`, observed head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`) while LAB-086 exact byte-preserving publication remains unavailable in the current runtime.

This finding is intentionally scoped to a distinct provenance gap. It does not replace the retained carrier-schema, preseeded-marker, inherited-ledger-authentication, or TOCTOU findings.

## Source observation

`activation_schema_provenance._schema_object_state()` checks only the objects with the two required LAB-090 names:

- `provider_generation_activations`; and
- `block_intent_during_provider_activation`.

For the required trigger it compares the stored SQL text, after whitespace normalization, to `_ACTIVATION_TRIGGER_SQL`.

Neither `_schema_object_state()` nor `_classify()` enumerates all persistent triggers attached to `shared_anchor_intents`, `provider_generation_activations`, `shared_anchor_meta`, `component_anchor_watermarks`, or other authority-relevant tables.

`_install_and_reserve_prepared()` subsequently inserts the deterministic migration PREPARED row into `shared_anchor_intents` and advances `shared_anchor_meta.reserved_position` under `BEGIN IMMEDIATE`. Any additional persistent SQLite trigger on that INSERT executes inside the same transaction and its side effects are committed together with the migration marker unless separately detected.

## Reproduced SQLite semantic schedule

An isolated file-backed SQLite probe created:

1. the ordinary shared-anchor meta/intents/watermark tables;
2. the exact LAB-090 activation table;
3. the exact required `block_intent_during_provider_activation` trigger; and
4. one additional persistent `AFTER INSERT ON shared_anchor_intents` trigger matching the LAB-092 migration intent id and updating an existing component watermark.

The probe then performed the same relevant mutation shape as `_install_and_reserve_prepared()`:

- `BEGIN IMMEDIATE`;
- insert the migration row as `PREPARED`;
- advance `shared_anchor_meta.reserved_position`;
- commit.

Observed result:

- the required LAB-090 trigger remained present with its exact definition;
- the additional trigger also remained present;
- the extra trigger changed the authority-relevant watermark from `0` to `777`;
- the transaction committed successfully.

This is a SQLite semantic reproduction of the trigger-set omission. It is not claimed as exact PR behavioral execution because exact branch/source execution remains unavailable in this runtime.

## Why this is distinct

This is not the existing provenance-carrier-schema finding. The carrier table may have its exact schema and the required activation DDL may also be exact. The missing predicate is that the **complete authority-relevant persistent trigger set** is trusted, not merely that one required trigger exists with exact text.

It is also not a check/use TOCTOU. The extra trigger can exist before migration begins and remain unchanged for the entire operation. The consequential mutation occurs deterministically as part of the very INSERT that LAB-092 believes is creating authenticated migration provenance.

A later full LAB-080 durable verification could detect some forged side effects, such as an out-of-range watermark, but that would happen only after the DDL/PREPARED/meta transaction has already committed. Therefore later verification cannot satisfy the stronger fail-before-authority-mutation requirement.

## Security/correctness impact

A database with the exact named LAB-090 objects can still contain additional trigger authority that changes durable state during migration or later provenance operations. Depending on the trigger body, this can mutate watermarks, meta, activation records, receipts, or other tables reachable from SQLite trigger statements.

Consequently, `exact required object present` is not equivalent to `exact migration authority schema authenticated`.

## Regression-first requirement

Before treating LAB-092 provenance as complete, add deterministic regressions that install an otherwise exact schema plus one additional persistent trigger on each relevant mutation surface, at minimum:

- `shared_anchor_intents` migration-marker INSERT;
- `shared_anchor_meta` tail update;
- activation table writes; and
- any receipt/watermark table mutated during confirmation/recovery.

The pre-fix regression should demonstrate that the extra trigger can execute while `_schema_object_state()` still accepts the named required objects.

Post-fix, migration/startup/provenance verification must fail closed **before any DDL, marker, meta, provider, receipt, activation, or watermark mutation** when an untrusted additional trigger can affect the authority transaction.

## Design constraint

Do not fix this by checking only for one known malicious trigger name. The authenticated schema predicate must cover the complete authority-relevant trigger set (or make the migration operate in a database capability/schema boundary where additional trigger authority is cryptographically/procedurally excluded).

Likewise, a separate preflight `SELECT name FROM sqlite_master ...` followed by an unsynchronized mutation would recreate the retained LAB-092 check/use race. The trigger-set proof must be bound to the same SQLite serialization/authority boundary as the consequential mutation.

## Status

Source-proved and independently reproduced at SQLite semantics level. Exact branch RED/GREEN remains pending because exact source execution is unavailable. Strengthen #176; do not create a duplicate issue.
