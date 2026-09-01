# LAB-092 — public provenance verification must re-check authority/integrity before reauthentication

Date: 2026-09-01
Issue: #176
PR: #177 (`lab-092-activation-schema-provenance`)

## Finding

`ProvenancedHistoricalSharedAnchorLedger.verify_activation_schema_provenance()` classified the local schema/marker state and then called the inherited `execute()` for the already-CONFIRMED migration marker.

For a confirmed entry, inherited `execute()` calls `_reauthenticate()`. If the historical provider receipt is missing, LAB-090's `_reauthenticate()` may reconcile externally and persist a replacement `historical_provider_receipts` row before any fresh LAB-090 activation-record integrity check is performed.

Therefore post-construction tamper can produce mutation-before-integrity-failure:

1. construct a valid LAB-092 ledger;
2. delete only the migration marker's historical receipt;
3. inject a malformed historical `COMMITTED` activation row referencing a missing provider generation (this avoids the SQL_COMMITTED writer trigger);
4. call the public `verify_activation_schema_provenance()` method.

Before this fix, the public method had no fresh `_verify_activation_records()` precheck. The external marker reconcile/receipt-store path was reachable before activation integrity was rejected by any later operation.

## Regression-first change

Commit `5c0870ce25e461a31359843556e51efee60e708e` adds `test_public_verify_rechecks_activation_integrity_before_missing_marker_receipt_is_recreated` to `test_activation_schema_pre_auth_history_verification.py`.

The regression constructs/migrates a valid ledger, then performs the post-construction receipt deletion + malformed COMMITTED activation injection, calls `verify_activation_schema_provenance()`, requires `HistoricalVerificationError`, and asserts the missing marker receipt remains absent.

## Fix

Commit `16640c2d6ba8cd69d565982c47f7ff9f21fecfb8` changes the public verification method to perform both read-only checks already used by startup/migration confirmation before marker `execute()`:

- `_verify_confirmation_authority(self, self.attested)` — complete durable provider-history verification plus current-runtime generation check;
- `_verify_confirmation_activation_integrity(self)` — inherited LAB-090 `_verify_activation_records()`.

Only after both succeed may the method externally reauthenticate the confirmed marker.

Published `activation_schema_provenance.py` blob after the fix: `4c74336b9de27ae080411f1a8863862d3be63633`.

## Audit

The scope is intentionally small and reuses the same non-mutating verification helpers already established for constructor startup and explicit migration confirmation. It does not change migration classification, marker identity, DDL definitions, reservation semantics, provider activation recovery, or receipt cryptography.

The stronger public verification contract is appropriate because the method is explicitly a fresh provenance-verification API. A long-lived object cannot rely on constructor-time activation/provider-history verification after durable state may have changed.

## Execution evidence / limitation

Fresh exact branch execution was attempted first via direct `git clone`, but network resolution failed before repository code execution with `Could not resolve host: github.com`.

Accordingly, no RED→GREEN or branch-suite PASS is claimed in this run. GitHub connector re-fetch did confirm the published source method contains the two prechecks before `execute()` and reports blob `4c74336b9de27ae080411f1a8863862d3be63633`.

## Next action

When exact source execution is available, run `test_activation_schema_pre_auth_history_verification.py` first on PR #177 head, including the new public-method regression. If execution remains unavailable, audit whether the second `self.execute(_completion_intent())` in `__init__` after `super().__init__()` is redundant or creates another mutation/revalidation ordering surface; only change it if a reachable contract violation is demonstrated.
