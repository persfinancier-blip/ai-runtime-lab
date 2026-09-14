# LAB-095 exact reconstruction of remaining focused test blobs

Date: 2026-09-14

## Context

Per `state/CURRENT.md`, LAB-086 was probed first. Direct shell Git materialization failed before repository execution with `Could not resolve host: github.com`, exit 128. No LAB-086 requirement was weakened.

The permitted LAB-095 fallback required reconstructing three previously unresolved PR #187 test blobs without whitespace or formatting normalization.

## Exact reconstruction evidence

Using PR #187 head `835a81914c5234e68ef436e30c9837331d262432` as authority, the three test files were reconstructed into an isolated `/dev/shm/lab095-exact` tree and verified with local `git hash-object`.

Observed hashes:

- `experiments/provider_generation_history/tests/test_database_identity_migration_recovery.py` -> `363ab95f1aad425fc89f146ae8fba35d9169950d`
- `experiments/provider_generation_history/tests/red_intent_lab095_confirmed_finalize_reauthentication.py` -> `7dcd20dfd24a9439583595bf433f9f696bd870e7`
- `experiments/provider_generation_history/tests/red_intent_lab095_locked_custody_payload_tamper.py` -> `443e84f65e1d7f58c9b0ae284d700d4ec0f77cc6`

All three hashes exactly match the authoritative Git blobs recorded in the PR diff/current handoff. This resolves the prior reconstruction mismatch for `test_database_identity_migration_recovery.py`.

## What is and is not GREEN

This run establishes exact-byte reconstruction for the three remaining focused test blobs. Combined with the five exact blobs established in the prior run, the focused eight-file manifest now has known exact content for all entries.

No no-stub behavioral GREEN is claimed in this report, because the complete eight-file closure was not reassembled simultaneously in the current executable filesystem and the focused suite was therefore not executed against the full no-stub closure in this run.

## Next action

After the mandatory LAB-086 probe, reassemble all eight verified blobs in one `/dev/shm` executable tree, require 8/8 `git hash-object` matches in that same run, run `compileall`, then execute the recovery / confirmed-finalize / locked-custody suite with no protocol stubs. Only observed execution counts as GREEN. Then proceed to the DB-A -> DB-B regression and downstream LAB-080/LAB-081/LAB-090/LAB-092 gates.
