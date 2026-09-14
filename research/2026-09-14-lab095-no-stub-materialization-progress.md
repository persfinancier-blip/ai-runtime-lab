# LAB-095 no-stub materialization progress

Date: 2026-09-14

## Mandatory priority probe

LAB-086 direct Git materialization was attempted first from this runtime and failed before repository execution with `Could not resolve host: github.com` (exit 128). The authoritative LAB-086 pin remains `1fa85a0e34c9ae67da57f1e64dadccf211feacc0`; no complete-gate PASS is claimed and no requirement was weakened.

## LAB-095 fallback progress

The exact PR #187 head remains `835a81914c5234e68ef436e30c9837331d262432`.

The two protocol dependencies that were previously stubbed were fetched from the GitHub control plane and reconstructed in an isolated `/dev/shm` executable tree. Local `git hash-object` matched both authoritative blobs exactly:

- `experiments/shared_anchor_intent_ledger/protocol.py` -> `68834409363c93eee4e9a9a7b9ec076098af0acf`
- `experiments/anchor_attestation/protocol.py` -> `15d8b7cf8ff093490ccb75679030d3a0fe41e401`

Three additional focused-closure files were also reconstructed and hash-verified exactly in this run:

- `experiments/provider_generation_history/database_identity.py` -> `bac58a48c576001370144cc10cfab8e0cfd129e3`
- `experiments/provider_generation_history/database_identity_migration.py` -> `c4d1db46b8b64fec116dcfef8bb05e1e7a7b875e`
- `experiments/provider_generation_history/tests/test_database_identity_migration.py` -> `cde9d16c5fb257a8b9ad7110f9badb79bede8f3f`

This establishes 5/8 byte-exact files in the current isolated closure, including both dependencies that caused the prior no-stub blocker.

## Safety stop

A first local reconstruction of `test_database_identity_migration_recovery.py` produced blob `1f308dfa9557ce0a99e1abdbe0b126e4607f47b4`, which does **not** equal the authoritative `363ab95f1aad425fc89f146ae8fba35d9169950d`. That local copy was therefore rejected as evidence and was not used to claim any exact regression result.

The two remaining target tests were not executed in this run. No 8/8 or no-stub behavioral GREEN is claimed.

## Decision / next action

Keep PR #187 draft. On the next run, probe LAB-086 first. If still blocked, reconstruct the three remaining exact test blobs directly from GitHub content without normalization/rewriting, require all 8/8 `git hash-object` matches, then run `compileall` and the recovery/confirmed-finalize/locked-custody suite under `TMPDIR=/dev/shm`. Only after that observed no-stub GREEN should work proceed to DB-A -> DB-B and downstream LAB-080/LAB-081/LAB-090/LAB-092 gates.
