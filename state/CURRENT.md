# Current Lab State

Last updated: 2026-08-18

## Active objective

Measure the execution cost of the correctness stack without weakening it. LAB-015 moved the kernel from file-backed semantics to an executable transactional approximation and proved the key storage-boundary invariants under races, rollback, stale fences, duplicate delivery, and completion/evidence ordering. The next question is how much these protections cost and which operations can be batched safely.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-015.
- Completed: #28 / LAB-015 transactional correctness kernel.
- LAB-015 PR #29 squash-merged as `327110abfd5eed4383c7bc92ab88aa1d7167d950`.
- Next: #30 / LAB-016 correctness-kernel overhead and batching benchmark — READY.
- Active branch/PR for LAB-016: none yet.

## Last completed step

LAB-015 created `experiments/transactional_kernel/` using standard-library SQLite as an executable approximation of SQL transactional semantics. The deliberately unsafe split-transaction completion design checked evidence validity, allowed invalidation, and then committed `DONE`; its expected-safety test failed with `unsafe split transaction committed invalid DONE`.

The corrected prototype binds claim generation+fence, state+outbox intent, and evidence-validity+completion at transactional boundaries. The initial 12-test matrix passed. A separate remote patch audit then found a terminal-monotonicity defect: late duplicate delivery could call `prepare_intent()` and reopen a `DONE` item as `INTENT`. The branch was corrected before merge and a regression test added. Final corrected matrix: 13/13 tests passed; `python -m compileall -q experiments/transactional_kernel` passed.

## Evidence produced

- `experiments/transactional_kernel/kernel.py`
- `experiments/transactional_kernel/tests/test_kernel.py`
- `experiments/transactional_kernel/tests/unsafe_seed_expected_failure.py`
- `experiments/transactional_kernel/README.md`
- `research/2026-08-18-transactional-correctness-kernel.md`
- Issue #28 closed DONE.
- PR #29 merged: `327110abfd5eed4383c7bc92ab88aa1d7167d950`.
- New follow-up Issue #30 / LAB-016 created.

## Findings carried forward

- atomicity belongs at the storage boundary, not in caller discipline;
- generation and fence advance together on claim; stale workers cannot mutate authoritative state;
- external-effect intent and outbox identity must commit together;
- terminal completion must read authoritative evidence validity/version and write `DONE` in the same deciding transaction;
- serialization/deadlock/lock conflicts are retryable transaction outcomes, never permission to weaken invariants;
- terminal state is monotonic under late duplicate delivery;
- SQLite proves invariants only approximately; PostgreSQL production semantics require row-level locking/conditional updates, short transactions, uniqueness constraints, and retry handling.

## Known blockers / constraints

- No current blocking issue is known.
- Direct local network access remains a per-run capability; use connector-first exact-source audit when needed.
- LAB-016 measurements are local runtime/SQLite measurements only and must not be generalized to PostgreSQL, other hardware, or production latency.
- Open-model serving efficiency remains deferred until representative target hardware/runtime is available; decorative benchmarking remains disallowed.

## Exact next action

Select Issue #30 / LAB-016. Build `experiments/correctness_overhead/` and benchmark a minimal unsafe baseline, full correctness path, and at least one safe batching variant under uncontended/contended conditions and small/larger evidence payloads. Record robust latency distributions, transaction/conflict counts and practical write amplification. Re-run correctness invariants for any optimization candidate; reject optimizations that require stale authoritative checks or weakened atomicity. Persist raw/summary results, audit the benchmark for methodological bias, integrate safely, and update this state.

## Backlog

- #30 / LAB-016 — correctness-kernel overhead and batching benchmark — READY and next.
- Open-model serving efficiency — DEFERRED pending representative hardware/runtime.
