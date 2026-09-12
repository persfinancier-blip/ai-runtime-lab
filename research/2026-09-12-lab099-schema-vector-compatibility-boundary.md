# LAB-099 — schema/vector compatibility boundary

Date: 2026-09-12

## Context

LAB-099 already has two intentionally independent test-owned reference layers on draft PR #186:

- `lab099_precursor_reference_vectors.py` freezes canonical PREPARED/CONFIRMED authority bytes and digests without choosing precursor SQL;
- `lab099_schema_identity_reference.py` freezes the non-SQL schema-identity authority relation without choosing a production API or physical DDL.

The next safe slice was to prove these two references describe the same already-frozen authority fields, without inventing a physical schema.

## Result

Added test-only, non-discoverable `lab099_schema_vector_compatibility.py` on PR #186.

The check maps only fields already frozen by the two prior references:

- PREPARED logical database identity;
- LAB-092 completion digest;
- predecessor provenance head and epoch;
- exact relation-definition digest;
- exact PREPARED event digest;
- CONFIRMED -> exact PREPARED binding;
- resulting provenance head and epoch;
- CONFIRMED event digest.

It first requires the independent authority vectors to validate, then constructs the schema-identity reference objects from those exact vector fields and requires `PREPARED_INCOMPLETE` and `CONFIRMED` classifications at the corresponding frozen states.

## Boundary

This slice deliberately does **not**:

- define literal SQLite DDL;
- define relation/table/index/trigger names;
- enable the fixture adapter mutation plans;
- make RED-intent cases discoverable as `test_*`;
- select a production API;
- add or modify production behavior.

`REFERENCE_ONLY_RELATION_DEFINITION_DIGEST` remains a synthetic DIGEST32 test value, not schema authority.

## Validation actually executed

Direct repository materialization was re-probed first and again failed before repository code execution with `Could not resolve host: github.com` (git exit 128).

For the newly authored compatibility module only:

- local `python -m py_compile` PASS;
- local `git hash-object` = `7a03017ea06cf5b0e4b3393ec4669209736bd465`;
- post-publication GitHub blob = `7a03017ea06cf5b0e4b3393ec4669209736bd465` (byte-exact match).

The compatibility function itself was **not** executed against the exact imported PR modules because this runtime still exposes no supported connector-to-local byte materialization path. Therefore no LAB-099 RED/GREEN or repository behavioral PASS is claimed.

## Decision

Freeze this as `LAB099_SCHEMA_VECTOR_NON_SQL_COMPATIBILITY_V1_FROZEN`.

Production LAB-099 code and physical precursor DDL remain blocked on executable RED evidence plus an independently frozen physical schema decision.
