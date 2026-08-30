# LAB-090 main-divergence conflict audit — 2026-08-30

## Scope

Fresh audit of draft PR #175 (`lab-090-provider-activation-fencing`) against current `main`, following the durable handoff after the premature-release fail-closed fix.

## Runtime observations

Direct git transport was probed again with:

`git ls-remote https://github.com/persfinancier-blip/ai-runtime-lab.git HEAD`

It failed before repository-code execution with `Could not resolve host: github.com`. Therefore no exact-head unittest or downstream executable PASS is claimed in this run.

The GitHub connector remained available for source/control-plane inspection.

## Exact refs observed

- PR #175 head: `9e53c6ed0340c8a3c77c22b23eb7c0340240294e`.
- Current main: `df316786015eb5abcc0d285b6ae13ce9ba0bf210`.
- Merge base: `6cc7a04496187075db1c02f3e27c1d394da53026`.
- Compare current main -> PR head: diverged, PR 15 commits ahead and 12 commits behind.

## Main-side conflict audit

Compared merge base `6cc7a044...` to current main `df316786...`.

The 12 main-side commits modify only:

- `research/2026-08-30-lab090-committed-fenced-release-protocol.md`
- `research/2026-08-30-lab090-durable-activation-ticket-integration.md`
- `research/2026-08-30-lab090-post-provider-commit-fence-release-race.md`
- `research/2026-08-30-lab090-premature-release-fail-closed-fix.md`
- `research/2026-08-30-lab090-premature-release-fail-open-audit.md`
- `research/2026-08-30-lab090-provider-activation-primitive.md`
- `state/CURRENT.md`

PR #175 changes exactly six implementation/test paths:

- `experiments/provider_generation_history/activation.py`
- `experiments/provider_generation_history/supported.py`
- `experiments/provider_generation_history/tests/test_activation.py`
- `experiments/provider_generation_history/tests/test_activation_integration.py`
- `experiments/provider_generation_history/tests/test_activation_premature_release.py`
- `experiments/provider_generation_history/tests/test_integration.py`

There is **no path overlap** between the 12 current-main-side commits and the six PR #175 paths. This rules out a direct file-content conflict introduced by the post-merge-base main changes. GitHub currently reports PR #175 `mergeable=false`, but that signal is therefore not evidence of a semantic/code conflict in the LAB-090 implementation files.

## Fresh source audit of the corrected head

Re-read the branch versions of `activation.py` and `supported.py`.

The previously required ordering is present:

1. `prepare_activation()` installs provider-owned pending fence at the exact expected position;
2. SQL stores the exact ticket with status `SQL_COMMITTED` in the same transaction as generation rotation;
3. `commit_activation()` records provider commitment while retaining `pending`, yielding `COMMITTED_FENCED`;
4. coordinator accepts only `COMMITTED_FENCED` before durable acknowledgement;
5. `_mark_activation_committed()` durably updates the exact ticket to `COMMITTED`;
6. only then `_release_committed_activation()` removes the provider fence;
7. restart with `SQL_COMMITTED + RELEASED` fails closed;
8. restart with durable `COMMITTED + COMMITTED_FENCED` completes release idempotently.

No new source-level defect was established in this pass. This is not a substitute for executable validation.

## Decision

- Keep PR #175 draft.
- Do not attempt low-level ref/tree manipulation or force-update to eliminate branch divergence.
- Do not claim merge readiness from the no-overlap result alone.
- The next highest-value operation remains exact-head execution of the LAB-090 focused/integration/downstream suites when direct checkout becomes available. If transport remains unavailable, continue source-level restart/concurrency audit only for concretely reproducible defects.

LAB-086 remains priority #1 and should preempt this fallback as soon as a supported byte-preserving composition path becomes available.
