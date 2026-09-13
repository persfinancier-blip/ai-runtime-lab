# LAB-086 executable pin and focused provider-receipt reprobe

Date: 2026-09-13

## Scope

Resume the priority LAB-086 exact executable/security gate without mixing later notes/evidence commits into the executable snapshot.

## Pin correction

`research/2026-08-27-lab086-exact-gate-manifest.md` was read from commit `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`. The manifest explicitly defines the pinned executable snapshot as:

`1f90830fca21e2f43fc241012cdd34fd187ba96d`

The later `1fa85a0...` commit contains gate notes/evidence and must not be treated as the executable source pin. GitHub commit metadata confirms `1f90830...` is `LAB-086 reject NULL provider receipt identities` and changes only `experiments/asymmetric_break_glass_history/strict_fence.py` relative to its parent.

## Exact pinned inventory observations

The pinned tree for `1f90830...` was read through GitHub Git-data/Contents endpoints. Relevant exact blobs include:

- `experiments/asymmetric_break_glass_history/protocol.py` — `cccb531fa13b8f8d4e3a7c3163dd7c7cbeb3ec41`;
- `migration_guard.py` — `1a9209b16fdb2c3dcae8e4690658a030040f6ca2`;
- `strict_fence.py` — `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`;
- `suffix.py` — `44847bde53b9f7b0e2fbcbab37d36dc992f497b2`;
- `final_supported.py` — `ceb7f48a55a931ba9923cac77d4ebf6c4cd2cfec`;
- `tests/test_provider_receipt_null_identity_regression.py` — `a66d9ddef2d4a41db937222b875f697c7ff74b75`.

The target tests directory tree is `ccd38ad88bd1be94fc78b2929e7938d6fa315b6f` and enumerates the complete `test_*.py` gate plus `unsafe_legacy_promotion_expected_failure.py`.

## Runtime transport observation

A fresh direct clone attempt again failed before repository code execution:

`Could not resolve host: github.com` (exit 128).

This remains a transport observation, not a repository failure.

The connector still provides exact pinned UTF-8 content and blob SHA. `fetch_file` also supports bounded line ranges, so large source files can be reconstructed deterministically in chunks and admitted only after local `git hash-object` equals the pinned blob SHA. Full closure reconstruction was not completed in this slice; therefore no whole-gate PASS is claimed.

## Focused semantic reprobe

The exact pinned regression source and the exact provider-receipt trigger block were inspected from `1f90830...`. A local SQLite semantic reprobe using that exact trigger predicate produced:

- post-cutoff `NULL request_id` insert: denied with `LAB-086 committed provider receipt cannot be replaced`;
- genuinely new non-NULL `request_id`: allowed;
- `INSERT OR REPLACE` against an existing non-NULL request identity: denied.

This is focused semantic evidence only. It does **not** replace the manifest-required byte-exact unittest/full-gate execution.

## Decision / next action

Keep PR #165 draft. Continue from executable pin `1f90830fca21e2f43fc241012cdd34fd187ba96d`, not `1fa85a0...`.

Next run: reconstruct the exact LAB-086 closure from the connector using line-ranged `fetch_file` where necessary, verify every file with local `git hash-object`, then run the manifest gate in order: all normal `test_*.py`, unsafe expected-failure separately, downstream/helper tests, compileall, source audit, security/reconciliation, and current-main conflict audit. If a specific blob cannot be reconstructed exactly, persist that exact path/SHA as the blocker rather than weakening the gate.
