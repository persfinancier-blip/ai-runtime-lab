# LAB-101 legacy integration adaptation — 2026-09-15

## Run observations

LAB-086 was probed first as required. `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository execution with `Could not resolve host: github.com`, exit 128. No LAB-086 PASS is claimed.

The GitHub connector remained available as the durable control plane. Exact repository materialization/execution was not available, so no pytest/compileall GREEN is claimed in this note.

## Objective resumed

PR #187 / LAB-101 had already introduced `migrate_activation_schema_v1()` as the explicit fresh/legacy path to exact LAB-092 COMPLETE provenance. The next durable handoff required adapting the older LAB-081 historical integration suite without weakening ordinary COMPLETE-only startup and without retaining pre-LAB-090 provider rotation semantics.

## Source audit

`experiments/provider_generation_history/tests/test_integration.py` still had two incompatible assumptions:

1. fresh tests constructed `SupportedHistoricalSharedAnchorLedger` directly, which is now intentionally rejected until LAB-092 provenance is COMPLETE;
2. provider rotation used `SignedAnchorProvider`, while composed LAB-090 `rotate_provider()` requires a `FencedActivationProvider` and exact activation-ticket lifecycle.

A third semantic consequence is important: explicit LAB-092 migration confirms its deterministic completion intent through the shared anchor, consuming position 1. Therefore old test expectations that the first ordinary user intent lands at position 1 are no longer valid.

## Change

PR #187 branch `lab-095-database-identity-red-intent` commit `0e8e47631a5e4ee40fa1e99ffc10e258ca47c827` updates only `experiments/provider_generation_history/tests/test_integration.py`:

- fresh setup now uses `migrate_activation_schema_v1()`;
- restart assertions continue to use the ordinary `SupportedHistoricalSharedAnchorLedger` constructor, proving tests do not bypass the COMPLETE startup gate after migration;
- all providers in this suite are `FencedActivationProvider` instances;
- candidate generation providers start at the exact current durable/provider position required by LAB-090 prepare fencing;
- position assertions account for the migration completion intent consuming position 1;
- historical receipt/restart verification assertions are retained;
- direct provider-history rotation remains blocked through the least-capability inspection view;
- PREPARED-vs-rotation and concurrent reserve-vs-rotation coverage is retained under fenced-provider semantics.

## Audit

The adaptation does not manually stamp LAB-092 CONFIRMED provenance, does not weaken `SupportedHistoricalSharedAnchorLedger.__init__()`, does not restore public mutable provider-history authority, and does not replace construction-bound history after startup.

The concurrency test still exercises the intended ordering: candidate activation preparation may race the shared-ledger reserve, but the pre-ack SQL transition rechecks the durable tail under `BEGIN IMMEDIATE`; if reserve wins, rotation must fail/abort rather than commit a stale handoff.

## Validation status

Source-level audit only in this run. Exact branch pytest/compileall remains pending because the branch cannot be materialized byte-for-byte into the executable filesystem with currently exposed capabilities. This commit is not a GREEN claim.

## Next action

After the mandatory LAB-086 transport probe, add LAB-101 end-to-end failure regressions on PR #187 for stale runtime, unrelated PREPARED intent, partial LAB-090 DDL, and failed confirmation/retry. Each regression must use the explicit migration surface and prove fail-closed state without weakening ordinary COMPLETE-only startup.
