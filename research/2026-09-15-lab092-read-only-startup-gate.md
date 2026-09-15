# LAB-092 read-only startup provenance gate

Date: 2026-09-15

## Runtime observation

LAB-086 was probed first. Direct `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository execution with `Could not resolve host: github.com`, exit 128. No LAB-086 PASS is claimed.

## Source audit

PR #177 ordinary startup classifies activation-schema provenance before inherited construction and treats `LEGACY_ABSENT`, `DDL_INSTALLED_UNMARKED`, and `DDL_INSTALLED_PREPARED` as explicit-migration-only states. Its original implementation also contains source-incompatible LAB-096 patterns: post-construction provider-history replacement and locked history access through the public handle. Those patterns are not carried forward.

## Implemented on PR #187

Added `activation_schema_startup.py` as an opt-in LAB-092 startup layer over the already-composed locked classifier.

Properties:
- path-level classification opens only a short-lived read transaction and delegates to `classify_activation_schema_provenance_locked(q)`;
- startup accepts only `COMPLETE`;
- `LEGACY_ABSENT`, `DDL_INSTALLED_UNMARKED`, and `DDL_INSTALLED_PREPARED` raise `ActivationSchemaMigrationRequired`;
- unknown/non-contract states fail closed with `HistoricalVerificationError`;
- `ActivationSchemaProvenanceStartupMixin` runs the gate before inherited constructor side effects;
- the module contains no DDL installation, migration-marker write, provider-history reference, history replacement, or mutation-authority recovery.

The mixin intentionally remains opt-in. Wiring it into the default supported ledger before LAB-090 activation installation/fencing and the explicit LAB-092 migration writer are composed would make legitimate pre-composition construction unusable.

Branch commits:
- production: `a97f37a5af49cc3e475660b0f98d46982a9d37c4`;
- regression initial: `53a56e90ab382cf0e18772e01c389fed478b80f4`;
- regression correction/current head: `0e6a56ec7e68b962344f8f8f797960456b99bd21`.

The initial test attempted to inspect `sqlite3.Connection.in_transaction` after the wrapper had correctly closed the connection; Python raises `ProgrammingError` for that observation. The regression was corrected to assert classifier invocation plus unchanged schema instead. This is a test defect correction, not a production change.

## Validation boundary

The exact repository closure is still unavailable in the executable filesystem, so no exact-branch pytest GREEN is claimed. The new files are small/file-scoped and were published through the normal Contents API after source inspection. Full execution remains pending a safe byte-preserving bridge.

## Next composition step

Implement the explicit migration writer as a separate opt-in LAB-092 layer. It must preserve one-time canonical path binding, install exactly one construction-bound `CoordinatorOnlyProviderHistory`, use private `_history()` for every locked history verification, atomically install exact activation DDL + reserve the deterministic PREPARED migration marker, and never use `_bind_live_provider_history_provenance()` or replace `_provider_history` after construction. Keep activation fencing behavior itself for the subsequent LAB-090 semantic port.
