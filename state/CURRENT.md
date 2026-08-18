# Current Lab State

Last updated: 2026-08-18

## Active objective

Move from example-driven correctness testing to systematic bounded state-space exploration. LAB-016 measured the local cost of the transactional correctness stack and validated a safe two-transaction boundary, but its remote audit also found another late-duplicate terminal-monotonicity defect that narrower tests had missed. The next priority is to make this class of regression automatically discoverable.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-016.
- Completed: #30 / LAB-016 correctness-kernel overhead and batching benchmark.
- LAB-016 PR #31 squash-merged as `1564e5e6507b3365a7a6b21f071b000af3a69c2e`.
- Next: #32 / LAB-017 model-based state-space exploration and invariant fuzzing — READY.
- Active branch/PR for LAB-017: none yet.

## Last completed step

LAB-016 built `experiments/correctness_overhead/` and compared an unsafe one-transaction terminal baseline, the current six-transaction LAB-015 path, and a safe two-transaction batching candidate around the external side-effect boundary. A methodological pilot was discarded because schema initialization was inside the timed path. A later remote patch audit found that the initial batching candidate could reopen terminal `DONE` on late duplicate delivery; that implementation/results were also discarded. The corrected candidate added terminal monotonicity protection and was rerun.

Final local results: 5/5 batching invariants passed and compileall passed. Uncontended median improved by ~69.8–69.9% vs the six-transaction path. Four-worker throughput improved ~2.37x for 32 B evidence and ~2.09x for 64 KiB evidence; retries/conflicts fell. Negative evidence was retained: 32 B contention p95 worsened in the corrected run, so LAB-016 does not claim universal latency improvement.

## Evidence produced

- `experiments/correctness_overhead/benchmark.py`
- `experiments/correctness_overhead/results.json`
- `experiments/correctness_overhead/tests/test_batching.py`
- `experiments/correctness_overhead/README.md`
- `research/2026-08-18-correctness-overhead-and-batching.md`
- Issue #30 closed DONE.
- PR #31 merged: `1564e5e6507b3365a7a6b21f071b000af3a69c2e`.
- New follow-up Issue #32 / LAB-017 created.

## Findings carried forward

- safe batching boundary: transaction A = claim/fence + durable intent + outbox; external effect/reconciliation; transaction B = confirmation + evidence + fresh terminal decision;
- never batch across the external side-effect boundary or cache authoritative fence/evidence checks at terminal commit;
- terminal `DONE` remains monotonic under duplicate delivery;
- fewer transaction boundaries materially improved local median/throughput in SQLite but tail latency remained workload-dependent;
- audit repeatedly finding defects after example tests pass is now itself evidence that bounded model/state exploration is high leverage.

## Known blockers / constraints

- No current blocking issue is known.
- Direct local network/tool availability remains per-run; use connector-first exact-source audit where needed.
- SQLite performance results do not predict PostgreSQL/hardware-general latency.
- Open-model serving efficiency remains deferred until representative target hardware/runtime is available.

## Exact next action

Select Issue #32 / LAB-017. Research primary-source state-machine/concurrency verification mechanisms (TLA+/PlusCal or Apalache, Jepsen/Knossos-style checking, and an implementation-level property/state-machine approach). Build a small storage-independent Python model and deterministic bounded explorer. Require it to rediscover the historical unsafe split-completion and reopen-terminal defects automatically, emit short replayable counterexample traces, then demonstrate the corrected model passes a documented search bound plus seeded randomized schedules. Persist code, traces, research, tests and audit before integration.

## Backlog

- #32 / LAB-017 — model-based state-space exploration and invariant fuzzing — READY and next.
- PostgreSQL-specific performance/locking validation — defer until a representative PostgreSQL runtime is actually available.
- Open-model serving efficiency — DEFERRED pending representative hardware/runtime.
