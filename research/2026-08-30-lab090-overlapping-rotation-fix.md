# LAB-090 overlapping provider-rotation exclusion fix

Date: 2026-08-30

## Finding carried from prior audit

A provider rotation could durably advance G1->G2 and leave its activation row `SQL_COMMITTED`, then a second G2->G3 rotation could enter `rotate_provider()` and advance the durable generation head again before G2 activation reconciliation completed. Normal recovery is keyed to the current durable generation, so an older unresolved activation could be stranded.

Focused regression candidate already published on PR #175: `experiments/provider_generation_history/tests/test_activation_overlapping_rotation.py` at commit `ac19c49226d9b31eed46646cd4ddb9ddd0dae507`.

## Minimal fix

Published on draft PR #175:

- commit `960e847c4309626d86fee756bb304cfb240a0f4f`;
- file `experiments/provider_generation_history/supported.py`;
- inside the existing `BEGIN IMMEDIATE` transaction in `rotate_provider()`, before PREPARED-intent validation and before inserting the candidate activation, query for any `provider_generation_activations.status='SQL_COMMITTED'`;
- if present, raise `PendingRotationBlocked("previous provider activation commit is unresolved")`.

The normal exception path then rolls back and calls `provider.abort_activation(ticket)` because the second candidate has not committed SQL state.

## Concurrency reasoning

The exclusion read and the new activation INSERT now share the same SQLite write transaction. Two provider rotations cannot both pass this gate and insert unresolved activations: SQLite serializes their `BEGIN IMMEDIATE` transactions, and the later transaction observes the earlier `SQL_COMMITTED` row before it can mutate generation history/head.

This does not broaden the protocol or add a second lock system. It extends the existing durable activation state machine with the missing coordinator-side mutual exclusion.

## Validation actually performed

- GitHub commit diff inspected after publication: exactly five added lines in `rotate_provider()`, no unrelated file change.
- Existing regression source inspected and matches the fixed schedule: unresolved G2 activation, attempted G3 rotation must raise `PendingRotationBlocked`, G3 reservation must be aborted, durable head must remain G2, and no G3 activation row may exist.
- Fresh direct `git ls-remote https://github.com/persfinancier-blip/ai-runtime-lab.git HEAD` failed before repository-code execution with `Could not resolve host: github.com`.

Therefore no exact-head unittest, provider-history integration, or downstream PASS is claimed in this run.

## Next gate

When exact-head execution is available, run:

1. `test_activation_overlapping_rotation.py`;
2. `test_activation.py`;
3. `test_activation_integration.py`;
4. `test_activation_premature_release.py`;
5. provider-generation integration tests;
6. downstream shared-anchor/provider-history suites.

PR #175 remains draft until those executable gates are clean and a fresh source audit finds no remaining restart/concurrency defect.
