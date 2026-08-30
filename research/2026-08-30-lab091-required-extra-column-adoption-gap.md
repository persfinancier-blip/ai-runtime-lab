# LAB-091 required extra-column adoption gap

Date: 2026-08-30

## Finding

A first-adoption legacy schema can contain all canonical LAB-091 columns and still add an ordinary column such as `extra_tag TEXT NOT NULL` with no `DEFAULT`.

The prior adoption gate validates canonical NOT NULL/affinity domains, canonical/extra UNIQUE constraints, CHECK constraints, protected triggers, and existing row state. It does not reject an additive required column.

That state is reachable and materially incompatible with the supported writer: canonical LAB-091 INSERT statements name only canonical columns, so SQLite rejects the next supported write with `NOT NULL constraint failed: shared_anchor_intents.extra_tag` even though adoption would otherwise succeed.

## Reproduction

Focused SQLite mechanism probe executed locally:

1. Create otherwise-canonical `shared_anchor_intents` with `extra_tag TEXT NOT NULL`.
2. Observe the column through `PRAGMA table_info`/`table_xinfo`.
3. Execute a supported-shape PREPARED INSERT naming only canonical columns.
4. SQLite raises `IntegrityError: NOT NULL constraint failed: shared_anchor_intents.extra_tag`.

Control cases:
- canonical schema: accepted;
- additive nullable metadata column: omittable and accepted;
- additive `NOT NULL` column with a DEFAULT: omittable and accepted;
- additive `NOT NULL` column with no DEFAULT: rejected by the new adoption gate.

## Fix

Draft PR #173 branch `lab/091-mutable-shared-anchor-writer` now includes:

- `experiments/mutable_shared_anchor_writer/adoption_extra_columns.py`: fail-closed validator for ordinary extra columns that are `NOT NULL` and have no DEFAULT;
- final supported constructor calls this validator during the same `BEGIN IMMEDIATE` adoption envelope after schema-domain validation and before existing-state validation;
- `tests/test_adoption_required_extra_column_regression.py`: canonical/control/rejection regression.

Published commits:
- helper: `73923cee374083422c80a2f18aa284cb221608a0`;
- final-surface wiring: `09789c3c34074bd69c28371f9290a5d9020ef213`;
- regression/current PR head: `865097e0cc2e23385e111cde5fc877c0c0a966be`.

Published helper blob: `1c4075224c7eec50471ac38bc190bf2dcf835aef`.

## Validation status

Focused local SQLite RED→GREEN mechanism check was actually executed and observed:
- canonical: accepted;
- nullable extra: accepted;
- NOT NULL + DEFAULT extra: accepted;
- NOT NULL/no-default extra: rejected;
- pre-fix supported-shape insert into the restrictive legacy table fails as reproduced.

This is focused SQLite/mechanism evidence. It is not claimed as byte-for-byte execution of the complete PR #173 branch or the full real LAB-080/LAB-082 stack.

## Scope decision

The fix is intentionally narrow. Generated/hidden columns are not rejected without a separate reproduced supported-write failure. This follows LAB-091's rule against speculative SQLite hardening.
