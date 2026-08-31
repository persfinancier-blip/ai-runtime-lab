# LAB-090 verify_component commit-boundary provider-generation fix

Date: 2026-08-31

## Problem

`SharedAnchorLedger.verify_component()` authenticated current-provider evidence and reauthenticated the ledger slice before its final `BEGIN IMMEDIATE`, but did not re-check provider generation after acquiring the SQLite writer reservation and before watermark DML. A provider-generation rotation could therefore durably commit between the initial provider check and watermark commit, allowing already-authenticated historical-generation evidence to advance `component_anchor_watermarks`.

Regression candidate already published in PR #175: `experiments/provider_generation_history/tests/test_activation_verify_component_rotation_race.py` (blob `359288e32e7df0ffd60bd359e326398b0bec276a`).

## Fix

PR #175 commit `9cefa27a285b292e9699505a3b10e580c69a38e1` changes only `experiments/shared_anchor_intent_ledger/protocol.py`.

Immediately after final `BEGIN IMMEDIATE`, before any watermark DML, `verify_component()` calls dynamic `_provider()` again and requires the resulting `(provider_id, generation)` to equal the provider identity authenticated earlier in the operation.

For LAB-090 `SupportedHistoricalSharedAnchorLedger`, `_provider()` first verifies that the live runtime matches the durable provider-generation head. Therefore:

- if rotation committed first, the stale runtime/provider evidence is rejected before watermark mutation;
- if verification acquires the SQLite writer reservation first, a concurrent rotation cannot acquire its own `BEGIN IMMEDIATE` until verification commits/rolls back, so the watermark linearizes before the rotation.

This avoids a larger shared-protocol hook/refactor while preserving the required commit-boundary linearization.

## Audited diff

GitHub commit inspection shows exactly six inserted lines after `q.execute("BEGIN IMMEDIATE")`; no other file or line changed. Published `protocol.py` blob: `fd22bc30f6aacdfd157557c8b458d9f7b0b3bda8`.

## Executed mechanism check

A local SQLite file-backed two-thread check was executed in this run:

1. verification connection acquired `BEGIN IMMEDIATE`;
2. a separate read connection read generation `1` while that writer reservation was held;
3. a concurrent rotation attempted `BEGIN IMMEDIATE` and serialized behind verification;
4. after verification committed, rotation completed and durable generation became `2`.

Observed result: PASS. This validates the specific assumption used by LAB-090's dynamic `_provider()` implementation: a separate durable-head reader can run while the verification connection owns the writer reservation, while competing writers cannot overtake it.

## Validation limits

Direct Git transport was re-probed and failed before repository execution with `Could not resolve host: github.com`. Therefore the exact PR-head behavioral regression/full suite was not executed in this run and no whole-branch PASS is claimed.

The published change was applied through the normal Contents API from the exact branch blob `68834409363c93eee4e9a9a7b9ec076098af0acf`, and the resulting commit diff was independently inspected after publication.

## Next gate

When exact-byte execution becomes available, run the new rotation-race regression first, then LAB-090 activation integration/restart/downstream suites. Keep PR #175 draft until those behavioral gates are clean and re-check branch/main mergeability/conflicts.
