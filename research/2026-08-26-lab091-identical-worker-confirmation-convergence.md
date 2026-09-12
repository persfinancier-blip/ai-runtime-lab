# LAB-091 — identical-worker confirmation convergence

## Finding

The operation-scoped candidate had a concurrency correctness gap after external effect reconciliation. Two workers can legitimately reserve the same exact intent, converge on the same provider request/receipt, and race only at the final `PREPARED -> CONFIRMED` SQL transition.

The original confirmation path required the durable row to remain byte-for-byte equal to the worker's earlier PREPARED snapshot. If another identical worker committed the exact same request with the exact same authenticated receipt first, the loser observed `current != entry` and raised `IntentSubstitution`. This is fail-closed but violates idempotent concurrent-worker convergence.

## Correct rule

A confirmation loser may accept an already-CONFIRMED durable winner only when both conditions hold:

1. the durable row has the exact same request identity (`intent_id`, component/type/payload, provider generation, predecessor/position, request_id);
2. the durable `receipt_binding` equals the authenticated receipt the loser independently obtained.

Different request identity or a different receipt remains fail-closed.

## Candidate

`SupportedConvergentOperationScopedAsymmetricSharedAnchorLedger` adds `_commit_confirmation()` and routes `execute()` through it. The first worker still uses the existing one-shot `intent-confirm` permit. A loser never performs a second write; it only returns the already-authenticated durable winner after exact request + receipt comparison.

Published blobs:

- `experiments/mutable_shared_anchor_writer/convergent_operation_scoped.py`: `84a84df633fbaaca7f424f4db5bd3fd20403263b`
- `experiments/mutable_shared_anchor_writer/tests/test_confirmation_convergence.py`: `faae1a75d5448737f51c850d4cbec289e83c4697`

The exact focused harness passed 4/4: normal confirm, identical-worker convergence, receipt substitution rejection, and request substitution rejection. This is not the final LAB-080/LAB-082 real-stack concurrency gate.
