# LAB-091 — generated extra-column adoption compatibility gap

Date: 2026-08-30

## Scope

Continuation of the first-adoption compatibility audit for draft PR #173. The audit rule remains: add no SQLite adoption guard without a reproduced, reachable supported-write failure.

## Reproduced defect

The prior `validate_no_required_extra_columns()` correctly rejected ordinary additive columns declared `NOT NULL` without a `DEFAULT`, but intentionally ignored generated/hidden columns pending a concrete counterexample.

A reachable counterexample exists. An otherwise canonical legacy `shared_anchor_intents` table can add:

```sql
legacy_json TEXT GENERATED ALWAYS AS (
  json_extract(component_id,'$.x')
) STORED
```

The legacy table can be empty and therefore has valid pre-adoption state. `PRAGMA table_xinfo(shared_anchor_intents)` reports the extra generated column with `hidden=3`, so the previous validator ignored it. LAB-091's canonical writer accepts an ordinary non-empty component identity such as `component-b` and does not provide the generated column explicitly. SQLite evaluates the inherited generated expression during that supported INSERT; `json_extract('component-b', '$.x')` raises `OperationalError: malformed JSON`.

Therefore adoption could succeed while the next contract-valid supported write fails solely because of inherited legacy schema behavior.

A second local mechanism probe also reproduced the same class through a generated `NOT NULL` expression that yields NULL for a contract-valid component identity. The JSON expression is used in the regression because it demonstrates that even a nullable generated extra column can reject a supported write; checking only generated-column nullability would be insufficient.

## Decision

Fail closed on any non-canonical generated extra column in the four LAB-091 mutable tables. SQLite `PRAGMA table_xinfo` identifies generated columns as `hidden=2` (VIRTUAL) or `hidden=3` (STORED).

This intentionally prefers adoption safety over accepting benign-looking generated legacy metadata. Proving an arbitrary inherited generated expression total over every LAB-091-supported future write would require materially broader expression analysis; the supported writer does not need that legacy column, so rejecting the schema is the smaller and auditable boundary.

Ordinary nullable extras and ordinary `NOT NULL ... DEFAULT ...` extras remain accepted by this validator.

## Published implementation

Branch: `lab/091-mutable-shared-anchor-writer`

- `b713c735eca2e8d57115c328088fd16cf3b828d8` — `adoption_extra_columns.py` rejects non-canonical generated extras while retaining ordinary omittable extras.
- `9f999dd9704742d5f929c4d340494d02322b044e` — regression added to `test_adoption_required_extra_column_regression.py`; confirmed PR #173 head after publication.
- GitHub content blobs after re-fetch:
  - validator: `e7fa006dcf287171a0f924da9f0cce87cc9660e8`
  - regression: `6829ff017e526fb132461ac1d6619ea96a6c5967`

## Executed evidence

A local reconstruction from the re-fetched published validator and regression content was executed with Python `unittest`:

- canonical schema accepted;
- ordinary nullable extra accepted;
- ordinary `NOT NULL` extra with a default accepted;
- ordinary required extra rejected and the pre-fix supported-shape INSERT reproduces its `IntegrityError`;
- generated nullable JSON extra rejected and the unguarded supported-shape INSERT reproduces `OperationalError: malformed JSON`.

Result: **4/4 PASS**.

The environment emitted an unrelated spreadsheet-runtime warmup traceback before Python test discovery, but `unittest` itself completed with return code 0 and all four named tests `ok`.

This is focused exact-content reconstruction evidence for the two published files, not a claim that the complete PR #173 branch/full real-stack gate has executed. The remaining final-surface timeout/UNKNOWN, process crash/concurrency, composition, and accumulated adoption regressions still require executable transport for the whole branch.

## Audit

- No trigger/UDF authority semantics changed.
- No canonical schema was widened or rewritten.
- The validator still requires an active adoption transaction.
- The change is limited to legacy schema acceptance and is fail-closed.
- The reproduced failure occurs through the same canonical INSERT shape used by LAB-091, so the guard is not speculative.
