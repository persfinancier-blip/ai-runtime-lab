# Model / Implementation Conformance Harness

LAB-018 replays one action trace against two independent representations:

1. the LAB-017 abstract model (`experiments/state_space_kernel/model.py`);
2. the LAB-015 SQLite transactional kernel through `KernelAdapter`.

After every action, implementation state is normalized to the abstract `State` schema. `compare()` stops at the first divergent step and returns the action, differing fields, model state, implementation state, and replayable prefix.

## Run

```bash
python -m unittest experiments.model_conformance.test_harness -v
python -m unittest experiments.state_space_kernel.test_model -v
python -m unittest discover -s experiments/transactional_kernel/tests -p 'test_*.py' -v
```

`bounded_traces(3)` enumerates 1,111 traces (including the empty trace and all prefixes through depth 3) over the LAB-017 action alphabet. The fixed corpus adds longer semantic paths such as UNKNOWN reconciliation, completion/invalidation, duplicate delivery and stale mutation.

## Seeded implementation drift

The adapter can inject five implementation-only defects:

- `reopen_done`
- `stale_fence`
- `invalid_completion`
- `unknown_retry`
- `terminal_invalidation`

Each must produce a first-divergence report rather than merely fail a final-state assertion.

## Important boundary

Conformance is only as good as the abstraction. LAB-018 itself found abstract-model defects (unclaimed authority and INVALID reopening) and implementation defects (terminal invalidation and terminal effect mutation). The harness therefore treats disagreement as a diagnostic signal, not as proof that the model is automatically right.
