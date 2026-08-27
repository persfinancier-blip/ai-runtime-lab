# LAB-086 exact branch-local gate manifest

Date: 2026-08-27

## Purpose

The remaining merge gate must execute LAB-086 against one coherent source snapshot. Do not mix current `main` with the long-lived PR branch. The pinned executable source snapshot for this gate is now:

`4570a19fb92f1222db64cb07f7e4ce6312630879`

This supersedes the earlier `3d22efc4...` executable pin because the combined thaw identity hardening was published to runtime `strict_fence.py`. Commits after this pin may update only non-executable gate notes/evidence; if executable/test code moves again, repin before counting a full gate.

The GitHub connector can read the recursive tree and exact UTF-8 blobs for this commit. Direct shell/raw GitHub transport is unavailable in the observed runtime, so branch-local connector blobs are the source of truth. A locally reconstructed file counts as exact only when `git hash-object <file>` equals the pinned blob SHA below.

## Minimal implementation closure

- `experiments/anchor_attestation/protocol.py` — `15d8b7cf8ff093490ccb75679030d3a0fe41e401`
- `experiments/shared_anchor_intent_ledger/protocol.py` — `68834409363c93eee4e9a9a7b9ec076098af0acf`
- `experiments/shared_anchor_intent_ledger/supported.py` — `22a05c04831f65c1d7fe9077df3bb780c4008e09`
- `experiments/asymmetric_provider_history/protocol.py` — `a2fc3456233930d94aaaca5fe57b1debd50cbdab`
- `experiments/asymmetric_provider_history/integration.py` — `23ae688c22a1b74bde49ac506544778b2659bad6`
- `experiments/asymmetric_provider_history/supported.py` — `d61bcd544c001de7108de42aafdc54069d0029bf`
- `experiments/provider_threshold_rotation/protocol.py` — `688f3961afd9e7593fbe14c308453cfde67d23a8`
- `experiments/provider_threshold_rotation/enablement.py` — `49e9a79dfa53268ce1eb32404f488ee720b41df9`
- `experiments/provider_threshold_rotation/strict.py` — `9e96b19e4e83f045b1155b9b41894fd26762227e`
- `experiments/provider_threshold_rotation/integration.py` — `045070fea664952e8a001258f62ea64390f818e1`
- `experiments/provider_threshold_rotation/supported.py` — `59337e73f157dbb2f8437c74b3f496507a0ce989`
- `experiments/provider_rotation_recovery/protocol.py` — `d464e1335b0cdda9b0387d345e293d766aa0d199`
- `experiments/provider_rotation_recovery/supported.py` — `f0b45f52df3182091874694365536b44cda3de4b`
- `experiments/provider_recovery_authority_lifecycle/protocol.py` — `c59723c018da6ce49ff19073697d859d5a9be709`
- `experiments/provider_recovery_authority_lifecycle/supported.py` — `df4f17152cddefb66dc7f4e7f76f3112d3ab4733`
- `experiments/provider_recovery_authority_lifecycle/asymmetric_custody.py` — `771e2ae8cde15ce06297a9cf4a94c4b3f0d81dd4`
- `experiments/provider_recovery_authority_lifecycle/custody_break_glass.py` — `f49139d80d13a3716817b79f0733cc0bc5d5bcac`
- `experiments/provider_recovery_authority_lifecycle/public_custody_supported.py` — `4c338c75f1c61420438fcfe462955bd1a7ed9c92`
- `experiments/provider_recovery_authority_lifecycle/final_supported.py` — `3baf405499c5d996cd5b4f08d8a710c121247daf`
- `experiments/asymmetric_break_glass_history/protocol.py` — read exact blob from pinned tree
- `experiments/asymmetric_break_glass_history/migration_guard.py` — `1a9209b16fdb2c3dcae8e4690658a030040f6ca2`
- `experiments/asymmetric_break_glass_history/strict_fence.py` — `080eb9454437932a8ab419d66a4f2a69ed17c7ce`
- `experiments/asymmetric_break_glass_history/suffix.py` — `44847bde53b9f7b0e2fbcbab37d36dc992f497b2`
- `experiments/asymmetric_break_glass_history/final_supported.py` — `ceb7f48a55a931ba9923cac77d4ebf6c4cd2cfec`

The LAB-085 helper used by LAB-086 integration fixtures is `experiments/provider_recovery_authority_lifecycle/tests/test_public_custody_supported.py` from the same pinned tree; never substitute the current-main copy without verifying the blob is identical.

## Current LAB-086 gate inventory

Execute every `test_*.py` under `experiments/asymmetric_break_glass_history/tests` from the pinned tree, including at minimum:

- pre-cutoff lower/own proof cardinality and orphan/partial migration state;
- migration v4 public + root coauthorization and restart;
- scrubbed legacy prefix + asymmetric suffix;
- public-custody history and public-rotation cross-binding/history;
- inherited/direct supported-surface fences;
- current authority, root-head, provider-receipt and migration metadata DML fences;
- post-cutoff proof creation/freeze authorization;
- transaction-scoped thaw minimality and NULL/`INSERT OR REPLACE`/UPSERT collision resistance across all INSERT-thawed authenticated-history/proof identities;
- final single-snapshot verification;
- stale writer, stale trigger upgrade and rotation/concurrency regressions.

Then execute `unsafe_legacy_promotion_expected_failure.py` separately and require it to fail for the intended unsafe behavior, followed by `python -m compileall` over the reconstructed closure.

## Reconstruction discipline

1. Read each file from the pinned commit, not a mutable branch name.
2. Verify `git hash-object` before importing or testing it.
3. If any byte hash differs, do not count that run as exact evidence.
4. Do not manually compress/reformat source while reconstructing.
5. Keep PR #165 draft until the whole pinned gate is green and a fresh security audit finds no blocker.

## Published combined thaw hardening evidence

The combined candidate was first staged through the normal Contents API. GitHub returned staged blob `080eb9454437932a8ab419d66a4f2a69ed17c7ce`. The same payload then replaced runtime `strict_fence.py` in commit `4570a19fb92f1222db64cb07f7e4ce6312630879`, and GitHub returned the same runtime blob `080eb945...`. The staging artifact was removed afterward; that cleanup is non-executable.

Exact published test blobs reconstructed and executed after publication:

- `test_strict_fence.py` — `97048a325c4cc1ed78612bdbb4cfec42146a43f6`;
- `test_thaw_null_proof_key_regression.py` — `fce5c57c8cfaa18f6761ae9b47c211813801aae0`;
- `test_thaw_history_key_collision_regression.py` — `88ba35e933c123d10af65597d6bb51f4f11068ec`;
- `test_thaw_proof_replace_regression.py` — `c511ccfc4b88b050910561b3b8f7e99be5f33e93`.

Result: **14/14 PASS** + focused package compileall PASS. Existing non-NULL keys and NULL identities are blocked on every INSERT-thawed authenticated-history/proof surface, while new unique non-NULL keys remain available to the legitimate final-writer thaw.

## Fresh audit note

The migration verifier calls public-custody durable verification through a separate read transaction while the outer LAB-086 path holds `BEGIN IMMEDIATE`. The lower verifier uses ordinary `BEGIN`, not a second `BEGIN IMMEDIATE`; the outer transaction excludes concurrent writers across the composed verification interval. No mixed-writer snapshot blocker was established from this path.
