# LAB-090 orphan activation restart verification

Date: 2026-08-31
Issue: #169
Draft PR: #175 (`lab-090-provider-activation-fencing`)

## Finding

`SupportedHistoricalSharedAnchorLedger._verify_activation_records()` queried activation rows with an `INNER JOIN` to `provider_generations`.

`provider_generation_activations.new_generation_id` is not protected by a SQLite foreign-key constraint. Therefore a durable orphan activation row could exist while the verifier silently omitted it from the result set. For `status='SQL_COMMITTED'`, the persisted `block_intent_during_provider_activation` trigger would still see the row and block every future shared-anchor intent. The constructor could therefore report a successful restart into a permanently blocked writer state instead of failing closed.

This is a restart/correctness defect, not an authority expansion. It is outside normal atomic rotation production because the legitimate insert and generation rotation share one transaction, but durable verification must not silently ignore structurally invalid rows.

## Reproduction mechanism

A standalone SQLite mechanism check was actually executed in this run:

- seed one valid generation;
- seed one activation referencing a missing generation;
- `INNER JOIN` returned `[]`;
- equivalent `LEFT JOIN` returned the orphan activation with `verification_key_hex = NULL`.

This validates the exact relational mechanism. It is not claimed as an exact-PR-head unittest execution.

## Regression

Published on PR #175:

- `experiments/provider_generation_history/tests/test_activation_orphan_restart.py`
- commit `35c530b7c8c316a8bd4e7d5331b9950e0c7d7db8`

The regression creates a valid ledger, injects an orphan `SQL_COMMITTED` activation row, and requires restart to raise `HistoricalVerificationError`.

Before the fix, source inspection shows the row is removed by the `INNER JOIN`, so the constructor reaches successful completion instead of raising.

## Fix

Published on PR #175:

- commit `6c68ba69914d588efd6fe9c8f4529418b69e444c`
- `supported.py` blob `b2ce60590eb0910735d79d3ecb27690b8d4eec06`

Change:

1. replace activation-history `JOIN` with `LEFT JOIN`;
2. reject `verification_key_hex is None` with `HistoricalVerificationError("activation references missing provider generation")` before constructing `GenerationDescriptor`.

GitHub commit diff reports only the intended query/check plus an end-of-file newline presentation difference; no protocol expansion was introduced.

## Validation status

Direct `git ls-remote https://github.com/persfinancier-blip/ai-runtime-lab.git HEAD` was actually attempted again and failed before repository-code execution with `Could not resolve host: github.com`.

Therefore no exact published-head unittest/compileall PASS is claimed. The focused regression and the rest of the LAB-090 executable gate remain pending until exact source bytes can be executed.

## Audit

The fix is fail-closed and narrow:

- legitimate activation rows continue to bind to exact generation descriptors;
- orphan rows are no longer invisible;
- no automatic deletion/reconciliation is attempted because there is no authenticated basis to infer missing generation history;
- historical unresolved logic remains unchanged.

## Next action

LAB-086 remains priority #1. Probe for a supported byte-preserving predecessor+patch composition path. If unavailable, run the exact-head LAB-090 gate as soon as direct source execution is possible, including `test_activation_orphan_restart.py` plus the existing historical-unresolved, historical-retry, overlapping-rotation, premature-release, activation primitive/integration, provider-generation integration, and downstream suites. If execution remains blocked, continue only narrow concrete restart/concurrency source audit.
