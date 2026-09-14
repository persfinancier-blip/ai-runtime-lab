# LAB-096 public provider-history alias leaks coordinator mutation helpers

Date: 2026-09-14

## Context

LAB-086 remained the first execution priority. A fresh direct `git clone` probe failed before repository execution with `Could not resolve host: github.com` / exit 128, so no new LAB-086 executable PASS is claimed.

Fallback work resumed LAB-095/#180 + LAB-096/#181 on draft PR #187.

## Finding

PR #187 head `af0ed4cfafc830628ee80905ca2809158f546965` made the provider-history strategy construction-bound, but the public compatibility property still returned the exact live `CoordinatorOnlyProviderHistory` object.

That object blocks its public `rotate()` method, but it inherits the transaction-internal mutation helper `_rotate_locked()` from `IntegratedProviderHistory`. The delegated supported ledger also exposes `_con()`. A caller holding only the supported ledger can therefore recover the live history strategy through `ledger.provider_history`, obtain a ledger DB connection with `ledger._con()`, start `BEGIN IMMEDIATE`, and call `history._rotate_locked(...)` directly.

This bypasses `SupportedHistoricalSharedAnchorLedger.rotate_provider()` and therefore bypasses its coordinator checks, including the shared-ledger PREPARED-intent gate, runtime/new-attested validation, provider-position observation, and normal runtime-handoff sequence.

This is a concrete LAB-096 acceptance failure, not merely LAB-093 least-capability hygiene: the public alias exposes an authority-changing helper of the construction-bound strategy itself.

## Regression-first change

Added `experiments/provider_generation_history/tests/test_provider_history_capability_surface.py` on PR #187.

The regression requires:

1. the intentionally blocked public `provider_history.rotate()` to continue failing;
2. the public history alias to be unable to drive `_rotate_locked()` even when given a ledger-owned transaction;
3. the durable provider generation and runtime generation to remain at generation 1.

Branch commit: `c3ce17f160ad157213fc931bd4fe1fec290353e5`.

The authored test file was locally syntax-compiled with `python -m py_compile` successfully. The exact repository regression was not executed because the current runtime still cannot materialize the repository closure byte-for-byte into the executable filesystem. The test is therefore a committed RED contract, not claimed behavioral evidence.

## Required production direction

Do not keep returning the live `CoordinatorOnlyProviderHistory` as a supposedly read-only compatibility alias.

The minimal coherent design is to separate the internal construction-bound strategy from the public inspection surface:

- internal ledger code uses a private strategy accessor/source (`_provider_history` or equivalent);
- public `provider_history` returns a least-capability read-only view that cannot expose `_con`, `_rotate_locked`, receipt mutation/storage helpers, bootstrap/path authority slots, or other internal mutation/verification machinery;
- existing diagnostics that genuinely need `current()` may be preserved through explicit immutable/read-only data access;
- do not fold caller-owned external provider capability work from LAB-093 into this patch unless required by a demonstrated bypass.

Because inherited `HistoricalSharedAnchorLedger` methods currently dispatch through `self.provider_history`, implementing the view safely likely requires a small internal-access refactor in `integration.py` rather than only wrapping the property in `supported.py`.

## Next validation

After the production refactor:

- execute the new capability-surface regression against exact PR #187 bytes;
- retain the DB-A/DB-B whole-object replacement regression;
- run the no-stub LAB-095 recovery/confirmed-finalize/locked-custody suite;
- run LAB-081 and conflict-resolved LAB-090/LAB-092 downstream gates.
