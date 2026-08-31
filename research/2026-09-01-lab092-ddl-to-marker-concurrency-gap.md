# LAB-092 — DDL-to-marker concurrency gap

Date: 2026-09-01

## Scope

Audit the explicit `migrate_activation_schema_v1()` path on PR #177 after the previously defined DDL-first / authenticated completion-marker contract.

## Source observation

Current LAB-092 migration does:

1. `_classify(path)`;
2. construct `SupportedHistoricalSharedAnchorLedger(...)`;
3. inherited LAB-090 `_init_activation_schema()` installs/verifies activation table + trigger under one `BEGIN IMMEDIATE` and commits;
4. only after that constructor returns, call `legacy.execute(_completion_intent())` to reserve/confirm provenance.

The LAB-090 DDL transaction is internally atomic, but its writer lock ends before the LAB-092 provenance intent is reserved.

## Concrete interleaving

There is therefore an observable state:

- exact activation DDL is committed;
- provenance marker is still ABSENT;
- no unresolved provider activation exists, so `block_intent_during_provider_activation` does not reject ordinary intent insertion;
- another legitimate shared-anchor writer can reserve an unrelated PREPARED intent before the migration marker reserves its own PREPARED intent.

This can deny completion of the explicit migration (`PendingIntent`) and violates the LAB-092 acceptance requirement that a concurrent writer not enter during initial install/reconciliation.

## Executed mechanism probe

A file-backed SQLite two-thread probe reproduced the interleaving with the same lock boundary:

- migration side exposed the post-DDL-commit / pre-marker interval;
- writer side acquired `BEGIN IMMEDIATE` and inserted its intent during that interval;
- observed result: `admitted_before_marker=True` and writer insertion completed before marker reservation.

This is mechanism-level evidence, not branch-level execution of PR #177.

## Regression published

Added `experiments/provider_generation_history/tests/test_activation_schema_migration_concurrency.py` to PR #177, branch commit `b36b4a334dc1a8dea49342c758424ed3cc00a8ea`.

The regression injects a deterministic pause after inherited LAB-090 activation DDL installation has committed but before LAB-092 calls the provenance marker. A concurrent legitimate shared-anchor writer is then attempted. Desired contract: the writer must not enter that window.

Current implementation is expected to be RED for this regression until migration admission is made atomic with provenance reservation or equivalently fenced. Exact branch execution is still unavailable because direct git transport failed before repository execution with `Could not resolve host: github.com`; do not claim a branch RED result until the published head is actually executed.

## Design constraint for the fix

Do not weaken the already established post-completion tamper rule. In particular:

- do not confirm the completion marker before exact DDL exists;
- do not add an unauthenticated ad-hoc marker that becomes a second authority surface;
- do not permit CONFIRMED marker + missing/mismatched DDL to auto-repair;
- avoid a PREPARED-before-DDL recovery rule unless it is proven not to let local database tamper be laundered into a fresh authenticated migration.

The promising direction is a single SQLite writer transaction that makes exact DDL installation and deterministic PREPARED migration reservation become visible atomically, followed by external confirmation after commit. This requires careful reuse/refactoring of LAB-080 reservation semantics rather than duplicating authority logic blindly.

## Next audit

Before implementing that refactor, add/regress the unresolved LAB-090 activation case: if `SQL_COMMITTED` activation fencing rejects migration-marker insertion, explicit migration must fail closed and must not leave a CONFIRMED provenance marker.
