# LAB-096 / LAB-092 provider-history composition audit

Date: 2026-09-14

## Scope

Static cross-draft audit of LAB-095/LAB-096 draft PR #187 against LAB-092 draft PR #177, focused on the construction-bound provider-history strategy and least-capability public history view.

No exact repository behavioral GREEN is claimed in this note. This is source/patch audit evidence only.

## Current LAB-096 contract on PR #187

PR #187 now gives `SupportedHistoricalSharedAnchorLedger` one construction-bound private `CoordinatorOnlyProviderHistory` in `_provider_history`. Ledger-internal security-sensitive paths resolve it through `_history()`. The public `provider_history` property returns a `ProviderHistoryInspectionView` that intentionally omits connection access, receipt mutation, locked helpers, and rotation authority.

Within the exact current PR #187 branch sources inspected in this run:

- `HistoricalSharedAnchorLedger._require_runtime_matches_durable_head()` uses `_history().current()`;
- `reserve()` uses `_history()._current_locked(q)`;
- `rotate_provider()` uses `_history()._rotate_locked(q, ...)`;
- runtime/receipt reauthentication uses `_history().current()/load_receipt()/store_receipt()`;
- durable verification uses `_history()._verify_durable_locked(q)` and `_history()._load_receipt_locked(q, ...)`;
- supported receipt helpers likewise use `_history()`.

No remaining direct `self.provider_history` use was found in those PR #187 LAB-081/internal security-sensitive paths.

## LAB-092 conflict found

Draft PR #177 adds `activation_schema_provenance.py` with helper paths that assume the pre-LAB-096 public live-strategy model.

### 1. Reservation helper constructs a live history strategy through the public slot

`_reservation_surface()` creates both objects with `object.__new__`, assigns `history.path` / `history.bootstrap`, then performs:

```python
ledger.provider_history = history
```

Under LAB-096, the supported ledger's provider-history strategy is construction-bound private state and the public property is a least-capability inspection view. Any LAB-092 reservation/migration helper must therefore establish the private strategy through an audited construction/bootstrap path rather than restore the old public mutable strategy slot.

### 2. Confirmation helpers call locked authority through the public history handle

`_verify_confirmation_authority()` calls:

```python
ledger.provider_history._verify_durable_locked(q)
```

`_install_and_reserve_prepared()` makes the same direct public locked call.

After LAB-096 the public history view intentionally does not expose `_verify_durable_locked`; internal authority checks must use the construction-bound private strategy via `_history()` or a narrower explicit internal helper.

### 3. LAB-092 deliberately replaces the live provider-history object after construction

`_bind_live_provider_history_provenance()` creates `_ProvenanceBoundCoordinatorOnlyProviderHistory` with `object.__new__` and then assigns:

```python
ledger.provider_history = history
```

This is directly incompatible with LAB-096's acceptance contract. Whole-object strategy replacement is the bypass LAB-096 exists to remove. Re-introducing replacement only for provenance wrapping would reopen split-authority/rebinding semantics.

### 4. Provenance enforcement currently lives in a replacement subclass

`_ProvenanceBoundCoordinatorOnlyProviderHistory.store_receipt()` enforces `_classify(self.path) == "COMPLETE"` before receipt mutation. The intended security property is valid, but the mechanism must change under LAB-096.

The provenance guard should be composed into the single construction-bound strategy (or enforced by the owning ledger before the private strategy mutation), not implemented by swapping a new history object into the ledger after construction.

## Required conflict-resolution contract

When LAB-092 is rebased/composed with LAB-095/LAB-096:

1. Preserve exactly one construction-bound provider-history strategy for the ledger lifetime.
2. Do not assign a live strategy through public `ledger.provider_history` after initial audited binding.
3. Convert LAB-092 locked/internal history calls to `_history()` or a narrower internal method.
4. Preserve LAB-092's post-provenance-loss receipt-mutation fail-closed behavior without whole-object strategy replacement.
5. Preserve `CanonicalDatabaseBinding` on the private history strategy and ledger.
6. Preserve LAB-090 activation fencing semantics and LAB-092 migration/read-only-startup semantics.
7. Public `provider_history` must remain the least-capability inspection view; do not re-export `path`, `bootstrap`, `_con`, locked helpers, `store_receipt`, or rotation.
8. Re-run LAB-092 migration/restart/concurrency tests plus LAB-095 DB-A→DB-B and LAB-096 capability-surface regressions on the final composed tree.

## Additional control-plane observation

The generic `get_pr_info` snapshot transiently reported PR #187 `mergeable=false`, but a direct current GitHub PR resource read in the same run reported `mergeable=true`, `rebaseable=true`, `mergeable_state=clean`. The direct PR resource is treated as the current authoritative observation. No integration was attempted because PR #187 remains intentionally draft pending exact behavioral/downstream gates.

## Decision

Do not patch PR #177 independently yet. The correct integration point is the eventual conflict-resolved LAB-090/LAB-092 + LAB-095/LAB-096 composed tree. Record this as a required downstream gate, not as a reason to weaken LAB-096 strategy immutability.
