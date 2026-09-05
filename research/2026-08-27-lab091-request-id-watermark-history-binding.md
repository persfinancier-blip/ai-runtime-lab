# LAB-091 — deterministic request IDs and watermark/history binding

## Finding

The v2/v3 one-shot permit layers constrain individual DML rows and bind new intents/receipts to current provider/tail state, but two useful state-machine invariants were still delegated entirely to the Python caller:

1. a broker-issued intent permit could carry an arbitrary `request_id` rather than LAB-080's deterministic request identity;
2. a broker-issued watermark permit could jump across PREPARED or malformed/gapped durable history.

A third related gap was found during the same audit: an exact `PREPARED -> CONFIRMED` permit could carry a non-null receipt binding without SQL proving that a matching persisted RECONCILE receipt existed.

These are not same-privilege raw-SQL sandbox escapes; LAB-087 remains that external boundary. They matter because LAB-091's purpose is to limit the damage of an incorrectly issued writable-handle permit by making SQL enforce the durable state machine as well as row identity.

## v4 additive guard

`state_machine_udfs.py` exposes LAB-080's deterministic request-id derivation as a connection-local SQLite UDF.

`history_binding_guards.py` adds distinct `lab091_v4_*` triggers that:

- require `NEW.request_id == shared-anchor:{position}:{sha256(canonical request fields)}` before intent creation;
- require every position crossed by a watermark insert/update to exist as a CONFIRMED intent with a receipt binding and canonical predecessor `position-1`;
- require `PREPARED -> CONFIRMED` to have a persisted RECONCILE receipt matching request ID, provider ID/generation, position and stable binding.

`SupportedHistoryBoundOperationScopedAsymmetricSharedAnchorLedger` composes v2 exact one-shot guards + v3 cross-table guards + v4 history-binding guards. It installs the deterministic request-id UDF on every connection.

## Executed evidence

A focused SQLite candidate harness executed 9 tests successfully:

- wrong deterministic request ID blocked;
- exact request ID accepted;
- watermark insert across PREPARED history blocked;
- complete confirmed prefix accepted;
- watermark update across PREPARED history blocked;
- complete confirmed delta accepted;
- malformed predecessor/gap not hidden by row count;
- confirmation without matching provider receipt blocked;
- confirmation with matching persisted RECONCILE receipt accepted.

Compileall passed for the focused workspace.

Published GitHub blobs currently include:

- `state_machine_udfs.py` `8c1d6d0cd075285aed3a90ac337b60b60c1d608b`;
- `history_binding_guards.py` `bd1f8fe16d3cdeaaa0f96bca1406e1edb02cfe0f`;
- `history_bound_operation_scoped.py` published on PR #173;
- updated regression `test_history_binding_guards.py` published on PR #173.

The focused 9/9 execution used the same semantics but is **not yet counted as an exact-published-source run** after the final Contents API rewrite because the published regression blob changed. The next gate must reconstruct those published blobs and rerun before promoting the evidence.

## Remaining gate

This v4 layer is additive and PR #173 remains draft. It still needs execution on the real LAB-080/LAB-082 stack across restart, actual concurrent workers, crash rollback, timeout-after-commit/UNKNOWN reconciliation, and LAB-087 restricted-worker composition.
