# LAB-095 identity migration/recovery composition audit — 2026-09-16

## Scope

Follow-up to the PR #187 stale-composition scan after adapting `test_database_identity_rotation_reauthentication.py`.

LAB-086 was probed first in this run. `git clone --no-checkout https://github.com/persfinancier-blip/ai-runtime-lab.git` failed before repository execution with `Could not resolve host: github.com`, exit 128. No LAB-086 executable PASS is claimed.

Audited PR #187 head `4eec30809ea0e6203146b9b0274014ec0aae3a3e`, focusing on:

- `experiments/provider_generation_history/tests/test_database_identity_migration.py` (`cde9d16c5fb257a8b9ad7110f9badb79bede8f3f`)
- `experiments/provider_generation_history/tests/test_database_identity_migration_recovery.py` (`363ab95f1aad425fc89f146ae8fba35d9169950d`)
- `experiments/provider_generation_history/tests/test_database_identity.py` (`b28c8caf3681d6bfbbc6e09f499cc509b03c287e`)
- `experiments/provider_generation_history/tests/test_database_identity_audit.py` (`cf3b2ad4b1c3edd5a4eafc3e206ef47954cf972e`)

## Finding

No additional stale LAB-101/LAB-092/LAB-090 composition defect was found in this slice.

The migration/recovery tests deliberately exercise `prepare_database_identity()` / `migrate_database_identity()` below the supported runtime-constructor boundary using narrow `_Ledger` and `_History` fixtures. Their hand-built SQLite schema is part of the migration primitive's unit contract: atomic reservation, retry identity reuse, confirmed-restart finalization, path-divergence rejection, under-lock provider-head change rejection, rollback-before-commit, orphan-intent fail-closed behavior, concurrent installer convergence, and legacy-tail next-position reservation. Replacing these fixtures with `SupportedHistoricalSharedAnchorLedger` + LAB-101 bootstrap would move the tests to a different abstraction level and hide the migration primitive states they intentionally construct.

Likewise, `test_database_identity.py` and `test_database_identity_audit.py` are classifier/schema tests. They intentionally create exact or malformed custody/anchor relations directly and do not claim supported runtime startup. LAB-092 COMPLETE provenance and fenced rotation are therefore not prerequisites for those classifier-only fixtures.

The previously adapted `test_database_identity_rotation_reauthentication.py` remains the relevant end-to-end supported-runtime case: it now uses `migrate_activation_schema_v1()` and `FencedActivationProvider`.

## Decision

Do not modify these four tests merely to make every SQLite fixture pass through LAB-101. Preserve abstraction-level separation. Continue the scan for actual `SupportedHistoricalSharedAnchorLedger` construction/restart and `rotate_provider()` call sites where LAB-092 COMPLETE or LAB-090 fencing is semantically required.

## Validation status

Source/connector audit only. Exact repository pytest/compileall was not executable because byte-exact repository materialization remains unavailable in the shell runtime. No executable GREEN is claimed.
