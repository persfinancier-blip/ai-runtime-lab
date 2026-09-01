# LAB-092 — stale runtime and non-mutating provider-history view

Date: 2026-09-01
Issue: #176
Draft PR: #177 (`lab-092-activation-schema-provenance`)

## Objective

Audit the next LAB-092 migration-boundary risk after atomic DDL + PREPARED publication: a stale runtime provider must fail closed before the migration commit, and migration setup must not initialize or bootstrap provider-history authority before the SQLite writer lock.

## Source audit

`activation_schema_provenance._reservation_surface()` previously built `CoordinatorOnlyProviderHistory(path, bootstrap)` before `_install_and_reserve_prepared()` acquired `BEGIN IMMEDIATE`.

`CoordinatorOnlyProviderHistory` inherits `DurableProviderHistory.__init__`. That constructor calls `_init()`, whose implementation executes `CREATE TABLE IF NOT EXISTS` for provider-history tables and bootstraps generation material/head when empty before calling durable verification.

Therefore LAB-092's migration helper had a pre-lock mutation surface. Although a valid legacy LAB-080/081 database would normally already contain these objects, a partially missing/corrupted provider-history surface could be recreated/bootstrap-initialized as a side effect before the migration's fail-closed checks. That violates the LAB-092 contract: migrate an existing authority surface; do not create a second or missing authority surface incidentally.

## Change published on PR #177

1. Regression first: commit `bc129f7d829486ff7a82fd88e260a872684374e2` adds `test_activation_schema_migration_stale_runtime.py`.
   - establishes valid inherited state;
   - advances durable provider history from generation 1 to generation 2;
   - removes only LAB-090 activation DDL to model a legitimate legacy activation-schema source;
   - invokes migration with generation-1 runtime;
   - requires `CurrentGenerationRequired`;
   - requires activation table absent, trigger absent, migration marker absent, and durable head still generation 2 after failure.

2. Implementation: commit `3abc53067d3e549a677f740c6a7b09c299acfaa2`, provenance blob `52be0d1ae8365f3c8ffbfdfdb94c972dc082b74e`.
   - `_reservation_surface()` no longer calls the mutating `CoordinatorOnlyProviderHistory` constructor;
   - it validates bootstrap and creates a read/verify-only history view with `object.__new__`, setting only `path` and `bootstrap`;
   - inside the same `BEGIN IMMEDIATE` that will publish DDL + PREPARED, migration now calls inherited `_verify_durable_locked(q)` rather than only `_current_locked(q)`;
   - stale runtime comparison happens after full durable-history verification but before DDL creation;
   - therefore provider history is verified, not initialized, on the migration boundary.

## Validation actually executed

- GitHub re-fetch shows PR #177 head `3abc53067d3e549a677f740c6a7b09c299acfaa2`, still open/draft and mergeable against LAB-090.
- GitHub per-file patch re-fetch shows the non-mutating history view and `_verify_durable_locked(q)` exactly as intended.
- Exact checkout/test execution was attempted with a fresh clone of `lab-092-activation-schema-provenance` and intended command:

  `python -m unittest experiments.provider_generation_history.tests.test_activation_schema_migration_stale_runtime`

  Checkout failed before repository code executed with `Could not resolve host: github.com`.

No branch-level RED/GREEN is claimed.

## Security/correctness conclusion

The source-level migration boundary is now stricter:

- no provider-history constructor side effects before migration lock;
- full provider-history verification under the lock;
- stale runtime rejection before activation DDL or provenance marker become visible;
- exact DDL + PREPARED atomic publication contract remains unchanged.

PR #177 must remain draft until exact branch tests execute, including the new stale-runtime regression plus the prior atomic-boundary, PREPARED recovery, deletion/mismatch, unresolved activation, and legitimate legacy migration cases.

## Next action

LAB-086 remains first priority. If its exact byte-preserving publication bridge is still unavailable and branch execution remains unavailable, audit LAB-092's two early-return paths for existing `PREPARED`/`CONFIRMED` migration markers: ensure they also perform full durable provider-history verification and runtime-current checks before returning an entry or proceeding to external confirmation. Add regressions if either path can bypass those checks.
