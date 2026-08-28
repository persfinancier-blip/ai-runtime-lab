# LAB-091 exact adoption-index regression gate — 2026-08-29

## Scope

LAB-086 remained first priority. A fresh direct raw-GitHub probe from the executable shell again failed before byte transfer with DNS resolution failure, so the retained security-critical hidden-rowid candidate was not hand-reserialized or published.

Per `state/CURRENT.md`, this run therefore executed the bounded LAB-091 fallback: reconstruct and run the published expression-UNIQUE, partial-UNIQUE, and missing canonical identity-constraint regression suites against the exact published validator.

## Exact reconstructed source identities

The following files were reconstructed from the GitHub branch `lab/091-mutable-shared-anchor-writer` and verified locally with `git hash-object` before execution:

- `experiments/mutable_shared_anchor_writer/adoption_validation.py` -> `2281d8e5ae21817b8eab0f52dc44abe61104c745`
- `experiments/mutable_shared_anchor_writer/operation_permit.py` -> `637784a5cb61a024a1df3e0e983887b6d0a838be`
- `experiments/mutable_shared_anchor_writer/state_machine_udfs.py` -> `8c1d6d0cd075285aed3a90ac337b60b60c1d608b`
- `tests/test_adoption_expression_unique_regression.py` -> `cec968e15f2cc4cfb0f38030ff44ae4c24bb89f0`
- `tests/test_adoption_partial_unique_regression.py` -> `e77521d839510490a2bea4d92d68d9071241ff35`
- `tests/test_adoption_schema_contract_regression.py` -> `e87c550282ac455e4ca5bedeb9de4f6626d563a4`

The lower `shared_anchor_intent_ledger.protocol` import was represented only by its verified branch constant `ALLOWED_INTENT_TYPES = {"migration", "root_rotation", "archive_checkpoint"}`. These focused schemas contain zero intent-history rows, so neither lower ledger behavior nor `expected_request_id()` is exercised by this gate. This is therefore exact target/test-source evidence, not a full dependency-closure claim.

## Execution

Executed:

```text
python -m unittest -v \
  experiments.mutable_shared_anchor_writer.tests.test_adoption_expression_unique_regression \
  experiments.mutable_shared_anchor_writer.tests.test_adoption_partial_unique_regression \
  experiments.mutable_shared_anchor_writer.tests.test_adoption_schema_contract_regression
```

Observed result:

```text
Ran 4 tests in 0.009s
OK
```

All four methods passed:

1. expression UNIQUE does not collapse into a false single-column identity guarantee;
2. partial UNIQUE indexes do not satisfy the global identity contract (five subcases);
3. canonical PK/UNIQUE identity constraints are accepted;
4. clean-looking schemas missing each required identity constraint fail closed (six subcases).

Also executed `python -m compileall -q experiments/mutable_shared_anchor_writer`; PASS.

## Decision

The exact published expression/partial/missing-constraint focused adoption gate is now GREEN. Do not repeat this narrow reconstruction unless one of the pinned blobs changes.

This does **not** satisfy the remaining LAB-091 merge gate. The next LAB-091 work, only when LAB-086 remains concretely transport-blocked, is the complete supported-surface gate through `SupportedHistoryBoundOperationScopedAsymmetricSharedAnchorLedger`: real LAB-080/LAB-082 dependency closure, two-worker/crash, timeout-after-commit/UNKNOWN reconciliation, LAB-087 composition, and reentrancy/alternate-write-surface audit.

LAB-086 remains priority #1 and must resume immediately if a supported byte-preserving response-to-write/executable-filesystem path becomes available.
