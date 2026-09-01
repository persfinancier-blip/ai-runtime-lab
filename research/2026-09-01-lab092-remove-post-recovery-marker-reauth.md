# LAB-092 — remove duplicate post-recovery marker reauthentication

Date: 2026-09-01

## Question

Does the second `self.execute(_completion_intent())` in `ProvenancedHistoricalSharedAnchorLedger.__init__()` add a necessary security check after `SupportedHistoricalSharedAnchorLedger.__init__()`, or does it create a redundant post-recovery reauthentication surface?

## Findings

The constructor already classifies the schema as `COMPLETE`, builds the non-mutating confirmation surface, verifies the full durable provider history and current runtime, verifies LAB-090 activation records, and authenticates the deterministic migration marker before invoking LAB-090 constructor recovery.

`SupportedHistoricalSharedAnchorLedger.__init__()` then performs its own runtime/head check, activation recovery, and activation-record verification. The following second `self.execute(_completion_intent())` does not strengthen the pre-recovery provenance boundary. It only repeats marker execution after recovery. If the historical marker receipt is removed in the intervening window, inherited LAB-090 historical `_reauthenticate()` can enter receipt-recovery/reconcile logic after activation recovery, recreating a mutation/revalidation surface that is unnecessary for object construction.

Decision: constructor marker authentication belongs only on the pre-recovery non-mutating confirmation bridge. Remove the second post-recovery `self.execute()` call. Public explicit provenance verification remains available through `verify_activation_schema_provenance()`, which performs fresh authority and activation-integrity checks before marker execution.

## Regression-first change

Commit `aca95c2c7a86fa139109d7aed3bb24b49024f406` adds `test_complete_restart_does_not_reauthenticate_marker_after_lab090_recovery`. The test creates a completed migration, then patches only `ProvenancedHistoricalSharedAnchorLedger.execute`; a COMPLETE restart must not call that subclass method after LAB-090 recovery.

## Fix

Commit `d05f7c7d7cf9a79182f03274042b25ec652bfa78` removes only the three-line duplicate post-recovery marker execution/check. GitHub commit diff confirms no other source change.

Current PR #177 head: `d05f7c7d7cf9a79182f03274042b25ec652bfa78`.

## Validation limits

A fresh direct `git clone` was attempted in this run and failed before repository code execution with `Could not resolve host: github.com`. Therefore no RED/GREEN unittest execution or branch-suite PASS is claimed. The authored regression source was syntax-compiled locally before publication, and the GitHub commit diffs were re-fetched to confirm exact scope.

## LAB-086 status

LAB-086 remains priority #1. Its issue #163 and `state/CURRENT.md` correctly identify the authoritative pending hidden-rowid lineage as predecessor `d4a6a40f...` + retained patch `61841b58...` -> exact target `b78e7c98...`. The older PR #165 body describes an earlier alternate-UNIQUE executable lineage and is not authoritative for the pending hidden-rowid publication. Direct git transport remains unavailable, and no safe byte-preserving composition bridge was observed in this run; no LAB-086 mutation was attempted.
