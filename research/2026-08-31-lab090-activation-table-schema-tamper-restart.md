# LAB-090 activation-table schema tamper on restart

Date: 2026-08-31

## Finding

The LAB-090 restart path authenticates the persisted activation trigger definition, but it does not authenticate the persisted `provider_generation_activations` schema itself.

SQLite accepts `CREATE TABLE IF NOT EXISTS provider_generation_activations(...)` when a same-name VIEW already exists. Therefore an actor able to tamper with the durable SQLite schema can replace the activation table with a compatible empty view, reinstall the exact canonical trigger text, and restart the supported ledger. The trigger remains textually canonical but now queries the empty view, while `_recover_pending_activation()` and `_verify_activation_records()` also see no activation rows.

This is a concrete durability-boundary defect: canonical trigger authentication alone is insufficient if the trigger's referenced relation is not itself authenticated as the expected table/constraints.

## Reproduction published

Branch: `lab-090-provider-activation-fencing`

Commit: `fcad18c938f732241c968229831e0fccd82a3f6b`

Test: `experiments/provider_generation_history/tests/test_activation_schema_tamper_restart.py`

Blob: `b03e52c1cd512a104b70cbd9f5a91747ce901184`

The regression initializes a valid LAB-090 ledger, drops the activation trigger/table, replaces the table with an empty compatible view, reinstalls the exact canonical trigger definition, and requires restart to raise `HistoricalVerificationError`.

Exact published test bytes were re-fetched and independently hash-checked; Git blob SHA matches. `py_compile` executed PASS on the exact byte content. Exact branch behavioral RED/GREEN is not claimed because repository execution transport is unavailable in this run.

## Independent SQLite mechanism check

A file-backed SQLite probe confirmed that `CREATE TABLE IF NOT EXISTS` succeeds rather than replacing/rejecting a same-name view. This makes the persisted relation-type substitution durable across constructor schema initialization.

## Required fix

Before recovery or record verification, fail closed unless `sqlite_master` shows `provider_generation_activations` as the expected table with the exact canonical schema/constraints. The verification must cover at least relation type and canonical table SQL, or an equivalently strict `PRAGMA table_info/index_list/index_info` contract. Do not drop/recreate the relation during restart, because doing so would destroy durable activation evidence and introduce a correctness/security failure.

## Boundary

This is schema-integrity hardening for the LAB-090 durable coordinator boundary. It does not expand the provider activation protocol or change authority semantics.
