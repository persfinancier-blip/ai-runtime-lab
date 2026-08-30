# LAB-090 — committed-fenced provider acknowledgement protocol

Date: 2026-08-30

## Objective

Close the concrete post-provider-commit race found on draft PR #175: provider commitment previously cleared the provider-side activation reservation before the coordinator durably acknowledged the exact activation ticket in SQLite. In that window an external writer could advance the newly current provider while the coordinator still held `SQL_COMMITTED`.

## Implemented correction

Draft PR #175 now uses an explicit provider lifecycle equivalent to:

`PREPARED -> COMMITTED_FENCED -> RELEASED`

Properties:

- `prepare_activation()` installs the provider-side exact-position fence.
- `commit_activation()` durably records provider commitment but deliberately leaves the same exact ticket in `activation_state.pending`.
- ordinary provider `increment()` remains rejected while the ticket is `PREPARED` or `COMMITTED_FENCED`.
- coordinator `_mark_activation_committed()` durably changes the exact SQLite activation row from `SQL_COMMITTED` to `COMMITTED`.
- only after that durable acknowledgement does coordinator call exact-ticket `release_activation()`.
- `release_activation()` is idempotent for the already released ticket and refuses a stale/different exact ticket.
- restart reconciliation handles both `SQL_COMMITTED + PREPARED/COMMITTED_FENCED` and `COMMITTED + COMMITTED_FENCED`; the latter completes a release that was lost after SQLite acknowledgement.

## Regressions added

- provider-level commit remains fenced until explicit release;
- lost acknowledgement after provider commit remains `COMMITTED_FENCED`;
- provider-owned state preserves the committed fence across coordinator reconstruction;
- stale/different ticket cannot release the fence;
- integration hook attempts external advance immediately after provider commit but before coordinator SQLite acknowledgement and must receive `ActivationFenced`;
- simulated outage on first provider release leaves SQLite `COMMITTED` and provider `COMMITTED_FENCED`; restart with the same provider-owned durable state releases the exact ticket and permits later increment.

## Published branch state

Draft PR: #175
Branch: `lab-090-provider-activation-fencing`
Head after correction: `348b279d979600e4a03333bc6ed729922705ff5b`

Relevant published blobs after correction:

- `experiments/provider_generation_history/activation.py`: `a8620d2f02fc8f489d382ccc467ea14b6324f180`
- `experiments/provider_generation_history/supported.py`: `be54ede1de1c3282b32af354e1ba7c7dab0a41bd`
- `experiments/provider_generation_history/tests/test_activation.py`: `31d421a1c8e62067d6b90d2aaeb47ddfeb84a800`
- `experiments/provider_generation_history/tests/test_activation_integration.py`: `cf85e7dfec2a59d96a5f8497a02b65641a8c246b`

A fresh PR diff audit confirmed the intended ordering in published source: provider commit preserves `pending`; coordinator marks the exact durable activation row `COMMITTED`; only then does coordinator release the exact provider ticket.

## Validation truth

Exact branch execution was attempted in this run with a fresh shallow clone and failed before repository code execution:

`Could not resolve host: github.com`

Therefore no whole-branch or unittest PASS is claimed from this run. The code/tests are published and source-audited, but executable validation remains pending until direct branch transport is available or another safe exact-byte execution bridge appears.

## Remaining gate

Keep PR #175 draft. Next run should first attempt LAB-086 exact hidden-rowid publication if a byte-preserving composition bridge appears. Otherwise, for LAB-090, execute exact published branch tests plus downstream provider-generation/shared-anchor regressions; fix any failures and perform a fresh concurrency/restart audit before considering ready-for-review.
