# LAB-099 schema-identity verifier boundary

Date: 2026-09-12

## Context

LAB-086 remains priority #1, but exact repository materialization is still unavailable in the current runtime: direct `git clone --no-checkout` failed before repository execution with `Could not resolve host: github.com` (exit 128). No new LAB-086 executable/security PASS is claimed.

The recorded fallback was to continue only LAB-099 draft PR #186 without production behavior, literal precursor DDL, or mutation plans. The immediate task was to freeze the RED-owned schema-identity verifier boundary that is already implied by prior authenticated-cutover decisions.

## Decision

Freeze a test-owned, side-effect-free reference oracle that contains **no SQLite DDL and no production API choice**.

Published on PR #186:

- `experiments/provider_generation_history/tests/lab099_schema_identity_reference.py`
- branch commit `339a0122b4e93add6eb6962fde92aaf4ea183356`
- Git blob `06f80aeb5a3203036a3964448d1c0dad266a8a30`

The oracle freezes only these already-decided authority rules:

1. A valid LAB-092 completion digest alone leaves LAB-099 precursor governance `ABSENT`; it does not authorize precursor schema.
2. A physical precursor relation without authenticated PREPARED authority is an orphan and fails closed.
3. PREPARED binds exact logical-database identity, exact LAB-092 completion digest, exact predecessor provenance head+epoch, and one exact relation-definition digest.
4. While PREPARED is incomplete, any different/missing physical relation digest fails closed and stale/forked predecessor head+epoch cannot gain authority.
5. CONFIRMED must bind the exact PREPARED event digest and the same relation-definition digest; it is valid only at its authenticated resulting provenance head+epoch.
6. Missing/different physical schema after PREPARED or CONFIRMED is corruption. A confirmed database cannot downgrade to LAB-090/LAB-092 legacy semantics merely because the precursor relation disappeared.

## Explicit non-decisions

This slice does **not** choose or imply:

- table/column names;
- column order or SQLite declared types;
- canonical-body versus decomposed storage;
- CHECK/UNIQUE/index/trigger spelling;
- FK/rowid policy;
- authenticator persistence layout;
- migration mutation plans;
- production function/class names or signatures.

Exact precursor DDL therefore remains independently implementation-gated. `REFERENCE_ONLY_RELATION_DEFINITION_DIGEST` remains synthetic test data and is not schema authority.

## Validation actually executed

Before publication, the exact authored file was executed locally as a standalone, side-effect-free oracle and passed its self-check. `python -m py_compile` also passed.

After publication, local `git hash-object` over the exact authored bytes returned `06f80aeb5a3203036a3964448d1c0dad266a8a30`, exactly matching the GitHub blob returned for the branch file.

This validates only the test-owned reference implementation and byte-exact publication. It is **not** repository RED/GREEN evidence and does not substitute for executing the real LAB-099 production surface.

## Branch audit

Against pinned LAB-092 PR #177 head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`, PR #186 is now ahead 5 / behind 0 and changes exactly four files, all under `experiments/provider_generation_history/tests/`. PR #186 remains draft.

## Next safe slice

Keep DDL/mutation plans disabled. On the next run, probe LAB-086 exact materialization first. If still unavailable, compose this schema-identity oracle with the existing byte-exact PREPARED/CONFIRMED reference vectors and determine the smallest non-SQL RED contract that checks the vector fields against this oracle without inventing production behavior. Do not write LAB-099 production code until actual RED execution is possible and an explicit physical DDL decision is independently frozen.
