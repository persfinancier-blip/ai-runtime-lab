# LAB-091 constructor/adoption ordering correction

Date: 2026-08-28
Branch: `lab/091-mutable-shared-anchor-writer`

## Why this note exists

A prior source audit concluded that final LAB-091 persistent guards were installed before the inherited LAB-082 durable-history verifier ran, implying that a failed first adoption could leave LAB-091 triggers behind. A fresh full-MRO audit shows that conclusion was incorrect.

## Exact constructor path

The final class is `SupportedHistoryBoundOperationScopedAsymmetricSharedAnchorLedger`.
Its inherited constructor is `SupportedMutableAsymmetricSharedAnchorLedger.__init__()`:

1. `super().__init__(*args, **kwargs)`
2. `self._install_guards()`
3. `self.verify_durable()`

However step 1 is not an opaque lower construction. The inherited LAB-082 path reaches `SupportedSharedAnchorLedger.__init__()`, which itself executes:

1. `super().__init__(path, attested)`
2. `self.verify_durable()`

`self.verify_durable()` dynamically resolves to `AsymmetricHistoricalSharedAnchorLedger.verify_durable()` because no LAB-091 subclass overrides it. Therefore the complete LAB-082 provider-history / receipt / ledger verifier runs **before** control returns to `SupportedMutableAsymmetricSharedAnchorLedger.__init__()` and before `self._install_guards()` can commit LAB-091 triggers.

The dynamic `_init()` call from `SharedAnchorLedger.__init__()` does resolve to the final LAB-091 `_init()` override, but that override only calls `initialize_shared_anchor_schema(q)`. It creates/ensures the historical LAB-080 tables and singleton using restart-safe SQL; it does not install LAB-091 guard triggers or LAB-091 permit tables.

## Consequence

The previously claimed mechanism — `install guards -> lower verify fails -> guards persist` — is not reachable through the actual final constructor ordering. A corrupt LAB-082 receipt/history row should fail during the inner inherited `verify_durable()` before `_install_guards()` runs.

This invalidates the prior recommendation to reorder the constructor as `verify_durable() -> _install_guards() -> verify_durable()` for the purpose of preventing persistent guard side effects. Such a runtime change is not currently justified.

## Residual adoption side-effect question

The only pre-verification LAB-091-specific dynamic dispatch is `_init() -> initialize_shared_anchor_schema(q)`. On an existing LAB-080/LAB-082 database, its `CREATE TABLE IF NOT EXISTS` statements are no-ops and it only reads the existing metadata singleton. On a genuinely fresh database it creates the same historical LAB-080 tables that the lower constructor must create anyway.

A focused real-stack regression is still useful to lock this ordering contract:

- create a valid LAB-082 ledger and confirmed receipt;
- corrupt the durable receipt signature;
- attempt first construction through `SupportedHistoryBoundOperationScopedAsymmetricSharedAnchorLedger`;
- require `HistoricalVerificationError`;
- reopen with raw SQLite and assert there are zero `sqlite_master` triggers whose names begin with `lab091_`.

That test is a regression guard for future MRO/constructor edits, not evidence that the current constructor is defective.

## Decision

- Do **not** publish a constructor-ordering runtime change based on the superseded finding.
- Add the real-stack failed-adoption/no-trigger-persistence regression when exact branch-local execution is available.
- Continue LAB-091’s remaining real-stack two-worker/crash/timeout-UNKNOWN/reentrancy gate independently.

## Source evidence audited

- `experiments/mutable_shared_anchor_writer/real_integration.py`: inherited LAB-091 constructor.
- `experiments/mutable_shared_anchor_writer/history_bound_operation_scoped.py`: final `_init()` and `_install_guards()` overrides.
- `experiments/shared_anchor_intent_ledger/protocol.py`: `SharedAnchorLedger.__init__()` dynamic `_init()` call.
- `experiments/shared_anchor_intent_ledger/supported.py`: inherited restart-time `self.verify_durable()` call.
- `experiments/asymmetric_provider_history/integration.py`: complete LAB-082 `verify_durable()` implementation.
- `experiments/mutable_shared_anchor_writer/restart_safe_schema.py`: restart-safe schema initializer contains no LAB-091 guard installation.
