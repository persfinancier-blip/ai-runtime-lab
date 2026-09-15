# LAB-095 / LAB-096 migration-only construction audit — 2026-09-15

## Scope

Audited PR #187 migration-only `object.__new__` construction in `experiments/provider_generation_history/activation_schema_migration.py`, specifically `_migration_reservation_surface()` and `_explicit_bootstrap_surface()`, against:

- LAB-095 construction-bound canonical database binding; and
- LAB-096 construction-bound provider-history strategy.

This is a source audit only. No executable GREEN is claimed.

## Runtime observation

LAB-086 was probed first with a direct `git clone --no-checkout`. It failed before repository code execution with `Could not resolve host: github.com`, exit 128. Exact repository materialization therefore remains unavailable in this run.

## Findings

### `_migration_reservation_surface()` preserves canonical DB binding

`CoordinatorOnlyProviderHistory` inherits `CanonicalDatabaseBinding` through its explicit `(CanonicalDatabaseBinding, IntegratedProviderHistory)` bases. Its first `history.path = path` assignment therefore canonicalizes the path into `_canonical_database_path`; subsequent public or private rebinding is rejected.

`SupportedHistoricalSharedAnchorLedger` reaches `CanonicalDatabaseBinding` through `HistoricalSharedAnchorLedger -> SupportedSharedAnchorLedger -> CanonicalDatabaseBinding`. Therefore the first `ledger.path = path` assignment on the `object.__new__` instance also canonicalizes and construction-binds the same input path.

The reservation surface does not assign either path a second time. Both migration authorities consequently retain independent immutable canonical references derived from the same caller input. No DB-A -> DB-B rebinding surface was found.

### `_migration_reservation_surface()` preserves construction-bound strategy

The first `ledger.provider_history = history` assignment invokes `SupportedHistoricalSharedAnchorLedger.provider_history` setter. With `_provider_history` absent, it requires exact `CoordinatorOnlyProviderHistory` and stores it in `_provider_history`. Later assignment to either `provider_history` or `_provider_history` is rejected by the supported class. The migration-only `object.__new__` path therefore does not bypass LAB-096 strategy custody.

### `_explicit_bootstrap_surface()` also preserves both boundaries

`CoordinatorOnlyProviderHistory(path, bootstrap)` runs the ordinary durable-history constructor on a canonical-binding subclass, so its inherited first `self.path = path` assignment becomes immutable canonical state.

The ledger then receives that exact history through the supported `provider_history` setter before `SharedAnchorLedger.__init__(ledger, path, attested)` runs. The base initializer's first ledger path assignment is intercepted by the supported ledger MRO's `CanonicalDatabaseBinding`, becoming the immutable canonical ledger path. This is deliberate first assignment, not rebinding.

The subsequent `_require_runtime_matches_durable_head()` and `verify_durable()` calls resolve history through `_history()`, which prefers `_provider_history`, so authority does not fall back to a caller-rebindable public strategy.

## Decision

No production change is justified by this audit. The deliberate `object.__new__` construction is unusual but does not create a concrete LAB-095 path-rebinding or LAB-096 strategy-rebinding defect under the current MRO/setter contracts.

Changing these surfaces merely to avoid `object.__new__` would increase bootstrap coupling without evidence of a correctness or security gain. Keep the current migration-only construction and retain focused regressions around canonical binding/strategy custody.

## Remaining risk / next action

The source proof depends on current MRO and first-assignment behavior, so exact execution remains required before closure. Next: source-audit every expected provider position in the adapted `test_database_path_binding.py` regression (migration completion at position 1, first ordinary intent at 2, generation-2 candidate tail at 2, post-rotation DB-A mutation at 3, independently migrated DB-B tail at 1). If exact materialization becomes available, verify retained blob/hash identity before running focused/downstream gates.
