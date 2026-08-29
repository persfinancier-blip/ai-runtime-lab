# LAB-091 missing-singleton adoption write gap — 2026-08-29

## Finding

`restart_safe_schema.initialize_shared_anchor_schema()` previously treated any database with no `shared_anchor_meta(singleton=1)` row as fresh and inserted `(1,0)` before first-adoption verification. That is unsafe for a preexisting mutable shared-anchor schema: the initializer mutates legacy state before validation and can erase the evidence that metadata was missing.

## Reproduction

A focused SQLite probe created the canonical three mutable shared-anchor tables but intentionally omitted the metadata singleton. Running the pre-fix initializer changed the database from zero metadata rows to `[(1, 0)]`. This demonstrates the unwanted pre-validation write directly.

## Fix

Branch `lab/091-mutable-shared-anchor-writer` now snapshots the preexisting table set before any `CREATE TABLE IF NOT EXISTS`. If any LAB-091 mutable shared-anchor table already existed and the singleton is absent, initialization raises `RestartSchemaError` and rolls back. Only a genuinely fresh database may synthesize `(1,0)`.

- implementation commit: `736434d0430bfae40d5726b0e63c310b0e98f8b8`
- implementation blob: `5b1ff616d9ddefbf82742e79d3b547eb02b8754b`
- regression commit: `fac191b8daba8754b3fe004576dfd31904e0ae83`
- regression blob: `60b4c33a9edf6b2405cd861b89b69037b2f89a37`

## Validation actually executed

The exact published implementation/regression text was reconstructed in the executable runtime and run with Python unittest. Result: 2/2 PASS:

1. a fresh database receives singleton `(1,0)`;
2. a preexisting canonical mutable schema with the singleton missing fails closed and remains with zero metadata rows.

The Python runtime emitted an unrelated spreadsheet warmup timeout before unittest output; the two tests themselves completed successfully and unittest returned `OK`.

## Scope / remaining work

This closes one alternate-write/adoption gap only. It does not substitute for the still-pending real final-ledger timeout/UNKNOWN and process concurrency/crash tests. LAB-086 remains higher priority and its exact rowid candidate must still be published only through a byte-preserving whole-file path with predecessor/hash verification.
