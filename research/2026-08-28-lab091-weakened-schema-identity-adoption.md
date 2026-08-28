# LAB-091 — first-adoption identity cardinality under weakened legacy schema

Date: 2026-08-28

## Finding

`initialize_shared_anchor_schema()` uses `CREATE TABLE IF NOT EXISTS`. That is correct for normal restart, but first adoption cannot infer from it that a preexisting legacy database still carries LAB-080 primary/unique constraints.

The pre-fix row validator checked content/state-machine fields and contiguous positions, but it could accept a structurally weakened legacy `shared_anchor_intents` table containing the same non-empty `intent_id` at two distinct contiguous positions. Such a state cannot be produced by the supported LAB-080 schema (`intent_id PRIMARY KEY`), yet later lookups such as `WHERE intent_id=?` become ambiguous after adoption.

The same first-adoption principle applies to the singleton metadata row, provider-receipt request identity, and component-watermark identity: existing identity cardinality must be proven rather than assumed from an old schema declaration.

## Focused reproduction

A local SQLite semantic probe recreated the current validator logic against a deliberately constraint-free legacy fixture with:

- `reserved_position=2`;
- two contiguous `CONFIRMED` intents;
- both rows using the same `intent_id`;
- deterministic request IDs computed for positions 1 and 2;
- matching non-orphan receipt rows.

The pre-fix validation logic returned `True`, demonstrating the adoption gap. This was a semantic reproduction of the branch logic, not a claim that the full historical branch stack was executed byte-for-byte.

## Fix

Branch `lab/091-mutable-shared-anchor-writer` now makes first adoption fail closed when existing identities could not have come from the supported state machine:

- exactly one `shared_anchor_meta` row, with `singleton=1`;
- unique existing `intent_id` values;
- unique existing deterministic `request_id` values;
- unique existing receipt `request_id` values;
- unique existing watermark `component_id` values.

Published commits:

- validator fix: `bc2f95d4ca6815383fe30fe856369c5ef1251d29`;
- regression: `80f84da5338706ab11666e1c5f561ff8bfc510fa`.

Exact published blobs:

- `adoption_validation.py`: `c7fff2c6c492ea470a2f495e112c72246aee3258`;
- `test_adoption_schema_identity_regression.py`: `ac2d6f5f23545a6871a04c589937213a579e3f9e`.

## Executed focused evidence

The exact validator and test bytes above were materialized locally and their Git blob hashes matched GitHub. The focused regression then executed:

- duplicate legacy `intent_id` -> rejected;
- duplicate metadata singleton -> rejected;
- duplicate receipt request identity -> rejected;
- duplicate watermark component identity -> rejected.

Result: **4/4 PASS**.

The focused harness used a minimal local package for imports, so this is exact target-file evidence, not a complete LAB-080/LAB-082/LAB-091 dependency-closure PASS.

## Security interpretation

First-adoption validation must establish semantic facts that future guards depend on even when the old database schema itself is not trusted as evidence. Persistent triggers constrain future statements; they cannot repair ambiguous identities already present at adoption time.

This is distinct from the earlier TOCTOU fix: the `BEGIN IMMEDIATE -> verify_durable -> install guards -> validate -> commit` envelope closes concurrent-writer races, while this fix closes preexisting identity ambiguity inside that locked snapshot.

## Remaining gate

PR #173 remains draft. The complete exact real-stack gate is still required, including two-worker/crash convergence, timeout-after-commit/UNKNOWN reconciliation, LAB-087 restricted-worker composition, restart, and final reentrancy/alternate-write-surface audit.
