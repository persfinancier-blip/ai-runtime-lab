# LAB-091 — unavailable persisted column-collation adoption gap

Date: 2026-08-30

## Finding

A legacy SQLite database can declare an application-defined collation directly on a canonical LAB-091 TEXT column while that collation is registered by the legacy process. SQLite persists only the collation name in the schema. Reopening the database through the supported LAB-091 connection does not recreate that application-defined collation.

Concrete reproduction used `shared_anchor_intents.status TEXT COLLATE LEGACY_ONLY NOT NULL` plus a persisted `BEFORE INSERT` predicate `NEW.status!='PREPARED'`. The legacy process registered `LEGACY_ONLY`, created/committed the schema, and closed. A fresh supported-shape SQLite connection without that registration then attempted an otherwise-valid canonical INSERT. SQLite failed while evaluating the persisted comparison with:

`sqlite3.OperationalError: no such collation sequence: LEGACY_ONLY`

This is a reachable first-adoption compatibility/availability defect: schema creation is valid in the legacy environment, reopen succeeds, but an authorized canonical write cannot execute.

## Fix

Added `experiments/mutable_shared_anchor_writer/adoption_column_collations.py` and wired `validate_resolvable_column_collations()` into the final adoption transaction before mutable-state acceptance.

The validator prepares a zero-row self-comparison for every canonical TEXT column. Preparing the expression forces SQLite to resolve that column's declared collation without mutating rows or depending on any row being present. An unavailable persisted collation is rejected fail-closed before adoption completes.

Scope is intentionally narrow: this does not reject every non-BINARY built-in collation merely because it differs from the canonical schema. It closes the reproduced unavailable-collation write failure. Existing identity/index validators continue to own byte-exact identity and secondary-index collation semantics.

## Published implementation

Draft PR #173, branch `lab/091-mutable-shared-anchor-writer`:

- `6b700c55eb340c0902600fccb157995874279678` — add column-collation adoption validator;
- `fe3b69852b5ab0f00135c409e7bef3a6d6247efe` — wire validator into final supported constructor/adoption envelope;
- `aad64cc350b5fdef44f941d0d2cffd22adf5b0f5` — add regression; branch head at publication time.

Published blobs re-fetched and locally Git-hashed:

- `adoption_column_collations.py` = `19b78a59fe3e8b3eae9f30eab15b00fff5584001`;
- `test_adoption_column_collation_regression.py` = `39e7246082c89636ad57c01e885f353d38d47927`.

The locally recomputed Git object identities matched those published blobs exactly.

## Validation actually executed

Focused exact-published-byte unittest: **2/2 PASS**.

- canonical BINARY/default TEXT declarations are accepted;
- legacy-only persisted status collation reproduces the pre-fix supported-shape INSERT failure and is rejected by the new adoption validator before acceptance.

Python startup also printed an unrelated spreadsheet-runtime warmup timeout. The unittest process returned exit code 0 and both LAB-091 tests completed successfully.

This is focused exact-candidate evidence, not a claim that the complete PR #173 dependency closure/full-stack suite executed.

## Audit

The check is read-only at the data level and runs inside the existing `BEGIN IMMEDIATE` adoption envelope. `LIMIT 0` still resolves the declared collation at statement preparation, so it catches the defect even on an empty table. Non-collation `OperationalError`s are not rewritten; they propagate instead of being misclassified.

LAB-086 remains priority #1. Its 949-line `strict_fence.py` per-file patch is now observable in full through the connector, but no supported tool path in this run directly composes that fetched payload with the retained hidden-rowid patch and transfers the exact bytes into Contents API without model/manual whole-file reserialization. No LAB-086 source mutation was attempted.
