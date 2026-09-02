# LAB-090 — activation schema installation occurs before runtime-head verification

Date: 2026-09-02
Scope: PR #175 / `experiments/provider_generation_history/supported.py`

## Finding

`SupportedHistoricalSharedAnchorLedger.__init__()` currently performs the following ordering:

1. construct and verify `CoordinatorOnlyProviderHistory`;
2. initialize the shared-anchor ledger;
3. call `_init_activation_schema()`;
4. only then call `_require_runtime_matches_durable_head()`;
5. then `_recover_pending_activation()`;
6. finally `_verify_activation_records()`.

`_init_activation_schema()` is not a read-only preflight. Under `BEGIN IMMEDIATE` it executes `CREATE TABLE IF NOT EXISTS provider_generation_activations(...)` and `CREATE TRIGGER IF NOT EXISTS block_intent_during_provider_activation ...`, verifies their SQL text, and commits.

Therefore an existing database whose durable provider history/shared-anchor state is otherwise valid can be mutated by LAB-090 schema installation even when the supplied runtime `AttestedCatchup` is stale or belongs to a different provider generation and construction is immediately rejected by `_require_runtime_matches_durable_head()` afterwards.

This is a fail-closed ordering violation: rejected construction should not perform durable migration/recovery side effects before all authority/runtime preconditions required to accept that construction have passed.

## Distinction from prior LAB-090 ordering finding

The previously recorded defect is stronger and later in the constructor: `_recover_pending_activation()` can commit/release provider activation state before `_verify_activation_records()` detects malformed historical activation evidence.

This finding occurs earlier: activation schema installation itself commits durable changes before runtime-head verification. The common fix principle is the same — establish a side-effect-free constructor preflight boundary before any schema/recovery mutation — but the regression is distinct and should be retained so a fix that merely swaps recovery and history verification does not leave migration side effects before runtime verification.

## Required regression

Use an existing legitimate pre-LAB-090 database with no activation table/trigger and a valid durable current generation A. Construct the LAB-090 supported ledger with an exact-type `AttestedCatchup` for stale/different generation B.

Pre-fix expectation:
- construction fails at runtime/durable-head mismatch;
- nevertheless `provider_generation_activations` and `block_intent_during_provider_activation` have been created and committed.

Post-fix requirement:
- construction fails before any LAB-090 schema mutation;
- activation table and trigger remain absent;
- no provider activation method is called;
- existing durable provider/shared-anchor state is byte/row equivalent to the pre-attempt state.

Also retain the already specified regression where malformed historical activation evidence prevents recovery commit/release. Together they enforce one rule: constructor rejection caused by authority/history/runtime preconditions must happen before durable or external activation side effects.

## Preferred direction

Split constructor work into explicit side-effect-free preflight and mutating phases. At minimum, verify the runtime descriptor against the already-verified durable provider head before `_init_activation_schema()`. More generally, do not let schema installation become an implicit repair path for a construction that has not yet established its authority/runtime preconditions.

LAB-092 installation provenance remains separate: it decides whether a missing activation schema is legitimate first install vs suspicious deletion. LAB-090 still needs correct ordering even after LAB-092 supplies that provenance decision.

## Execution status

Source-level audit only in this run. No behavioral PASS/RED is claimed because exact branch-local source execution remains unavailable. Production code was not modified.
