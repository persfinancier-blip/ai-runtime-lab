# LAB-091 — first-adoption schema identity contract

Date: 2026-08-28

## Finding

`CREATE TABLE IF NOT EXISTS` does not repair a weakened preexisting SQLite schema. The prior first-adoption validator rechecked existing row cardinality, but a clean legacy database missing canonical `PRIMARY KEY` / `UNIQUE` identity constraints could still be admitted. After LAB-091 guards were installed, a later otherwise-authorized transition could then reintroduce an ambiguous identity because the transition guards validate state-machine semantics, not all physical uniqueness constraints.

This is distinct from the already-fixed case where duplicate rows already exist at adoption time.

## Fix

On `lab/091-mutable-shared-anchor-writer`, `adoption_validation.py` now inspects SQLite schema metadata before row validation and requires the canonical identity keys:

- `shared_anchor_meta(singleton)` unique/primary;
- `shared_anchor_intents(intent_id)` primary/unique;
- `shared_anchor_intents(position)` unique;
- `shared_anchor_intents(request_id)` unique;
- `component_anchor_watermarks(component_id)` primary/unique;
- `asymmetric_provider_receipts(request_id)` primary/unique.

A clean-looking legacy database missing any one of these constraints is rejected before LAB-091 guards are adopted.

Published branch commits:

- validator: `19502cb3a81887732c95f07ed17fb9763d38dd87`;
- regression: `059bfc1bf544f683277f8cf5b00b37a84e3249b5`.

Exact Git blobs match the locally executed candidate bytes:

- `adoption_validation.py`: `c45142317c405748060a8d7d81587b14be89fc81`;
- `test_adoption_schema_contract_regression.py`: `e87c550282ac455e4ca5bedeb9de4f6626d563a4`.

## Execution evidence

A minimal exact-target harness executed the published candidate logic before publication:

- canonical schema accepted;
- six weakened-schema variants rejected: missing meta singleton key, intent ID key, position unique key, request ID unique key, watermark component key, or receipt request key;
- result: 2 unittest methods PASS, including six subcases for weakened identities.

This is focused target-file evidence. It is not a complete LAB-080/LAB-082/LAB-091 dependency-closure PASS.

## Security interpretation

First adoption must establish both:

1. current rows satisfy semantic/cardinality invariants; and
2. the physical schema will continue enforcing canonical identities after adoption.

Checking only current row contents is insufficient when legacy DDL may have been weakened.

## Next gate

Keep PR #173 draft. Include this schema-contract regression in the complete real-stack adoption gate, then continue auditing whether any other legacy physical property is assumed rather than semantically or structurally revalidated.
