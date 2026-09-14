# LAB-086 combined thaw-key candidate verification

Date: 2026-08-27

## Scope

Verified the staged combined fix for the two current transaction-scoped thaw key-identity blockers against the exact published runtime bytes.

## Exact reconstruction

- Published `strict_fence.py` blob reconstructed locally from connector line ranges: `cea0ca3b42723790971ba9415b70a7e9fa0c7368`.
- Local `git hash-object` matched that GitHub blob exactly before modification.
- Applied the durable staged design mechanically to those bytes:
  - NULL-safe proof-key collision predicate: `NEW.key IS NULL OR EXISTS(... key IS NEW.key)`;
  - permanent NULL-safe existing-key collision triggers for every other authenticated-history table whose normal INSERT-deny is removed during final-writer thaw;
  - collision triggers are included in full reinstall cleanup but are never removed by `remove_public_mutation_fence_locked()`;
  - `assert_public_mutation_fence_locked()` requires every applicable collision trigger.
- Resulting candidate blob: `080eb9454437932a8ab419d66a4f2a69ed17c7ce`.
- `python -m py_compile` passed.

The candidate diff is limited to the staged combined change: one `THAW_INSERT_HISTORY_COLLISION_FENCES` map, helper/name collection, install/assert wiring, full-cleanup wiring, and NULL-safe proof collision semantics.

## Exact focused regression execution

The following published test files were reconstructed locally and verified by `git hash-object` before execution:

- `test_strict_fence.py` — `97048a325c4cc1ed78612bdbb4cfec42146a43f6`;
- `test_thaw_null_proof_key_regression.py` — `fce5c57c8cfaa18f6761ae9b47c211813801aae0`;
- `test_thaw_history_key_collision_regression.py` — `88ba35e933c123d10af65597d6bb51f4f11068ec`;
- `test_thaw_proof_replace_regression.py` — `c511ccfc4b88b050910561b3b8f7e99be5f33e93`.

Result on candidate `080eb945...`: **14/14 PASS**. Package compileall also passed.

The gate covers:

- existing non-NULL proof keys cannot be REPLACE'd during thaw;
- NULL proof identities cannot be inserted/replaced during thaw;
- existing public/root/provider/threshold history keys cannot be REPLACE'd during thaw;
- NULL identities on those seven thawed history surfaces are denied;
- new unique non-NULL authority/transition/proof/generation keys remain creatable by the legitimate thaw path;
- ordinary strict-fence DELETE/UPSERT/head/reinstall/rollback behavior remains green.

## Publication status

Runtime `experiments/asymmetric_break_glass_history/strict_fence.py` is **not yet replaced** in this run. The available high-level GitHub write action accepts only complete UTF-8 text and exposes no mounted-file/patch parameter. Low-level tree/ref manipulation is prohibited by `AGENTS.md`. The candidate is nevertheless reproducible from the exact current blob plus the already-durable staged patches, and this note records the exact resulting hash and execution evidence.

## Exact next step

Publish only a byte-identical candidate whose resulting GitHub content blob is `080eb9454437932a8ab419d66a4f2a69ed17c7ce`; then re-fetch that published blob and rerun the exact 14-test focused gate. After that repin the executable snapshot and resume the full branch-local LAB-080→086 real-ledger gate.
