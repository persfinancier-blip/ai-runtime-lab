# LAB-092 public provider-history receipt mutation after provenance deletion

Date: 2026-09-01
Issue: #176
Draft PR: #177

## Question

After a legitimate LAB-092 migration object is constructed and the confirmed activation-schema migration marker is later deleted, do any remaining reachable public surfaces still mutate durable authority before re-validating activation-schema provenance?

## Finding

Yes. The live ledger exposes `ledger.provider_history`, whose type inherited from LAB-090 is `CoordinatorOnlyProviderHistory`.

`CoordinatorOnlyProviderHistory` blocks public provider-generation `rotate()`, but it inherits `DurableProviderHistory.store_receipt()` unchanged. `store_receipt()` verifies the receipt signature against authenticated provider-generation history and then inserts a new row into `historical_provider_receipts` when `request_id` is absent.

The receipt API does not require the request to correspond to an existing shared-anchor ledger row. Therefore, after a valid LAB-092 object is constructed, deleting the confirmed migration marker and then calling `ledger.provider_history.store_receipt(valid_new_receipt)` can still mutate durable historical receipt state without first requiring LAB-092 provenance to remain `COMPLETE`.

This is deterministic and requires no concurrency window.

## Regression-first change

Regression commit on `lab-092-activation-schema-provenance`:

- `1f4175da0122633d66772202bda703bb6b0d9c65`

The regression adds `test_direct_provider_receipt_store_fails_closed_after_marker_deletion` to `test_activation_schema_postconstruction_marker_deletion.py`.

The test constructs a legitimately migrated live LAB-092 object, deletes the confirmed migration marker, constructs a cryptographically valid current-generation `HistoricalReceipt` for a fresh request id, calls the public `ledger.provider_history.store_receipt(receipt)`, and requires:

1. `HistoricalVerificationError`;
2. no row inserted into `historical_provider_receipts` for that request id.

Exact behavioral RED is not claimed because direct branch checkout/execution remains unavailable in this run.

## Fix

Fix commit:

- `81673f8f6e4e0864dfa124735938c40aa28b4f2c`

Current production blob:

- `experiments/provider_generation_history/activation_schema_provenance.py` = `396b67a46686f6df23584b1b366824c1b7ac1886`

The fix introduces `_ProvenanceBoundCoordinatorOnlyProviderHistory`, which overrides only the public durable receipt mutation `store_receipt()` and requires `_classify(path) == "COMPLETE"` before delegating to the inherited cryptographic/history validation and insert logic.

After the normal LAB-090 constructor completes, the live LAB-092 object replaces its public `provider_history` handle with this provenance-bound coordinator surface using `object.__new__` plus the already-validated `path` and `bootstrap`. This deliberately avoids replaying provider-history schema initialization.

The explicit migration/constructor confirmation bridge remains based on the unbound internal `_reservation_surface()`. That is necessary because marker confirmation may need to persist the marker's historical receipt while the local marker is still PREPARED and provenance is not yet COMPLETE. The stricter receipt guard is therefore installed only on the fully constructed live LAB-092 object.

## Public provider-history surface audit

After this fix, inherited public provider-history methods split as follows:

- `rotate()` — already blocked by `CoordinatorOnlyProviderHistory`;
- `store_receipt()` — now LAB-092 provenance-bound on the live object;
- `current()`, `verify_durable()`, `require_current()`, `load_receipt()`, `verify_receipt()`, `make_transition()` — read-only / proof-construction surfaces with respect to durable state.

Private underscore helpers remain outside the supported public surface and were not promoted into a new contract.

## PR mergeability reconciliation

A fresh metadata read after the fix reports PR #177:

- base `lab-090-provider-activation-fencing` at `d9a381dd4607a928cd1315adef6431e239995bc1`;
- head `81673f8f6e4e0864dfa124735938c40aa28b4f2c`;
- `mergeable=true`;
- draft remains true.

The earlier one-off `mergeable=false` observation is therefore not treated as evidence of a durable base conflict. No integration was attempted because exact behavioral gates remain unavailable.

## Runtime/tool evidence

Fresh local probe:

`git ls-remote https://github.com/persfinancier-blip/ai-runtime-lab.git HEAD`

failed before repository execution with:

`Could not resolve host: github.com`

The GitHub connector remains available for repository reads and normal Contents API writes. No GitHub Actions/workers were used as execution substitutes.

## Security conclusion

The direct public provider-history receipt mutation was a concrete post-construction provenance bypass and is now guarded at the narrowest live public mutation surface. The explicit migration confirmation bridge remains intentionally unguarded until marker confirmation completes, but it is preceded by LAB-092 full provider-history/runtime and activation-record integrity checks.

Exact behavioral RED→GREEN and full PR #177 test execution remain pending; do not mark PR #177 ready or integrate it until those gates actually execute.
