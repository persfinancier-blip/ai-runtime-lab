# LAB-095 byte-exact cross-generation COMPLETE reauthentication execution

Date: 2026-09-14

## Scope
Executed the committed PR #187 regression `experiments/provider_generation_history/tests/test_database_identity_rotation_reauthentication.py` against the smallest dependency closure required by that test. This is focused LAB-095 evidence, not a full repository/downstream GREEN claim.

## Mandatory LAB-086 probe
Direct shell Git materialization was attempted first and failed before repository execution:

`fatal: unable to access 'https://github.com/persfinancier-blip/ai-runtime-lab.git/': Could not resolve host: github.com`

Exit 128. No LAB-086 byte-exact requirement was weakened.

## Safe connector -> executable filesystem fallback established
The GitHub connector returned exact UTF-8 file contents plus Git blob SHA for the PR #187 head `835a81914c5234e68ef436e30c9837331d262432`. Those exact bytes were written into an isolated executable closure and independently checked with `git hash-object` before execution.

Verified 10/10 files:

- `experiments/database_binding.py` -> `c6bf05b3a5579e076142300aefbc9d785cc6354a`
- `experiments/anchor_attestation/protocol.py` -> `15d8b7cf8ff093490ccb75679030d3a0fe41e401`
- `experiments/shared_anchor_intent_ledger/protocol.py` -> `68834409363c93eee4e9a9a7b9ec076098af0acf`
- `experiments/shared_anchor_intent_ledger/supported.py` -> `b16fda1fd1f47ab3f333af6ac94190d6135dcf64`
- `experiments/provider_generation_history/protocol.py` -> `c2077635aa2ecebf9a3072d97efeacb37cb0d478`
- `experiments/provider_generation_history/integration.py` -> `a6937db161f33a41a04829661dd301c52b250015`
- `experiments/provider_generation_history/supported.py` -> `7808753d7fb27c979e93f342eaf05d1e9f3f7c41`
- `experiments/provider_generation_history/database_identity.py` -> `bac58a48c576001370144cc10cfab8e0cfd129e3`
- `experiments/provider_generation_history/database_identity_migration.py` -> `c4d1db46b8b64fec116dcfef8bb05e1e7a7b875e`
- `experiments/provider_generation_history/tests/test_database_identity_rotation_reauthentication.py` -> `c46914e435a1edbcf234265718976a89eb7a7108`

`python -m compileall -q experiments` on the materialized closure: PASS.

## Runtime filesystem observation
A first test execution failed before LAB-095 semantics with `sqlite3.OperationalError: disk I/O error`. A minimal independent SQLite probe showed default journaling fails on `/tmp`, `/mnt/data`, and `/home/oai/share` in this runtime, while `/dev/shm` supports ordinary SQLite create/insert/commit.

This was treated as a per-run filesystem capability issue, not a code failure. No source or SQLite semantics were monkeypatched. The test was rerun unchanged with only `TMPDIR=/dev/shm`, causing its own `tempfile.TemporaryDirectory()` to use a journal-capable filesystem.

## Executed result
Command equivalent:

`TMPDIR=/dev/shm python -m unittest -v experiments.provider_generation_history.tests.test_database_identity_rotation_reauthentication`

Result: **1/1 PASS**.

The passing regression proves on this exact focused closure that:

1. LAB-095 identity is installed/confirmed at provider generation 1;
2. the exact identity request has persisted signed historical receipt evidence;
3. a legitimate provider rotation to generation 2 succeeds;
4. after generation 1 runtime availability is removed, repeated `migrate_database_identity()` returns the same logical database identity through historical signed evidence;
5. deleting the exact historical receipt makes the subsequent reauthentication fail closed with `HistoricalVerificationError`.

## Decision
The previous handoff statement that no supported byte-preserving connector-to-executable-filesystem path existed is no longer true for small UTF-8 closures in this runtime. The supported fallback is now:

connector exact content + published SHA -> isolated file write -> `git hash-object` equality gate -> execute only after every required file matches.

Keep PR #187 draft. The remaining recovery/tamper, DB-A -> DB-B, and downstream LAB-080/LAB-081/LAB-090/LAB-092 gates are still pending.
