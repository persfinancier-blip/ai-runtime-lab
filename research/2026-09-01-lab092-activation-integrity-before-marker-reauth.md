# LAB-092 — activation integrity before marker reauthentication

Date: 2026-09-01
Issue: #176
Draft PR: #177 (`lab-092-activation-schema-provenance`)

## Question

Can LAB-092 provenance verification mask, reorder, or mutate state before LAB-090 `_verify_activation_records()` reports malformed historical `COMMITTED` activation rows?

## Finding

Yes. On an already `COMPLETE` LAB-092 database, startup constructed a non-mutating confirmation surface, verified provider-history/runtime authority, and then called `execute(_completion_intent())` before constructing the full LAB-090 ledger. If the migration marker's historical receipt was missing, `execute()` could externally reauthenticate and persist the receipt before LAB-090 later reached `_verify_activation_records()`.

A malformed `COMMITTED` activation row can avoid the SQL_COMMITTED trigger fence and can also be outside the durable current generation, so `_recover_pending_activation()` does not necessarily encounter it. The later `_verify_activation_records()` does detect structural failures such as a missing referenced provider generation. Therefore the old ordering admitted a real mutation-before-integrity-failure path.

## Regression-first change

Commit `ab9b2e1702ff7120e5c966d85e436f148cbce89c` adds `test_corrupt_historical_activation_fails_before_missing_marker_receipt_is_recreated` to `test_activation_schema_pre_auth_history_verification.py`.

The regression:

1. creates a legitimate LAB-090 database;
2. migrates it to LAB-092 COMPLETE provenance;
3. deletes only the migration marker's stored historical receipt;
4. injects a `COMMITTED` activation row whose `new_generation_id` has no provider-history descriptor;
5. starts LAB-092 and requires `HistoricalVerificationError`;
6. asserts the missing migration receipt remains absent.

This specifically distinguishes fail-before-mutation from merely eventually failing.

## Fix

Commit `b5be5d8e335f463c1af22877aa181a6e7db45fb0` adds `_verify_confirmation_activation_integrity()` and calls inherited LAB-090 `_verify_activation_records()` on the non-mutating confirmation surface before any migration-marker `execute()` in both ordinary COMPLETE startup and explicit migration confirmation.

Published provenance blob after re-fetch: `8418463dc8d05e49daaeaa8a00e497b56df4ce7b`.

The change reuses LAB-090's existing activation-record validator rather than duplicating the schema/identity checks in LAB-092.

## Validation actually observed

A fresh exact checkout/test attempt was executed:

`git clone --depth 1 --branch lab-092-activation-schema-provenance https://github.com/persfinancier-blip/ai-runtime-lab.git ...`

The transport failed before repository code execution with:

`Could not resolve host: github.com`

Therefore no RED/GREEN or branch-suite PASS is claimed in this run. The branch content was re-fetched through the GitHub connector after publication and contains the intended pre-reauth activation-integrity call sites.

## Audit notes

- This fix does not mutate LAB-086 or LAB-090.
- It preserves the existing rule that legacy/unmarked/PREPARED startup is read-only and requires explicit migration.
- It preserves provider-history/runtime verification before external marker reauthentication.
- It adds activation-record integrity verification before that same external mutation boundary.
- A separate concurrency question remains: arbitrary concurrent direct database tampering between the read-only validation and external marker execution is not newly solved here. Existing code already treats supported writers and SQLite writer transactions as the concurrency boundary; do not claim stronger hostile concurrent-DB-tamper resistance without a dedicated design/regression.

## Next action

LAB-086 remains priority #1: probe for a supported byte-preserving patch composition path. If unavailable and exact execution remains unavailable, continue LAB-092/LAB-090 integration audit at the next mutation boundary: `verify_activation_schema_provenance()` currently calls marker `execute()` directly on an already-constructed object; determine whether that public verification method needs the same pre-execute activation-integrity recheck after post-construction tamper, and add a regression first only if the method's contract is intended to detect such post-startup corruption before receipt mutation.
