# LAB-091 receipt affinity adoption gap

Date: 2026-08-29
Issue: #170
PR: #173
Branch: `lab/091-mutable-shared-anchor-writer`

## Finding

`asymmetric_provider_receipts` is part of the protected LAB-091 trigger surface, but the first-adoption schema-domain validator previously checked affinity/NOT NULL only for the three LAB-080 mutable tables. A legacy LAB-082 receipt table could therefore preserve canonical identity and valid existing rows while declaring a non-canonical affinity such as `generation TEXT NOT NULL`.

SQLite applies column affinity before `BEFORE INSERT` triggers observe `NEW.*`. A bound integer `1` inserted into a `TEXT`-affinity `generation` column is observed by the trigger/UDF as string `"1"`. LAB-091 receipt authorization binds an exact row token including integer generation, so such a legacy schema can pass adoption but make the supported guarded receipt write semantically incompatible.

## Reproduction

A focused SQLite reproduction created `asymmetric_provider_receipts(generation TEXT NOT NULL)` plus a `BEFORE INSERT` trigger calling a connection UDF. Binding integer `1` produced UDF observation `"1"` (`str`) and durable SQLite `typeof(generation)='text'`.

## Fix

Extended `adoption_schema_domains.py` so `asymmetric_provider_receipts` now requires the canonical LAB-082 domain:

- `request_id`, `provider_id`, `kind`, `challenge`, `signature`, `stable_binding`: TEXT affinity;
- `generation`, `position`: INTEGER affinity;
- every non-primary receipt field listed by LAB-082's schema remains NOT NULL.

Published runtime commit: `627f7257437f3da2438e32c2e6b7871c0a76a246`; blob `3688066de1ba12bc485a3dcc5846033685cbcb96`.

Added `tests/test_receipt_adoption_affinity_regression.py` in commit `d4ad82916a4a4a2cb79ef7ebe6c8466a0e32d820`; blob `35baec3bf65c23b6af2fadae3695fa879c4499f2`.

## Execution evidence

Executed a focused semantic candidate locally against SQLite covering the same four assertions:

1. canonical four-table schema accepted;
2. receipt `generation TEXT` rejected;
3. nullable receipt `stable_binding` rejected;
4. SQLite pre-trigger affinity coercion reproduced.

Result: **4/4 PASS**.

The repository branch itself was not available as an executable filesystem in this run, so the newly published pytest file was not claimed as executed byte-for-byte. This remains within the existing LAB-091 full-stack execution blocker and must be included when a branch-to-executable-FS bridge is available.

## Audit

This is fail-closed adoption hardening only. It does not alter canonical fresh schemas or receipt serialization. The additional requirements mirror the existing LAB-082 `CREATE TABLE asymmetric_provider_receipts` contract and are applied under the existing first-adoption `BEGIN IMMEDIATE` lock.
