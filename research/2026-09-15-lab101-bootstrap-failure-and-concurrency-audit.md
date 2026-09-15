# LAB-101 explicit bootstrap failure + concurrency audit

Date: 2026-09-15

## Runtime observation

LAB-086 was probed first with direct `git clone --no-checkout`. The shell failed before repository execution with `Could not resolve host: github.com` (exit 128). No LAB-086 PASS is claimed. The connector still provides source/control-plane access but no supported byte-preserving repository-to-executable-filesystem materialization path was observed, so no exact pytest/compileall GREEN is claimed.

## PR #187 work

Branch: `lab-095-database-identity-red-intent`

Added `tests/test_activation_schema_explicit_bootstrap_failures.py` covering four LAB-101 failure/recovery boundaries:

1. partial LAB-090 DDL fails closed without creating the deterministic migration marker;
2. an unrelated PREPARED shared-anchor intent blocks migration and remains authoritative;
3. a stale generation-1 runtime against a durably advanced generation-2 history fails before activation reservation;
4. an injected failure at authenticated confirmation leaves exact PREPARED provenance and a retry deterministically reaches COMPLETE without consuming an external position during the failed attempt.

Initial test source was audited immediately. Two setup defects were corrected before handoff: `reserve()` requires an `Intent`, and stale-runtime setup must advance history through the transaction-internal `_rotate_locked` mechanism because the supported public history view intentionally blocks direct rotation.

## Legacy concurrency audit

Audited the newly adapted LAB-081 integration fixture against LAB-090 prepare/abort ordering.

Found two incorrect assumptions in the prior adaptation:

- the PREPARED-vs-rotation fixture used `entry.predecessor_position` for the candidate provider, which prevents provider prepare before the intended SQLite PREPARED check; it now uses `entry.position`, proving prepare succeeds and the rejected SQL transition aborts the exact provider ticket;
- reserve-vs-rotation unconditionally loaded entry `r` and assumed only `PendingRotationBlocked` on a losing rotation. Under LAB-090 fencing, a reserve can move the reserved tail before provider prepare, causing safe `AnchorMismatch` before a ticket exists; conversely a reserve after successful rotation can legitimately bind generation 2. Assertions now accept only these safe serialized outcomes and require no leaked candidate activation fence after failed rotation.

Current branch head after audit: `ab2a5cba273ad8b04b5ee866665acea20291c66c`.

## Validation status

Source/API audit only. Exact repository tests were not executed in this runtime; no GREEN claim.

## Next action

Probe LAB-086 first. If still transport-blocked, source-audit the new failure regressions against the exact provenance classifier states (especially expected classification for partial DDL and PREPARED), then inspect whether `migrate_activation_schema_v1()` should normalize provider-side `PendingIntent`/unknown-outcome confirmation failures for retry semantics. If source remains coherent, continue LAB-095 eight-file reconstruction/hash verification work that can be done through connector-visible content without claiming executable validation.
