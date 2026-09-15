# LAB-092 supported startup ordering audit — 2026-09-15

## Scope
Audit PR #187 constructor ordering after LAB-090 restart recovery was composed into `SupportedHistoricalSharedAnchorLedger`.

## Finding
Before this audit, `SupportedHistoricalSharedAnchorLedger.__init__()` constructed `CoordinatorOnlyProviderHistory`, initialized the supported shared-anchor ledger, verified runtime/durable head, and then called `_recover_pending_activation()`. The LAB-092 read-only startup classifier existed only as an opt-in mixin and was not on this supported constructor path.

That ordering allowed LAB-090 recovery to query `provider_generation_activations` without first proving the exact LAB-090 activation table/trigger and CONFIRMED migration marker were present. On an absent/unmarked/partial schema, behavior could therefore be an incidental SQLite error or an unclassified read rather than the explicit LAB-092 migration contract.

## Fix
PR #187 now calls `require_complete_activation_schema_provenance_for_startup(path)` immediately after exact `AttestedCatchup` type validation and before constructing `CoordinatorOnlyProviderHistory` or any supported ledger initialization/recovery.

Consequences:
- `COMPLETE` proceeds to history construction and LAB-090 recovery;
- `LEGACY_ABSENT`, `DDL_INSTALLED_UNMARKED`, and `DDL_INSTALLED_PREPARED` raise `ActivationSchemaMigrationRequired` and require explicit `migrate_activation_schema_v1()`;
- invalid/corrupt provenance states fail closed as `HistoricalVerificationError`;
- recovery cannot be the first consumer of an uninstalled/unconfirmed activation schema.

## Audit correction during implementation
An initial edit added `ActivationSchemaProvenanceStartupMixin` to the class MRO. A separate audit immediately caught that `SupportedHistoricalSharedAnchorLedger` defines its own `__init__`, so the mixin initializer would not execute. That edit was superseded in the same run by an explicit call at the top of the concrete constructor. Current production commit on PR #187: `f67eec5e274767e38c58d70bcc0c172980e3e81b`.

## Validation status
Direct LAB-086 clone was probed first and failed before repository execution with `Could not resolve host: github.com`, exit 128. The exact PR #187 repository closure could not be materialized into the executable filesystem, so no pytest/compileall GREEN is claimed for this change.

Source audit confirms the classifier call textually precedes provider-history construction, supported-ledger initialization, runtime/head verification, and `_recover_pending_activation()` in the concrete constructor. Behavioral regression execution remains required when byte-preserving materialization becomes available.

## Next regression slice
Add focused restart regressions for:
1. `SQL_COMMITTED` + provider `PREPARED`;
2. `SQL_COMMITTED` + provider `COMMITTED_FENCED`;
3. premature provider `RELEASED`;
4. provider reservation `ABSENT`;
5. historical non-current `SQL_COMMITTED`.

Each test must begin from exact COMPLETE LAB-092 provenance (or explicitly run the migration writer) so it tests recovery rather than bypassing the startup contract.