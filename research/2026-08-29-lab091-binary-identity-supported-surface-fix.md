# LAB-091 binary identity supported-surface fix

Date: 2026-08-29

## Finding

The previously reproduced adoption/runtime mismatch was broader than `reserve()`: a legacy protected identity column can retain `COLLATE NOCASE` while a separate BINARY UNIQUE index satisfies LAB-091's canonical identity-key check. Any supported predicate written as `WHERE identity=?` then inherits the legacy column collation and can alias byte-distinct identities.

Reachable final-surface inventory found affected paths for:
- `shared_anchor_intents.intent_id`: reserve/read/reconciliation/confirmation CAS and inherited `entry()`;
- `component_anchor_watermarks.component_id`: inherited `watermark()`, verification read and update CAS;
- `asymmetric_provider_receipts.request_id`: inherited LAB-082 load/maybe-load/store helpers;
- v2 freshness guards for intent ID, request ID, component ID and receipt request ID.

The already-hardened v3/v4 receipt cross-table predicates use explicit BINARY collation and did not need another change.

## Fix

Branch `lab/091-mutable-shared-anchor-writer` now makes byte identity explicit instead of parsing `sqlite_schema` declarations:

- `binary_identity_provider_history.py` introduces final-surface receipt load/maybe-load/store helpers with `COLLATE BINARY` request matching; blob `d412d3b6abb70b5947243dcf5988314733f6f6df`.
- `history_bound_operation_scoped.py` installs that helper for the final class and overrides `entry()` / `watermark()` with explicit BINARY identity reads; blob `5cb106fc26ac79d0f7c09c732b176b17ac4665f0`.
- `operation_scoped_integration.py` makes all reachable final intent and watermark lookup/CAS predicates BINARY; blob `577979b1c3643c6232fd76cccd942429214542ca`.
- `convergent_operation_scoped.py` makes loser/winner confirmation lookup/CAS BINARY; blob `f93e67f8140782aec824fb4057832d568c761712`.
- `full_operation_guards.py` makes freshness checks for intent/request/component/receipt identities BINARY; blob `6ff1f5eedac80c524163a7e78ea03cd1f0460742`.
- regression `test_identity_lookup_collation_regression.py` is blob `c35c4280d26ba7c90a88a891fbce697c83ffb7f5`.

Current PR #173 head after publication: `0d73b6bc4d51e8dc018627bd1df1dc2b7ddd0383`.

## Executed evidence in this run

A focused local SQLite semantic probe used NOCASE identity columns plus separate BINARY UNIQUE indexes. It reconfirmed the old alias for ordinary predicates and proved the new predicate form distinguishes case-distinct intent, component and receipt identities. A BINARY freshness trigger allowed a genuinely byte-distinct lower-case identity while rejecting an exact duplicate. Result: PASS.

This is mechanism evidence only. The exact published pytest regression and the complete final-class real-stack gate were not executed because GitHub branch bytes are not mounted into the executable filesystem in this run. Do not promote this to exact branch behavioral PASS until that transport is available.

## Audit

The fix deliberately leaves status/state comparisons unchanged unless prior evidence showed a reachable collation problem. It does not change identity formats, uniqueness cardinality, permit semantics or LAB-082 receipt cryptography. It only prevents inherited legacy collations from widening final supported identity matching.

PR #173 must remain draft. Next priority is exact execution of the new identity regression plus the already published timeout/UNKNOWN, process concurrency/crash, receipt affinity and receipt collation final-surface regressions when executable branch transport is available.
