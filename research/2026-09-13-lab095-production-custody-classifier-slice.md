# LAB-095 production custody/classifier slice — 2026-09-13

## Context
LAB-086 remained priority #1. A fresh direct clone of executable pin `1f90830fca21e2f43fc241012cdd34fd187ba96d` failed before repository execution with `Could not resolve host: github.com`; the byte-exact LAB-086 gate was therefore not weakened or claimed.

Per `state/CURRENT.md`, work then resumed on LAB-095/#180 / draft PR #187.

## Implemented production slice
Added `experiments/provider_generation_history/database_identity.py` on branch `lab-095-database-identity-red-intent`.

The production module does **not** import `tests/lab095_*` and does not manufacture external shared-anchor authority. It independently implements:
- canonical v1 logical identity payload and payload digest;
- CONFIRMED logical database identity digest bound to payload/provider-generation/position/request/receipt;
- domain-separated genesis and transition parent-chain links;
- exact `provider_history_database_identity` custody DDL;
- read-only fail-closed persisted-state classification: `ABSENT`, `PREPARED`, `CONFIRMED_NEEDS_FINALIZE`, `COMPLETE`, `CORRUPT`;
- custody payload/request cross-binding to the persisted `shared_anchor_intents` identity intent;
- recomputation of final identity from persisted CONFIRMED intent evidence rather than trusting a stored self-assertion.

Published production blob after audit fix: `96be3e6fd17a86a3f7fb133a68b9b88741ad4070` (commit `c943e9bbd56989258ce919a578a54a50ff32aa88`).

Focused regression files on the branch:
- `experiments/provider_generation_history/tests/test_database_identity.py`;
- `experiments/provider_generation_history/tests/test_database_identity_audit.py`.

Current PR #187 head after the audit regression commit: `ed0e3baeba6be964ae05f33063c8073bcd15d2d6`.

## Execution evidence
The authored production source passed local `py_compile`. Its local `git hash-object` was `96be3e6fd17a86a3f7fb133a68b9b88741ad4070`, exactly matching the published GitHub blob.

A file-backed SQLite focused suite executed against those production bytes and a locally reconstructed frozen-reference helper: **5/5 PASS, exit 0**. Covered:
1. canonical derivation equality against the frozen reference semantics;
2. `ABSENT -> PREPARED -> CONFIRMED_NEEDS_FINALIZE -> COMPLETE` persisted-state classification;
3. final identity digest tamper -> `CORRUPT`;
4. orphan custody with no shared-anchor identity row -> `CORRUPT`;
5. absent-path classification creates no SQLite file;
6. same-name noncanonical custody schema -> `CORRUPT`.

This is a focused slice, **not** a full exact-repository LAB-095 GREEN. The complete repository dependency closure and LAB-080/081/090/092 downstream gates were not materialized in this runtime.

## Audit finding fixed before handoff
The first implementation of `classify_identity_custody()` used `sqlite3.connect(path)` before checking existence. For a missing path that creates an empty SQLite file, contradicting the read-only classifier contract.

Fix:
- check path existence/type before connecting;
- require the exact custody DDL stored by SQLite;
- require `shared_anchor_intents` to be a table before consuming it as external identity evidence;
- add regressions proving missing-path classification has no filesystem creation side effect and same-name altered custody DDL fails closed.

## Deliberate scope boundary
This slice does not yet:
- generate the 32-byte nonce;
- perform `BEGIN IMMEDIATE` installation;
- atomically create custody plus the deterministic PREPARED shared-anchor reservation;
- reconcile timeout/UNKNOWN;
- finalize local custody after reauthenticating external CONFIRMED evidence;
- make `DurableProviderHistory.path` / `SharedAnchorLedger.path` construction-bound and non-rebindable;
- integrate parent-chain identity into provider-generation transitions.

Those remain the next production slices. In particular, no caller-supplied nonce/digest and no test vector is treated as production authority.

## Decision
Keep PR #187 draft. The next LAB-095 implementation step is explicit migration/recovery: under `BEGIN IMMEDIATE`, re-read `ABSENT`, generate the CSPRNG nonce internally, persist custody and one deterministic PREPARED identity reservation atomically, then perform external execution outside the transaction and recover only through same-request reconciliation / authenticated local finalization.
