# LAB-091 — inherited mutable-state adoption gap

Date: 2026-08-28

## Finding

LAB-091 persistent v2/v3/v4 triggers constrain future DML, but the prior adoption validator only checked deterministic request IDs and orphan provider receipts. It did not prove that already-existing `shared_anchor_meta`, intent ordering/status, or component watermarks could have been produced by the supported state machine.

Executable counterexample against the old validator:

- `shared_anchor_meta.reserved_position = 5`;
- zero rows in `shared_anchor_intents`;
- `component_anchor_watermarks('component-A') = 5`;
- no orphan receipts.

The old validator returned success.

This is more than a fail-closed availability concern. LAB-080 `verify_component()` returns immediately when authenticated external position equals the local watermark. A preexisting watermark can therefore represent verification progress without the corresponding durable intent history unless adoption closes the gap.

## Fix

`validate_existing_mutable_state_locked()` now requires, under the same `BEGIN IMMEDIATE` adoption transaction:

1. valid `shared_anchor_meta` singleton;
2. `reserved_position == len(shared_anchor_intents)`;
3. exact contiguous positions `1..reserved_position` with `predecessor_position == position-1`;
4. deterministic LAB-080 request IDs;
5. at most one `PREPARED` row, only at the current tail, with no receipt binding;
6. every `CONFIRMED` row has a receipt binding (cryptographic receipt verification remains owned by LAB-082 `verify_durable()`);
7. no orphan asymmetric provider receipts;
8. every inherited component watermark is non-negative, no greater than the reserved tail, and backed by complete contiguous `CONFIRMED` history through that position.

## Published bytes

- `operation_permit.py`: `637784a5cb61a024a1df3e0e983887b6d0a838be`;
- `state_machine_udfs.py`: `8c1d6d0cd075285aed3a90ac337b60b60c1d608b`;
- `adoption_validation.py`: `36551cce4351e9305262d8f3476ad633d3246564`;
- extended `test_adoption_validation.py`: `ef19e3f21994e5d5282eec30a785a1cfe101f3ed`;
- focused `test_adoption_history_regression.py`: `9f705187059b577c131535959a347f52a55178e9`.

## Execution evidence

All files above were reconstructed locally and accepted only after `git hash-object` matched the published GitHub blob.

Exact published-source result: **15/15 PASS + compileall PASS**:

- 12 extended adoption-validation tests;
- 3 focused tail/watermark regression tests.

The earlier design-only qualification for the local 12/12 run is superseded by this exact published execution.

## Remaining boundary

This fix does not complete LAB-091. PR #173 remains draft until the full real LAB-080/LAB-082 supported surface passes real two-worker, crash rollback, timeout/UNKNOWN reconciliation, LAB-087 composition and final alternate-write/reentrancy audit.
