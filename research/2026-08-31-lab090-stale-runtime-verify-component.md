# LAB-090 stale-runtime `verify_component` audit

Date: 2026-08-31
Issue: #169
PR: #175 (`lab-090-provider-activation-fencing`)

## Finding

A lost provider-fence release can leave this durable/live split:

- provider-generation history/head: new generation G2;
- activation row: `COMMITTED`;
- provider G2: `COMMITTED_FENCED` until release succeeds;
- live `SupportedHistoricalSharedAnchorLedger.attested`: old generation G1 because `rotate_provider()` raises before swapping runtime.

The prior LAB-090 stale-runtime fix guarded `reserve()`, but inherited LAB-080 `verify_component()` still performed its authenticated read through `self.attested` and then compared that observation with inherited `_provider()`, which also described `self.attested`. Therefore a stale G1 runtime could verify freshness against G1 after the durable cutover to G2.

This is a freshness/correctness boundary failure, not an authority expansion: after durable provider rotation, current-provider reads must not silently use a historical runtime generation.

## Regression

Published on PR #175:

- commit `17f504176cdcffe8c9304807d169a31d02d07326`
- `experiments/provider_generation_history/tests/test_activation_stale_verify_component.py`
- blob `b1f3e06b0b67da5ee892c5e0b35650dd3567b71f`

The regression reproduces a release outage, confirms durable head G2 while the live object still references G1, and requires `verify_component("component-A")` to fail closed with `CurrentGenerationRequired`.

The exact published regression bytes were independently reconstructed and Git-blob hashed to `b1f3e06b...`; `py_compile` PASS. This is syntax/identity evidence only, not a whole-branch unittest PASS.

## Fix

Published on PR #175:

- commit `82d15ca21543ba2c70d1a11b7df0633e5cc387f1`
- `experiments/provider_generation_history/supported.py` blob `6aee4eaec6d34563ea82c2a3216a82fb1d157c00`

`SupportedHistoricalSharedAnchorLedger` now overrides `_provider()` to first call `_require_runtime_matches_durable_head()` and only then expose the durable provider identity. This makes inherited current-provider read surfaces fail closed when the live runtime is stale.

GitHub commit diff confirms the implementation change is exactly four added lines and no unrelated source mutation.

## Validation / limitations

Direct `git ls-remote` again failed before repository-code execution with `Could not resolve host: github.com`, so exact whole-branch execution remains unavailable in this run. No unittest PASS is claimed for the new behavioral regression.

Current PR #175 is heavily diverged from main (27 ahead / 30 behind). A merge-base-to-main comparison shows the main-side commits since the merge base touch only `research/*` and `state/CURRENT.md`, not LAB-090 implementation/test files. GitHub currently reports the draft PR as non-mergeable despite that no-source-overlap comparison; treat mergeability as unresolved control-plane state until rechecked.

## Next gate

1. Reconstruct/hash-verify the exact dependency closure for the activation integration/restart tests and execute the new stale-runtime `verify_component` regression plus existing activation tests when a safe byte transfer path is available.
2. Re-audit `verify_component` for a concurrent generation-head change between the initial current-runtime check and final watermark commit; do not claim that race closed solely by this stable-stale fix.
3. Keep PR #175 draft until exact integration/restart/downstream gates are clean.
