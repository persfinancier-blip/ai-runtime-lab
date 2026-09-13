# LAB-095 under-lock full-history verification fix

Date: 2026-09-13
Issue: #180
Branch/PR: `lab-095-database-identity-red-intent` / #187

## Observation

The prior `prepare_database_identity()` performed `history.verify_durable()` before acquiring `BEGIN IMMEDIATE`, then performed only shallow bootstrap/head checks under the writer lock. It also called `install_custody_schema()` before any full under-lock verifier. A provider-history transition/proof could therefore change after the precheck while a superficially matching head survived, and a failing under-lock check could leave custody schema mutation behind.

## Fix

PR #187 now calls the existing integrated `history._verify_durable_locked(q)` on the same SQLite connection immediately after `BEGIN IMMEDIATE`, before custody DDL/DML, CSPRNG nonce generation, shared-anchor reservation, or tail mutation. The locked verified `(provider_id, generation)` must match both the pre-lock durable current descriptor and runtime ledger provider authority. Reservation fields are sourced from the locked verified descriptor.

Published production blob after the fix: `eef3277def1443ea880e64240ef314f731825a98`.

The existing focused migration regression fake was updated to provide `_verify_durable_locked()` and now expects the head-race failure at the stronger under-lock authority comparison. PR head after test alignment: `74d4acf0a7fb819cef574c841cdf9d7ee31d2476`.

## Execution evidence

Direct LAB-086 clone was re-probed first and failed before repository execution with `Could not resolve host: github.com`, exit 128. No LAB-086 PASS is claimed.

The candidate LAB-095 production source passed local `py_compile`; local `git hash-object` was `eef3277def1443ea880e64240ef314f731825a98`, matching the published GitHub blob exactly.

A focused file-backed SQLite semantic harness executed four migration cases against the exact published migration module with minimal dependency stubs:

1. corrupt full-history verifier under the writer lock -> exception, zero shared-anchor rows, no custody table persisted;
2. fresh PREPARED retry -> same nonce and request reused;
3. head change between precheck and writer lock -> rejected before custody creation;
4. externally CONFIRMED restart -> same custody finalized locally.

Result: 4/4 PASS.

This is focused semantic evidence only. It is not a claim that the complete repository/downstream LAB-080/081/090/092 closure is GREEN.

## Audit

The fix closes the identified TOCTOU because full chain verification and migration mutation now share the same SQLite writer transaction. It also moves custody schema creation behind that verification, preserving zero migration mutation when history is already corrupt.

Remaining risks/gates:
- exact repository execution of the committed RED/focused tests;
- crash-before-commit, partial-state, concurrent-installer, and legacy-history migration regressions;
- DB-A/DB-B binding regression and LAB-080/LAB-081/LAB-090/LAB-092 downstream gates;
- security-sensitive LAB-090/LAB-095 conflict resolution preserving `CanonicalDatabaseBinding` MRO.
