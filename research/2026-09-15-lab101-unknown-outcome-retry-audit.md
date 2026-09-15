# LAB-101 unknown-outcome retry audit — 2026-09-15

## Runtime observation

LAB-086 was probed first with `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git`. The command failed before repository code execution with `Could not resolve host: github.com`, exit 128. No LAB-086 PASS is claimed.

## Source audit

PR #187 activation provenance classification is exact for the failure states covered by LAB-101:

- exact table + exact trigger + deterministic PREPARED marker => `DDL_INSTALLED_PREPARED`;
- exact table + exact trigger + deterministic CONFIRMED marker => `COMPLETE`;
- a marker whose identity/content/status is not the deterministic migration intent raises `HistoricalVerificationError`;
- partial/mismatched DDL is not normalized into a recoverable state.

The existing confirmation-failure regression only injected failure *before* the external provider effect. That did not cover the important UNKNOWN window where the provider increment commits but the caller observes a timeout before SQLite confirmation.

`SharedAnchorLedger.execute()` already has the required idempotent mechanism: a timeout after provider commit is surfaced as `PendingIntent`; the durable row remains PREPARED; retry uses the same deterministic request id, and provider reconciliation binds the already-committed position/request before CONFIRMED is persisted.

## Change

Added `test_unknown_outcome_confirmation_retry_reconciles_without_double_increment` on PR #187.

The regression injects the real `timeout_after_commit=True` path for the deterministic LAB-092 completion intent, then requires:

1. first migration attempt raises `PendingIntent`;
2. external provider position is exactly 1;
3. provenance is exactly `DDL_INSTALLED_PREPARED` and marker remains PREPARED;
4. retry through the same explicit migration entrypoint reaches COMPLETE;
5. provider position remains exactly 1, proving no duplicate external increment;
6. deterministic marker becomes CONFIRMED.

Branch commit: `c69eb116e78ac85b4983ddb0499131210ddcacc9`.

## Validation boundary

This is a source-level regression and audit, not executable GREEN. Exact repository materialization remains unavailable in this runtime because direct GitHub transport is DNS-blocked and no byte-preserving connector-to-filesystem bridge is exposed.

## Next action

Probe LAB-086 first next run. If still blocked, resume LAB-095 eight-file reconstruction/hash verification from connector-visible authoritative PR #187 content, prioritizing the database-binding/identity production files before reference tests. Do not claim exact pytest/compileall GREEN without executable byte-exact materialization.
