# LAB-090 premature-release fail-closed fix — 2026-08-30

## Objective

Close the source-audited protocol violation in draft PR #175 where coordinator recovery accepted provider status `RELEASED` while the durable activation row was still `SQL_COMMITTED`.

## Defect

`RELEASED` means the provider-side external increment fence has already been removed. Before the coordinator durably acknowledges the exact activation ticket as `COMMITTED`, accepting that state is fail-open: an external writer can advance the candidate provider before SQLite has recorded the acknowledgement that authorizes release.

The previously published PR source admitted this in two places:

- `_commit_or_reconcile_activation()` accepted both `COMMITTED_FENCED` and `RELEASED` before `_mark_activation_committed()`;
- `_recover_pending_activation()` accepted `SQLite=SQL_COMMITTED + provider=RELEASED`, promoted the durable row to `COMMITTED`, and then treated release as idempotent.

## Implemented correction

Draft PR #175 branch `lab-090-provider-activation-fencing` now fails closed:

1. `_commit_or_reconcile_activation()` accepts only `COMMITTED_FENCED` before durable acknowledgement.
2. `_recover_pending_activation()` with durable `SQL_COMMITTED` accepts only:
   - `PREPARED` -> commit/reconcile while retaining the fence;
   - `COMMITTED_FENCED` -> durable acknowledgement, then release.
3. `SQL_COMMITTED + RELEASED` raises `HistoricalVerificationError("provider activation released before durable acknowledgement")`.
4. `RELEASED` remains idempotently accepted only when the durable row is already `COMMITTED`.

Published fix commit: `3f6c7a32e12ee57d82fca87abab27dbe1d3fe2dc`.

A dedicated regression was added as `experiments/provider_generation_history/tests/test_activation_premature_release.py` at commit `9e53c6ed0340c8a3c77c22b23eb7c0340240294e`. The test models a faulty provider that commits and immediately releases its exact ticket before coordinator acknowledgement; rotation must fail closed, leave durable status `SQL_COMMITTED`, and restart must also reject the premature-release state.

## Validation actually observed in this run

- Branch source re-fetched after publication: PR head observed as `9e53c6ed0340c8a3c77c22b23eb7c0340240294e`.
- GitHub PR metadata now reports `mergeable=true`; the PR remains draft.
- Explicit compare against current `main` (`0fa5d40611e2c11023e9c06e0c643c7b198377f4`) reports the branch is still diverged: 15 commits ahead, 10 behind, merge-base `6cc7a04496187075db1c02f3e27c1d394da53026`.
- Direct branch checkout/execution was attempted in the current runtime and failed before repository code execution because `github.com` could not be resolved. Therefore no unittest PASS is claimed for this exact head.

## Remaining gate

Keep PR #175 draft. Next run should first retry exact-head execution of:

- `test_activation.py`;
- `test_activation_integration.py`;
- `test_activation_premature_release.py`;
- existing provider-generation integration;
- downstream shared-anchor/provider-history suites.

Then audit the current main/head divergence for semantic conflicts before any readiness/merge decision.
