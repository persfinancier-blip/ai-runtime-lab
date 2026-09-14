# LAB-096 receipt guard seam + LAB-092 reservation-surface audit

Date: 2026-09-14

## Context

LAB-086 remains the first-priority executable gate. In this run, direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` again failed before repository execution with `Could not resolve host: github.com` (exit 128). No LAB-086 PASS is claimed.

The permitted fallback is LAB-095/#180 plus composed LAB-096/#181 on draft PR #187.

## Receipt-persistence guard seam

PR #187 already owns receipt persistence through private ledger hook:

```python
def _store_receipt(self, receipt: HistoricalReceipt):
    return self._history().store_receipt(receipt)
```

and `_reauthenticate()` calls that hook immediately before comparing the persisted stable binding.

A focused regression was added on branch `lab-095-database-identity-red-intent`:

- `experiments/provider_generation_history/tests/test_store_receipt_guard_hook.py`
- commit `fe2c39e964d3abd5b4028053b0828febe54307ba`
- blob `d00af7540cc23410859fbb62f34bffd349020ba8`

The test subclasses `SupportedHistoricalSharedAnchorLedger`, overrides `_store_receipt(receipt)` with a LAB-092-style provenance guard, and overrides `_history()` to raise if the private strategy is touched. With provenance denied, `_store_receipt()` must raise the guard exception before `_history()` is reached.

This proves the compatibility seam does not require passing, exposing, or replacing the private provider-history strategy in order to perform a last-moment fail-closed provenance check.

Validation actually executed in this run:

- `python -m py_compile` on the exact authored test: PASS;
- local `git hash-object`: `d00af7540cc23410859fbb62f34bffd349020ba8`;
- post-publication GitHub refetch reports the same blob SHA.

This is syntax/byte-identity evidence only. The full branch behavioral suite remains unexecuted because the exact repository closure cannot currently be materialized into the executable filesystem.

## LAB-092 `_reservation_surface()` construction audit

PR #177 currently constructs a migration-only reservation surface with `object.__new__` and manual first assignments:

```python
ledger = object.__new__(SupportedHistoricalSharedAnchorLedger)
ledger.path = str(path)
...
history = object.__new__(CoordinatorOnlyProviderHistory)
history.path = str(path)
history.bootstrap = bootstrap
ledger.provider_history = history
```

Against PR #187's authority structure:

1. `SupportedHistoricalSharedAnchorLedger.__setattr__` delegates non-history fields to its MRO;
2. both the ledger-side and history-side classes inherit `CanonicalDatabaseBinding`;
3. the first `path = ...` assignment therefore canonicalizes and installs `_canonical_database_path` exactly once;
4. later public `path` or private `_canonical_database_path` rebinding is rejected;
5. `ledger.provider_history = history` is accepted only once and only when `type(history) is CoordinatorOnlyProviderHistory`.

Therefore the *one-time construction shape* of `_reservation_surface()` is compatible with LAB-095 canonical path binding and LAB-096 exact private history installation, provided composition preserves those exact classes/MROs.

The already-published PR #187 regression `test_database_binding_object_new_surface.py` independently covers the `object.__new__ -> first bind -> rebinding rejected` path contract.

## Remaining incompatibility in LAB-092

The unsafe portion of PR #177 is still post-construction replacement, not the initial reservation-surface bind:

- `_bind_live_provider_history_provenance()` constructs `_ProvenanceBoundCoordinatorOnlyProviderHistory` and assigns it after supported construction;
- this conflicts with PR #187 exact-type construction-bound history strategy;
- locked history operations in PR #177 still dispatch through public `ledger.provider_history` rather than private `_history()`.

Final composition should therefore:

1. retain PR #187 as the structural authority base;
2. keep `_reservation_surface()` only as a tightly scoped one-time migration constructor that binds canonical path + exact private history once;
3. remove `_bind_live_provider_history_provenance()` entirely;
4. move LAB-092 last-moment provenance enforcement to the ledger-owned `_store_receipt()` override;
5. route locked/internal history calls through `_history()`;
6. then layer LAB-090 activation fencing semantics without selecting PR #175/#177 whole files wholesale.

## Current decision

No new owner decision is needed. The minimal receipt guard regression is safe to retain on draft PR #187. Exact behavioral GREEN and downstream LAB-081/LAB-090/LAB-092 gates remain mandatory before integration.
