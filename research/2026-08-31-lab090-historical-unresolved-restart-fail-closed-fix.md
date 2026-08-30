# LAB-090 historical unresolved activation restart — fail-closed fix

Date: 2026-08-31
Issue: #169
Draft PR: #175
Branch: `lab-090-provider-activation-fencing`

## Problem

A database produced by the older overlapping-rotation behavior can contain an activation row for historical generation G2 with `status='SQL_COMMITTED'` while the durable provider-generation head is already G3.

The constructor first reconciles only the activation row for the durable current generation. Before this fix, `_verify_activation_records()` accepted `SQL_COMMITTED` for any historical generation. Because the persistent `block_intent_during_provider_activation` trigger blocks new intents whenever *any* row is `SQL_COMMITTED`, and the rotation path also blocks while any unresolved activation exists, restart could succeed into a permanently unavailable state. The current G3 runtime cannot safely infer or clear the historical G2 provider reservation.

This is a fail-closed availability/correctness defect, not an authority expansion.

## Fix

PR #175 commit `d6c9306d7df5ef106be1bfaca85eefe8236b7b6a` adds one verifier rule after current-generation recovery:

- read the durable current generation;
- if an activation row remains `SQL_COMMITTED` and its `new_generation_id` is not that durable current generation, raise `HistoricalVerificationError`;
- do not auto-clear, release, abort, or otherwise reconcile historical provider activation state.

GitHub's commit diff confirms the commit changes only `experiments/provider_generation_history/supported.py` and adds exactly this guard.

The expected-RED regression already published in commit `0cbbfd2477db1774b0cadc5294cd85c2b5495d17`, `test_activation_historical_unresolved_restart.py`, constructs G1→G2→G3, restores G2 to `SQL_COMMITTED`, and requires constructor restart with valid G3 runtime to raise `HistoricalVerificationError`.

## Validation actually performed

- Exact GitHub commit diff audited: only the intended verifier guard was added.
- Direct `git ls-remote https://github.com/persfinancier-blip/ai-runtime-lab.git HEAD` was attempted in this run and failed before repository-code execution with `Could not resolve host: github.com`.
- Therefore no exact-head unittest/compileall PASS is claimed in this run.

## Security/correctness audit

The guard executes after `_recover_pending_activation()`. Thus a legitimate unresolved activation for the *current* durable generation still has its existing recovery opportunity. Any unresolved activation left for an older generation is instead treated as durable-state inconsistency. This preserves the existing recovery semantics while avoiding unsafe inference about an external provider fence that the current runtime does not control.

## Remaining gate

Keep PR #175 draft until exact published-head execution covers:

- `test_activation_historical_unresolved_restart.py`;
- historical retry regression;
- overlapping-rotation regression;
- activation primitive/integration/premature-release suites;
- provider-generation integration;
- downstream shared-anchor/provider-history suites.

LAB-086 remains priority #1 whenever a byte-preserving publication/execution bridge is available.
