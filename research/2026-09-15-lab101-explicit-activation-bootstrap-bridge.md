# LAB-101 explicit activation bootstrap bridge — 2026-09-15

## Objective
Restore a supported end-to-end path from a legitimate fresh/pre-LAB-090 database to LAB-092 `COMPLETE` without weakening the ordinary `SupportedHistoricalSharedAnchorLedger` COMPLETE-only startup gate.

## Runtime observation
LAB-086 was probed first with direct `git clone --no-checkout`. The shell failed before repository execution with `Could not resolve host: github.com`, exit 128. No LAB-086 PASS is claimed. Exact PR #187 pytest/compileall is likewise not claimed because no byte-preserving connector-to-executable-filesystem bridge was available.

## Implementation
PR #187 branch `lab-095-database-identity-red-intent` now exposes `migrate_activation_schema_v1()` in `activation_schema_migration.py`.

The explicit path:
1. constructs the exact construction-bound `CoordinatorOnlyProviderHistory` once;
2. initializes the shared-anchor base without invoking ordinary COMPLETE-only supported startup;
3. verifies historical durable state and runtime/current-head equality through the final historical ledger abstraction;
4. atomically installs exact LAB-090 table+trigger and reserves the deterministic LAB-092 PREPARED marker using the existing writer;
5. re-verifies durable history/runtime authority after PREPARED is committed;
6. confirms the exact migration intent through the ordinary authenticated shared-anchor execution path;
7. only after the marker is CONFIRMED invokes the normal `SupportedHistoricalSharedAnchorLedger` constructor.

No post-construction provider-history replacement was introduced. Canonical DB binding and private `_history()` remain the authority path.

## Audit correction during implementation
The first draft used `SupportedSharedAnchorLedger.__init__()` for the migration-only bootstrap. Audit found that its LAB-080 verifier rejects legitimate historical-generation confirmed rows because LAB-080 intentionally has no historical verification surface. That would break pre-LAB-090 databases that already contain provider rotations. The branch was corrected before handoff: bootstrap now invokes only `SharedAnchorLedger.__init__()` for schema initialization, then calls the final historical ledger's `verify_durable()` so historical receipts/generations remain authoritative.

## Regression committed
`tests/test_activation_schema_explicit_bootstrap.py` covers:
- fresh DB -> authenticated migration marker -> exact `COMPLETE` -> normal restart;
- retry after `COMPLETE` is idempotent and does not advance the provider again.

These tests are source-reviewed/committed but not execution evidence in this runtime.

## Commits
- initial bridge: `c687e256a1b22116fc6f33af25e3fb2f35a263cd`;
- historical-verification audit correction: `3784a93b853c921f952e3f16a981dc9cec7ce6e8`;
- focused regression: `6aec2aec3e7877c8d6c1594cb88a5b4225e139a5`.

## Remaining work
Adapt the legacy LAB-081 integration fixture through the explicit migration entrypoint. Because LAB-090 now requires fenced activation for provider rotation, that adaptation must not merely replace the constructor helper: rotation fixtures also need the composed LAB-090 provider semantics. Add stale-runtime, unrelated-PREPARED, partial-DDL, and failed-confirmation end-to-end regressions around the new bridge, then execute exact repository gates when materialization becomes available.
