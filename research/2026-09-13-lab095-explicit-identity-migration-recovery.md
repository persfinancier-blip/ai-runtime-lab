# LAB-095 explicit database-identity migration/recovery slice — 2026-09-13

## Context
LAB-086 remained priority #1. A fresh direct clone probe failed before repository execution with `Could not resolve host: github.com` (exit 128), so no new LAB-086 executable/security PASS is claimed and its byte-exact gate remains unchanged.

The permitted fallback was LAB-095/#180 on draft PR #187.

## Implemented production slice
Added `experiments/provider_generation_history/database_identity_migration.py` on PR #187.

The explicit API now:
- requires ledger/history to resolve to the same physical path at migration time;
- runs existing `history.verify_durable()` and current-provider checks before installation;
- acquires `BEGIN IMMEDIATE` before deciding whether installation is truly absent;
- exact-checks/creates the existing LAB-095 custody schema inside that transaction;
- rechecks persisted bootstrap/current provider-history head while the writer lock is held, closing the supported rotation TOCTOU window between precheck and reservation;
- generates exactly 32 random bytes internally with `secrets.token_bytes(32)` only for a true absent state;
- atomically inserts local custody, one deterministic PREPARED identity intent, and advances the shared-anchor reserved tail in the same SQLite transaction;
- returns/reuses existing PREPARED/CONFIRMED work instead of creating another nonce/request;
- reconstructs the ordinary `Intent` from persisted custody and delegates external increment/reconciliation/CONFIRMED authentication to the existing `SharedAnchorLedger.execute()` mechanism;
- after external confirmation, finalizes the logical database identity locally from the persisted confirmed provider generation, position, request ID, and receipt binding;
- on retry after timeout/crash, reuses the same custody/request and allows already-CONFIRMED shared-anchor evidence to be reauthenticated by `SharedAnchorLedger.execute()` before local finalization.

Production does not import `tests/lab095_*`, accept caller-supplied nonce/digest authority, or create a second external-anchor protocol.

Published production commit: `5f0e2576798f069eeadeedc2ca808439c613750b`.
Published production blob: `9f3d3a9c31ffa45939393df67e624cd003b09475`.
The locally compiled production source was adjusted to the exact published text and `git hash-object` matched this blob.

## Regression source
Added `experiments/provider_generation_history/tests/test_database_identity_migration.py` in commit `092ebf04fef20558256af80dff0bfd117ca79ab8`, blob `be85be6534b24f24d3a664332377ade6696019ac`.

It covers:
1. fresh PREPARED installation and idempotent retry preserving the same nonce/request;
2. externally confirmed/local-prepared restart and local finalization without a new request;
3. ledger/history path divergence fail-closed;
4. provider-head mutation between precheck and writer-lock acquisition fail-closed.

## Execution actually performed
The full repository closure was not materialized in this runtime, so no full-repository LAB-095 GREEN is claimed.

A focused file-backed SQLite execution harness ran the exact published production migration source with narrow local stand-ins for the already-inspected database-identity/shared-anchor interfaces. Observed:
- fresh prepare + retry + finalization: PASS;
- confirmed-restart same-custody recovery: PASS;
- path-divergence rejection: PASS;
- provider-head TOCTOU rejection: PASS;
- production `py_compile`: PASS.

The repository regression source itself also passed `py_compile` locally and its local blob matched the published blob exactly.

## Audit finding fixed before publication
An initial draft verified provider history before acquiring `BEGIN IMMEDIATE` but did not re-read the provider-history head under the same writer lock used for the PREPARED reservation. A concurrent supported rotation could therefore have occurred between verification and reservation. The published module rechecks bootstrap, head generation, and head provider after locking and fails closed on drift.

## Remaining boundary
This slice still does not solve the original lifetime-rebinding acceptance criterion. `SharedAnchorLedger.path` and `DurableProviderHistory.path` remain public/mutable after construction. Next LAB-095 production work must make the physical DB reference private/non-rebindable across the composed supported objects and add DB-A -> DB-B regressions, then run the retained LAB-080/LAB-081/LAB-090/LAB-092 downstream gate before PR #187 can leave draft.
