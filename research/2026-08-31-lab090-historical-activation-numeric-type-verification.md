# LAB-090 historical activation numeric-type verification

Date: 2026-08-31

## Finding

`provider_generation_activations.expected_position` and `fence` use SQLite `INTEGER` affinity, but SQLite accepts non-integral REAL values in those columns. Historical `COMMITTED` activation rows are not reconciled against a live provider after a later generation becomes current, so `_verify_activation_records()` is the durable integrity boundary for those ticket fields.

The previous verifier normalized `expected_position` through `int()` while rebuilding the deterministic activation ID and only checked `fence < 1`. Therefore values such as `expected_position=0.5` and `fence=1.5` could survive as REALs and pass the historical verifier even though the provider activation contract defines both fields as exact integers.

A local file-backed SQLite mechanism check confirmed that `INTEGER NOT NULL` columns preserve `0.5` and `1.5` as storage class `real`.

## Regression

Published on LAB-090 PR #175:

- `experiments/provider_generation_history/tests/test_activation_historical_numeric_types.py`
- commit `c39bb4f89042f3c8171e534f3c389716f80da5f8`

The regression constructs valid G1 -> G2 -> G3 rotations, mutates historical committed G2 ticket numbers to non-integral REALs, and requires restart on current G3 to fail with `HistoricalVerificationError`.

## Fix

Published on PR #175:

- commit `71c22a2054b983839b760edf21ceedc77ad0bc6b`
- `supported.py` blob `fb2bab4a262f295ef6a9b87cee459547038a0da9`

The historical verifier now requires:

- exact `int` `expected_position` and value >= 0;
- exact `int` `fence` and value >= 1.

GitHub commit diff confirms the production change is limited to these two validation guards.

## Validation status

- SQLite storage-class mechanism check: PASS (`0.5`/`1.5` persist as REAL under INTEGER affinity).
- GitHub commit diff audit: PASS; only the intended verifier lines changed.
- Exact branch behavioral unittest/full downstream gate: not claimed in this run because direct repository execution transport remains unavailable.

## Boundary

This is fail-closed durable-integrity hardening only. It does not alter provider-generation authority, activation lifecycle states, or fence allocation semantics.
