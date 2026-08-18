# Current Lab State

Last updated: 2026-08-19

## Active objective

Move from bounded abstract correctness exploration to model/implementation conformance. LAB-017 now automatically rediscovers historical cross-layer defects as short traces; the next risk is semantic drift between that correct abstract model and executable SQL/kernel implementations.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-017.
- Completed: #32 / LAB-017 model-based state-space exploration and invariant fuzzing.
- LAB-017 PR #33 squash-merged as `99a9f37c7d5babe9a31d26d65a4ef548314adb20`.
- Next: #34 / LAB-018 abstract-model / implementation conformance harness — READY.
- Active branch/PR for LAB-018: none yet.

## Last completed step

LAB-017 built a storage-independent state/action model and bounded BFS explorer. The corrected model passed depth 8 (314 queued states) and seed 17017 / 1000 x 20-step randomized schedules. It automatically found the historical invalid-evidence completion trace and terminal-reopen-on-duplicate trace, plus a stale-authority mutation variant. Local unittest passed 5/5. Remote patch audit found no unresolved blocker and PR #33 was merged.

Implementation audit also found and fixed a defect in the first abstract model itself: effect execution had been over-permitted from CONFIRMED and is now restricted to INTENT/UNKNOWN.

## Evidence produced

- `experiments/state_space_kernel/model.py`
- `experiments/state_space_kernel/test_model.py`
- `experiments/state_space_kernel/README.md`
- `research/2026-08-19-state-space-exploration.md`
- Issue #32 closed DONE.
- PR #33 merged: `99a9f37c7d5babe9a31d26d65a4ef548314adb20`.
- Follow-up Issue #34 / LAB-018 created.

## Findings carried forward

- bounded model exploration is a falsification/regression amplifier, not universal proof;
- every new cross-layer defect should be reduced to a replayable action/invariant trace;
- short abstract traces expose invalid-evidence completion, terminal reopening and stale authority with less incidental implementation detail;
- a correct abstract model still does not prove an implementation conforms to it.

## Known blockers / constraints

- No current blocking issue is known.
- Direct local network/tool availability remains per-run.
- PostgreSQL-specific performance/locking validation remains deferred until representative PostgreSQL is available.
- Open-model serving efficiency remains deferred pending representative hardware/runtime.

## Exact next action

Select Issue #34 / LAB-018. Reuse LAB-017 traces as executable contracts against an implementation adapter, preferably the existing SQLite transactional kernel. Normalize implementation observations to abstract state and compare after each authoritative action. Seed implementation-only drift variants for terminal reopening, stale fence acceptance, invalid-evidence completion, UNKNOWN retry, and invalidation semantics; require first-divergence replay traces before integration.

## Backlog

- #34 / LAB-018 — abstract-model / implementation conformance harness — READY and next.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
