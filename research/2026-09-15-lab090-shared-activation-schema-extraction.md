# LAB-090 shared activation schema extraction

Date: 2026-09-15

## Context

LAB-086 remained transport-blocked in this runtime: direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository execution with `Could not resolve host: github.com`, exit 128. No LAB-086 PASS is claimed.

The next permitted fallback was the smallest prerequisite for composing LAB-092 onto PR #187 without importing LAB-090's authority-heavy `supported.py` wholesale.

## Conflict check

PR #175 (`d9a381dd4607a928cd1315adef6431e239995bc1`) defines these immutable schema/classifier inputs directly in `experiments/provider_generation_history/supported.py`:

- `_ACTIVATION_TABLE_NAME`
- `_ACTIVATION_TABLE_SQL`
- `_ACTIVATION_TRIGGER_NAME`
- `_ACTIVATION_TRIGGER_SQL`
- `_normalized_sql`

PR #187 intentionally has a different provider-history authority topology: canonical DB binding, construction-bound private `_provider_history`, `_history()` for internal authority, and a public least-capability inspection view. Therefore selecting LAB-090 `supported.py` wholesale would reopen previously removed authority paths.

## Implemented slice on PR #187

PR #187 branch `lab-095-database-identity-red-intent` now contains:

- `experiments/provider_generation_history/activation_schema.py`
- `experiments/provider_generation_history/tests/test_activation_schema_contract.py`

Production module properties:

- exact LAB-090 activation table name and DDL;
- exact LAB-090 activation trigger name and DDL;
- SQL whitespace normalization equivalent to LAB-090 `_normalized_sql`;
- no SQLite connection, execute, commit/rollback, ledger, provider, receipt, rotation, activation mutation, or other runtime authority.

Commits:

- production extraction: `000b9edb1cc3b3af4422f498ab80660a677e814d`
- focused contract test / current PR head: `dfef95568179ce45e37beeaec69f86cdd86c4fca`

Published blobs re-fetched from GitHub:

- `activation_schema.py`: `ec6fa59fc947f2d7812ede71617edd3edb511a68`
- `test_activation_schema_contract.py`: `57b5fdd658933b06dcde33fcb56284ef3fff6b22`

## Validation actually executed

A local reconstruction of the exact authored `activation_schema.py` and focused test was executed with:

`python -m pytest -q experiments/provider_generation_history/tests/test_activation_schema_contract.py`

Observed result: `2 passed in 0.08s`.

The test freezes exact LAB-090 DDL/name equivalence, normalization behavior, and an AST/public-surface check that the helper contains no mutation-authority calls.

This is focused helper validation only. It is not a claim that the full PR #187 repository closure or downstream LAB-090/LAB-092 gates are GREEN.

## Decision

Use `activation_schema.py` as the single non-authority schema-definition owner during composition. LAB-092 may depend on this helper for exact persisted-schema classification without importing LAB-090 mutation/rotation authority.

Do not reintroduce constants by copy into LAB-092. Do not resolve conflicts by taking PR #175 `supported.py` wholesale.

## Exact next composition step

Add the smallest LAB-092 classifier/guard layer on PR #187:

1. import activation schema definitions from `activation_schema.py`;
2. perform COMPLETE/provenance classification through the `q` supplied to `_guard_receipt_persistence_locked(q)` so guard + history verification + receipt persistence stay in one transaction;
3. use `ledger._history()` for locked history checks;
4. never call `_bind_live_provider_history_provenance()` and never replace `_provider_history` after construction;
5. add focused fail-closed regressions before porting LAB-090 activation fencing semantics.
