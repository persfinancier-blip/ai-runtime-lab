# LAB-096 least-capability provider-history view

Date: 2026-09-14

## Context

LAB-096/#181 requires the provider-history strategy used by a supported historical shared-anchor ledger to be construction-bound private state. The previous PR #187 slice prevented rebinding the strategy object but still returned that exact live `CoordinatorOnlyProviderHistory` through the public `provider_history` compatibility alias. Because the live object inherits transaction-internal helpers such as `_rotate_locked()`, a caller delegated only the ledger could combine the leaked strategy with `ledger._con()` and bypass `rotate_provider()` coordinator checks.

LAB-086 was probed first in this run as required. Direct `git clone` again failed before repository execution with `Could not resolve host: github.com` / exit 128. No LAB-086 PASS is claimed.

## Change on draft PR #187

Branch: `lab-095-database-identity-red-intent`

Commits produced in this run:

- `939c0f5de2ea0787165e5816c4f1bba2c31f02ed` — route `HistoricalSharedAnchorLedger` internal provider-history operations through `_history()`. The helper returns the construction-bound `_provider_history` when present and preserves the LAB-081 base behavior otherwise.
- `be494e1afa5f09cc4e04b5d133e44a43bd27dbb3` — add `ProviderHistoryInspectionView` and change supported `provider_history` to return only that read-only view. Supported internals now use `_history()` rather than the public alias.
- `0a14492c280c0fa6ed60ae20c8ea9f04144ade7a` — strengthen the delegated-ledger regression so the public view must not expose `rotate`, `_rotate_locked`, `_current_locked`, `_verify_durable_locked`, `_load_receipt_locked`, `store_receipt`, `_con`, `path`, or `bootstrap`; the view must also reject attribute assignment.

## Resulting authority split

`SupportedHistoricalSharedAnchorLedger` retains one construction-bound `CoordinatorOnlyProviderHistory` in `_provider_history`. Security-sensitive ledger paths use that exact private object via `_history()`:

- durable-head check;
- reservation under the ledger write lock;
- provider rotation under the ledger write lock;
- current-generation checks;
- receipt load/store used by reauthentication;
- durable history verification and confirmed-receipt verification.

The public `provider_history` surface is now an inspection facade exposing only read-only operations needed for compatibility: `current()`, `verify_durable()`, `load_receipt()`, `verify_receipt()`, `require_current()`, and pure `make_transition()` construction. It intentionally exposes no DB path/bootstrap state, connection constructor, receipt mutation, rotation API, or transaction-internal locked helper.

## Validation actually performed

The GitHub connector was used to conflict-check the exact current branch files before each Contents API write, and the written files were fetched back for source-level audit. The resulting source shows all retained security-sensitive internal call sites in the inspected `HistoricalSharedAnchorLedger` region dispatching through `_history()`, while the supported class returns the restricted inspection view.

No exact repository behavioral GREEN is claimed in this run. The executable runtime still cannot materialize the GitHub branch byte-for-byte: direct GitHub transport fails before repository code executes, and no supported connector-to-filesystem byte-preserving bridge is exposed. The PR must therefore remain draft until the retained exact execution gates run.

## Audit note

Python cannot provide a cryptographic object-capability boundary against arbitrary reflective access to name-mangled private state. The contract here is the supported/public API boundary used throughout these experiments: ordinary delegated access no longer exposes the live strategy or any named authority-changing helper. This patch does not claim to defend against a caller deliberately using Python reflection to violate private implementation boundaries; that would require a process/module isolation boundary rather than an object facade.

## Next exact gate

When a safe byte-preserving execution bridge is available:

1. materialize exact PR #187 head;
2. run `compileall`;
3. execute `test_provider_history_capability_surface.py` and `test_database_path_binding.py` under a journal-capable filesystem (`TMPDIR=/dev/shm` when needed);
4. run retained no-stub LAB-095 recovery/confirmed-finalize/locked-custody tests;
5. run LAB-081 then conflict-resolved LAB-090/LAB-092 downstream gates, preserving activation fencing, canonical DB binding, the construction-bound history strategy, and the least-capability public inspection view.

Keep PR #187 draft until those gates execute cleanly.
