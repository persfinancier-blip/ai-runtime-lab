# LAB-092 supported-constructor compatibility audit — bootstrap gap

Date: 2026-09-15

## Run observation

LAB-086 was probed first with direct `git clone --no-checkout`. Transport failed before repository execution with `Could not resolve host: github.com`, exit 128. No LAB-086 PASS is claimed.

## Audit target

Per `state/CURRENT.md`, audit existing supported-ledger constructor tests after PR #187 made LAB-092 exact `COMPLETE` provenance a prerequisite for `SupportedHistoricalSharedAnchorLedger.__init__()`.

The main LAB-081 integration suite (`experiments/provider_generation_history/tests/test_integration.py`) constructs a fresh supported historical ledger directly in its `ledger()` helper. Those call sites cannot be mechanically changed to invoke the current PR #187 migration writer first.

## Finding

PR #187 currently has two individually sensible pieces that do not yet compose into an end-to-end bootstrap path:

1. `SupportedHistoricalSharedAnchorLedger.__init__()` calls `require_complete_activation_schema_provenance_for_startup(path)` before provider-history/shared-ledger construction or LAB-090 recovery. This preserves the intended read-only ordinary-startup gate.
2. `install_and_reserve_activation_schema_v1()` requires an already-existing `shared_anchor_intents` ledger and durable provider history, verifies them under `BEGIN IMMEDIATE`, installs exact activation DDL if legitimately absent, and reserves the deterministic LAB-092 marker as `PREPARED`. It deliberately stops before authenticated confirmation.

Therefore a legitimate fresh database cannot be constructed by the normal supported class (it is not `COMPLETE`), while the explicit migration writer cannot run first because the shared ledger/history do not exist. A legitimate pre-LAB-090 database can reach PREPARED through the writer, but PR #187 does not currently expose the donor's authenticated confirmation bridge that executes the exact completion intent and returns a normal supported ledger.

This means the compatibility work requested by the previous handoff is blocked by a real production API gap, not merely stale test setup. Weakening the startup gate or manually stamping a CONFIRMED row in tests would invalidate LAB-092's authority contract.

## Donor comparison

Draft PR #177 had `ProvenancedHistoricalSharedAnchorLedger.migrate_activation_schema_v1()` with the missing conceptual sequence:

- classify recoverable legacy state;
- atomically install DDL + reserve deterministic PREPARED marker;
- verify full provider history/runtime authority;
- verify activation integrity;
- execute the exact completion intent to obtain authenticated CONFIRMED evidence;
- only then construct the ordinary supported ledger.

That donor relied on the older pre-gate LAB-090 constructor to establish the initial legacy database, and it also used provider-history replacement mechanisms intentionally removed by LAB-096 composition. It therefore cannot be copied wholesale.

## Decision

Do not modify the legacy integration tests yet and do not weaken `require_complete_activation_schema_provenance_for_startup()`.

Create LAB-101/#188 for a minimal construction-bound explicit bootstrap/migration entrypoint compatible with PR #187's private `_history()`, canonical DB binding, and no post-construction strategy replacement. After that entrypoint exists, adapt `test_integration.py` and other direct fresh-constructor tests through it.

## Validation status

This is a source/control-flow audit only. Exact PR #187 pytest/compileall remains unavailable because byte-exact repository materialization into the executable filesystem is not exposed in this run. No behavioral GREEN is claimed.
