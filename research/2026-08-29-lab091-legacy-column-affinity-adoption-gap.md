# LAB-091 — legacy column affinity adoption gap

Date: 2026-08-29

## Finding

LAB-091 first-adoption validation checked required NOT NULL declarations and canonical identity constraints, but did not check SQLite column affinity. `CREATE TABLE IF NOT EXISTS` cannot repair a preexisting legacy table whose declared type has incompatible affinity.

This matters to the one-shot permit boundary. SQLite applies column affinity before a BEFORE trigger observes `NEW.*`. A Python integer `1` inserted into a legacy `TEXT NOT NULL` position column is observed by the trigger as string `"1"`. LAB-091 row/permit tokens distinguish those values, so an empty legacy schema could pass adoption but later make an otherwise supported exact-permit write fail closed. Type/affinity mismatch can also change comparison/coercion behavior relative to the canonical LAB-080 schema.

## Reproduction

Executed an in-memory SQLite probe with the same BEFORE-trigger observation point:

- `INTEGER NOT NULL` position: integer `1` remained SQLite `integer` and exact token matched.
- `TEXT NOT NULL` position: integer `1` became string `"1"` / SQLite `text` before the BEFORE trigger; exact integer permit did not match.

The focused regression also directly captures `NEW.position` and proves the value is `("1", str)` for the incompatible TEXT-affinity schema.

## Fix

Branch `lab/091-mutable-shared-anchor-writer` now extends `adoption_schema_domains.py` with SQLite affinity derivation using SQLite's documented type-name rules and requires canonical affinity for all LAB-091 mutable shared-anchor columns:

- integer-domain fields -> INTEGER affinity;
- text-domain fields -> TEXT affinity.

The existing final supported class already calls `validate_required_not_null_contract()` inside the same `BEGIN IMMEDIATE` adoption transaction, so no additional wiring is needed.

Published runtime commit: `4806c7f0a4d7ea34b239d9a1f639479c1d32bac9`.
Published runtime blob: `36a94d721cc627707be89a0ae1ef99d8bbcaa673`.
Published regression commit: `d18ffff9565ed3ad8c1afeeb672aae09f561975c`.
Published regression blob: `4f1cf3789d6bad0af8943ad612f430f891d3dd90`.

## Validation actually executed

Before publication, the exact candidate helper and regression were executed locally:

- canonical affinity accepted;
- legacy `position TEXT NOT NULL` rejected at adoption;
- SQLite BEFORE-trigger coercion reproduced (`1` -> `"1"`);
- 3/3 unittest PASS;
- focused compileall PASS.

Post-publication re-fetch confirmed the runtime blob `36a94d72...` and regression blob `4f1cf378...` contain the exact tested logic.

## Boundary

This is a first-adoption/schema-compatibility hardening fix. It does not satisfy the remaining PR readiness gate: the exact final supported class still needs full real-stack timeout-after-commit/UNKNOWN and process concurrency/crash execution against the real LAB-080/LAB-082 dependency closure.
