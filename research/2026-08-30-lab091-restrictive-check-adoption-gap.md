# LAB-091 restrictive CHECK adoption gap

Date: 2026-08-30

## Finding

The LAB-091 first-adoption schema-domain gate validated required affinity/NOT NULL guarantees and the effective UNIQUE write contract, but it did not inspect legacy `CHECK` constraints. An otherwise canonical legacy table could therefore carry an extra restrictive `CHECK` and pass adoption even though that constraint rejects a write the supported state machine is entitled to make.

Concrete reproduction: add `CHECK(component_id='component-a')` to `shared_anchor_intents.component_id`. The remaining column affinities, NOT NULL constraints and canonical UNIQUE keys are unchanged, so the previous validator accepted the schema. A supported-shape PREPARED intent for `component-b` then fails with `sqlite3.IntegrityError` before LAB-091 can provide its normal semantics.

This is a first-adoption compatibility defect, not a raw-DDL sandbox claim: the problem exists before LAB-091 assumes ownership of a preexisting schema.

## Fix

PR #173 / branch `lab/091-mutable-shared-anchor-writer` now fail-closes on legacy CHECK expressions outside the canonical set:

- runtime commit `38df1258a3dc17d59efcc66f11db0e48bde05668` updates `adoption_schema_domains.py`;
- regression commit `bb2b3cb49bb2ac05e55a261b26b33f0db3166fc5` adds `test_adoption_restrictive_check_regression.py`.

The validator normalizes SQL syntax outside quoted literals, extracts CHECK bodies with balanced-parenthesis/quoted-string handling, and permits only canonical CHECK expressions. Missing canonical CHECKs remain allowed because the persisted LAB-091 guards re-impose those protected predicates; an additional legacy CHECK is rejected because it can narrow the supported write domain.

## Executed evidence

A focused local unittest was executed against the exact prepared update/test payload before Contents API publication: **3/3 PASS**.

Covered cases:

1. canonical CHECK constraints are accepted;
2. omitted canonical CHECK constraints remain accepted for guard-compatible legacy adoption;
3. the restrictive `component_id='component-a'` CHECK reproduces a real supported-shape INSERT failure and is rejected by the hardened adoption gate.

This is focused payload/mechanism execution. It is not represented as an exact branch checkout/full PR pytest run because no executable GitHub-to-filesystem transport was observed in this run.

## Audit notes

The change is intentionally conservative. Semantically equivalent but syntactically unusual legacy CHECK expressions may be rejected rather than guessed equivalent. That is acceptable for first adoption: false rejection is safer than accepting a schema that silently narrows LAB-091's supported write domain.

LAB-086 remains priority #1 and is unchanged; its retained 949-line security-critical composition still requires a byte-preserving supported path.
