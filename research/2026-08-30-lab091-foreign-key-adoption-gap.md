# LAB-091 foreign-key adoption gap

Date: 2026-08-30

## Finding

A preexisting mutable-table schema can be structurally close to the canonical LAB-080/LAB-082 layout while adding a legacy `REFERENCES` clause on a canonical column. The previous LAB-091 first-adoption envelope did not inspect `PRAGMA foreign_key_list(...)`.

This is reachable through the supported writer contract. With `PRAGMA foreign_keys=ON`, a legacy `shared_anchor_intents.component_id REFERENCES legacy_components(component_id)` accepts first-adoption validation but rejects a normal supported INSERT for `component-b` when no unrelated parent row exists. The reproduced failure is `sqlite3.IntegrityError: FOREIGN KEY constraint failed`.

Canonical LAB-080/LAB-082 protected mutable tables declare no foreign keys. LAB-091 also cannot prove arbitrary parent-table lifetime, mutability, collation, or availability semantics during adoption. Therefore inherited foreign keys are not harmless metadata; they narrow the supported write domain.

## Fix

Draft PR #173 branch `lab/091-mutable-shared-anchor-writer` now contains:

- `experiments/mutable_shared_anchor_writer/adoption_foreign_keys.py`: fail-closed validator rejecting any foreign key on `shared_anchor_meta`, `shared_anchor_intents`, `component_anchor_watermarks`, or `asymmetric_provider_receipts`;
- `history_bound_operation_scoped.py`: validator wired into the same `BEGIN IMMEDIATE` adoption/restart envelope after field-domain validation and before extra-column/current-state acceptance;
- `tests/test_adoption_foreign_key_regression.py`: canonical schema acceptance plus reachable restrictive-FK failure/rejection regression.

Published commits:

- `26c2ab079d1b316d0c067782f94c147842b0c5ff` — validator module;
- `0d7166550d7744c37f5262e0948c41f073f7fe3f` — final supported constructor wiring;
- `eb832145e7e33021b9d03b3269da04d15ca0eae1` — regression test/current branch head at publication time.

Published blobs re-fetched:

- validator `18cbb38e23b027618b0abec74f1f824ee26faf6a`;
- regression `6c76d91b389afde1338d86b906313ac58a435fe6`.

## Executed evidence

A local SQLite RED probe with `foreign_keys=ON` reproduced the canonical-shaped supported INSERT failure against the legacy FK schema.

The re-fetched published validator/test contents were reconstructed in an isolated temporary package and executed with `unittest -v`: **2/2 PASS**. The canonical no-FK schema was accepted; the restrictive legacy FK both reproduced the pre-fix supported-write `IntegrityError` and was rejected by the new validator.

An unrelated spreadsheet-runtime warmup traceback was emitted during Python startup, but unittest itself returned exit code 0 and both named tests were `ok`.

This is focused exact-content evidence for the newly published validator/regression pair, not a claim of whole-branch/full-stack execution.

## LAB-086 capability observation

PR #165 still exposes `strict_fence.py` as an addition relative to `main`; the per-file patch returns the complete current 949-line source, and branch re-fetch confirms the exact predecessor blob `d4a6a40fb94455d357328bdcd10cf077a2dfc2cd`. The retained hidden-rowid patch remains blob `61841b58be42b01b97ca223567cbf9f428f7f0ce`.

However, this run still lacks a supported byte-preserving bridge that can feed that complete connector-returned source into an automatic patch application and then into the Contents API without model/manual reserialization. Because `strict_fence.py` is security-critical, no mutation was attempted. The previously derived exact target remains `b78e7c98e35138719f77c482c7f1aab36b702de7`.
