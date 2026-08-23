# LAB-086 — durable trigger-upgrade conformance

## Finding

The LAB-086 migration/public-custody fence used `CREATE TRIGGER IF NOT EXISTS`. SQLite treats an existing same-name trigger as authoritative and does not compare or replace its SQL definition. A durable database initialized by an older/weaker LAB-086 build could therefore retain an obsolete trigger after code upgrade.

A deterministic pre-fix SQLite reproduction installed a same-name `lab086_public_head_requires_root_proof` with `WHEN 0`, ran the former `CREATE TRIGGER IF NOT EXISTS` installer, and then successfully changed the public recovery head without a root proof. The stored trigger SQL was still the weak historical definition.

## Fix

`AuthenticatedBreakGlassMigrationGuard._ensure_schema_locked()` now treats LAB-086 trigger definitions as executable security policy rather than cache. While the caller holds `BEGIN IMMEDIATE`, it:

1. creates the required boundary/projection tables;
2. drops every LAB-086-owned migration/public-fence trigger name;
3. recreates the exact current definitions;
4. continues under the same write-excluding transaction.

SQLite schema DDL is transactional, so other writers cannot observe an intermediate durable policy state when this method is used through the supported guard paths.

## Executed evidence

A focused post-fix SQLite probe used the exact current trigger predicates and observed:

- the old `WHEN 0` definition no longer existed after `_ensure_schema_locked` semantics were applied;
- an unproved `provider_recovery_public_head` change raised `IntegrityError` with the LAB-086 proof-first message;
- the authoritative head remained unchanged.

An executable repository regression was added as `experiments/asymmetric_break_glass_history/tests/test_stale_trigger_upgrade_regression.py`.

## Boundary

This focused probe proves the schema-upgrade mechanism/predicates. It is not a substitute for the full exact-source LAB-086 + LAB-085/084/083/082/080 regression gate, which remains required before merge.
