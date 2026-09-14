# LAB-096 — transaction-atomic receipt provenance guard

Date: 2026-09-14

## Context

LAB-086 was probed first in this runtime. `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository execution with `Could not resolve host: github.com` and exit 128. No LAB-086 PASS is claimed.

Fallback work therefore continued on LAB-095/#180 + LAB-096/#181 draft PR #187.

## Finding

The prior `_store_receipt()` compatibility seam was not strong enough for LAB-092 provenance composition. A subclass could check activation-schema provenance and then call `super()._store_receipt()`, but the check and `CoordinatorOnlyProviderHistory.store_receipt()` occurred in separate SQLite transactions/connections. A concurrent schema/provenance mutation could therefore race between the guard and receipt persistence.

This is a real check/use gap for the intended LAB-092 requirement that COMPLETE provenance still hold immediately before receipt mutation.

## Patch

PR #187 now makes receipt persistence ledger-owned and transaction-atomic:

- `SupportedHistoricalSharedAnchorLedger._store_receipt()` opens `BEGIN IMMEDIATE` itself;
- `_guard_receipt_persistence_locked(q)` runs first inside that exact transaction;
- receipt verification uses the private construction-bound history strategy's `_verify_receipt_locked(q, receipt)` on the same connection;
- idempotency/substitution comparison and any insert happen in the same transaction;
- failures roll back before mutation.

This preserves LAB-096 least-capability requirements: no public live history strategy is reintroduced and no post-construction provider-history replacement is needed.

Branch commits:
- production: `7400348c670b0bdcb52547a871b6ee71eb61544f`;
- regression: `c66961c71a962ce69fb8d506c88c450c8291b44b` (current PR #187 head).

Published blobs:
- `experiments/provider_generation_history/supported.py`: `c478f7e8676b09a2b891f1e1eafd36e0b77224ca`;
- `experiments/provider_generation_history/tests/test_store_receipt_guard_hook.py`: `8a06ed8bcea2f85ff85c6b4fe6395b467c714c0b`.

## Validation actually executed

The authored production and regression files both passed local `python -m py_compile` before publication, and local `git hash-object` matched the returned GitHub content SHAs exactly.

An isolated execution of the exact authored bytes with inert import stubs ran the focused regression:

- guard + receipt verification + SELECT + INSERT + COMMIT used one identical fake connection under one `BEGIN IMMEDIATE`;
- provenance loss caused `ROLLBACK` before history verification or insert;
- result: **2/2 PASS**.

This is focused seam evidence only. It is not a full exact-repository LAB-095/LAB-096 GREEN claim because the runtime still lacks a supported byte-preserving connector-to-filesystem materialization path for the repository closure.

## Composition consequence for LAB-092

The composed LAB-092 implementation should override `_guard_receipt_persistence_locked(q)`, not `_store_receipt()`. Its COMPLETE classifier must inspect activation DDL + marker using the supplied locked connection `q`. This removes the earlier check/use window and keeps all mutation authority on the private construction-bound strategy.

The remaining LAB-092 changes are still:

1. route locked provider-history verification through `self._history()`;
2. remove `_bind_live_provider_history_provenance()` and all post-construction strategy replacement;
3. preserve `_reservation_surface()` only as a one-time construction surface;
4. carry LAB-090 activation fencing semantically after the LAB-095/LAB-096 authority base is stable.
