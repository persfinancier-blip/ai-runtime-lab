# LAB-090 provider activation state concurrency audit and fix

Date: 2026-08-31

## Finding

The LAB-090 provider primitive claimed `prepare_activation()` as an atomic external linearization point, but the in-repository `ActivationState` model had no synchronization. Multiple `FencedActivationProvider` objects may intentionally share one `ActivationState` to model provider-side durability across coordinator reconstruction. Concurrent calls could therefore interleave reads/writes of `pending`, `next_fence`, and `committed`.

A particularly damaging schedule is two concurrent `prepare_activation()` calls that both observe `pending is None` before either installs its ticket. Both can return reservations. SQL later serializes generation rotation, but that is too late: provider-side single-reservation atomicity has already been violated and the durable SQL winner can subsequently encounter a provider ticket/status mismatch.

A second race existed between `prepare_activation()` and `increment()`: `increment()` could observe no pending ticket, then `prepare_activation()` could install the fence before the inherited increment mutates the provider position. The provider position could therefore advance after activation reservation despite the intended fence.

This is correctness/availability and linearizability failure, not an authority-escalation claim.

## Fix

Draft PR #175 branch `lab-090-provider-activation-fencing` now serializes all activation-state transitions and provider increments with a shared re-entrant lock stored in `ActivationState`.

Implementation commit: `8d05c5ffeef1d770af3ec4bc700d556a8f905c23`.

Published `activation.py` blob: `fbc8cb4f581221c8b8755a43c436e4d6be74c7a7`.

A re-entrant lock is required because `commit_activation()`, `release_activation()`, and `abort_activation()` call `activation_status()` while holding the same provider-state lock.

The lock covers the complete `increment()` check-and-mutate path, not only the `pending` read, so an increment cannot linearize between activation-position validation and reservation installation.

## Regression

Added `experiments/provider_generation_history/tests/test_activation_concurrency.py` in commit `4d2d4f46e718e595ace9bbc963925e0415a5d869`.

Published test blob: `80495b18cd17fa6b8c1af728ca5232ec1da9b486`.

The regression uses a shared test state whose `next_fence` getter deliberately widens the pre-fix race window. It checks:

1. two synchronized distinct prepares have exactly one winner and one `ActivationFenced` loser;
2. prepare versus increment is serializable: they may linearize in either order, but both cannot succeed from position 10.

## Exact-byte execution

Direct git transport remained unavailable in this runtime (`Could not resolve host: github.com`), so the relevant files were reconstructed from GitHub connector responses and independently Git-blob hashed before execution.

Observed hashes in the execution sandbox:

- `experiments/provider_generation_history/activation.py` -> `fbc8cb4f581221c8b8755a43c436e4d6be74c7a7` (matches published blob exactly);
- `experiments/provider_generation_history/tests/test_activation_concurrency.py` -> `80495b18cd17fa6b8c1af728ca5232ec1da9b486` (matches published blob exactly);
- existing `experiments/provider_generation_history/tests/test_activation.py` -> `31d421a1c8e62067d6b90d2aaeb47ddfeb84a800` (matches published blob exactly);
- dependency `experiments/anchor_attestation/protocol.py` -> `15d8b7cf8ff093490ccb75679030d3a0fe41e401` (matches published blob exactly).

Executed:

```text
PYTHONPATH=. python -m unittest \
  experiments.provider_generation_history.tests.test_activation \
  experiments.provider_generation_history.tests.test_activation_concurrency -v
```

Result: **10/10 PASS**.

Also executed `python -m compileall -q` for the exact-hash activation implementation and both primitive/concurrency test files: **PASS**.

This is exact-byte evidence for the provider primitive/concurrency slice only. It is not a whole-PR or downstream integration PASS.

## Remaining gate

PR #175 remains draft. The next executable work is the previously retained exact-head activation integration/restart/downstream suite. LAB-086 remains priority #1 whenever a safe byte-preserving predecessor+patch composition path becomes available.
