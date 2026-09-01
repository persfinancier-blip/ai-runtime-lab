# LAB-096 — provider-history strategy rebinding audit

Date: 2026-09-02

## Finding

`HistoricalSharedAnchorLedger.__init__()` stores the history helper in public mutable `self.provider_history`. This field is not passive metadata. Supported operations repeatedly dispatch security-relevant decisions and mutations through it after construction.

Observed call sites in `experiments/provider_generation_history/integration.py`:

- `reserve()` calls `self.provider_history._current_locked(q)` before inserting an intent;
- `rotate_provider()` calls `self.provider_history._rotate_locked(q, ...)` inside the ledger write transaction;
- `_require_runtime_matches_durable_head()` and `_runtime_matches_entry()` call `current()`;
- `_reauthenticate()` calls `current()`, `load_receipt()`, and `store_receipt()`;
- `verify_durable()` calls `_verify_durable_locked(q)` and `_load_receipt_locked(q)`.

Therefore a component delegated only the supported ledger can replace `ledger.provider_history` after construction and thereby replace the strategy/capability object trusted for provider-generation identity, history verification, receipt verification/storage, and rotation.

## Concrete security/correctness effect

This is stronger than rebinding one retained datum. A replacement object can alter authority decisions made inside otherwise supported ledger methods. In particular, permissive implementations of `_current_locked`, `_verify_durable_locked`, or `_load_receipt_locked` can supply arbitrary accepted results while the ledger continues opening and mutating its durable DB through its normal supported paths.

There is also a non-synthetic split-authority case using another legitimate `IntegratedProviderHistory`: transaction-internal helpers receive the ledger's already-open DB-A connection, while ordinary helper methods such as `current()`, `load_receipt()`, and `store_receipt()` open the replacement history object's own configured DB. After rebinding, which durable authority is consulted depends on which helper method is invoked. This can combine with, but is distinct from, the narrower mutable-bootstrap and mutable-path defects.

## Boundary against existing issues

- LAB-093/#178: caller-owned mutable `AttestedCatchup` / provider capability escapes through a delegated ledger.
- LAB-094/#179: the bootstrap trust-root datum inside one provider-history object is rebindable.
- LAB-095/#180: the durable database identity/path is rebindable.
- LAB-096/#181: the provider-history strategy/capability object itself is rebindable, replacing the trusted implementation used by ledger operations.

## Contract

The history helper used by a supported ledger should be construction-bound private state. All internal history/head/receipt/rotation/verification paths should use exactly that private object. If public introspection is required, expose only a read-only least-capability view and do not expose internal locked mutation/verification helpers.

The eventual fix should be reconciled with LAB-093/094/095 so the supported ledger has one construction-bound authority graph rather than several independently replaceable public aliases.

## Required regression-first proof

Before production changes, execute at least two pre-fix RED cases on exact source:

1. delegated-ledger strategy replacement with a deliberately permissive replacement proving that a supported authority decision or durable mutation can be changed after construction;
2. a legitimate DB-A ledger + legitimate DB-B `IntegratedProviderHistory` replacement demonstrating split authority without relying only on arbitrary monkeypatching.

Then prove post-fix rebinding cannot influence supported behavior, and run LAB-081/LAB-090/LAB-092 focused/downstream gates.

## Execution status

Source-level audit only. Direct Git transport in this run failed before repository execution with `Could not resolve host: github.com`. No fresh behavioral PASS/RED is claimed and no LAB-096 production code was staged.

Issue: #181.
