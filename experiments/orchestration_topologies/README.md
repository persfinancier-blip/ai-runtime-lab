# Orchestration Topology Benchmark

Deterministic LAB-013 benchmark comparing three orchestration shapes under the same evidence/idempotency/recovery assumptions:

- `single`: one sequential execution context;
- `manager`: central coordinator with isolated specialist results and explicit synthesis;
- `peer`: bounded handoff chain where each active peer forwards state to the next.

The benchmark does **not** call an LLM. Worker behavior is deterministic so topology effects can be inspected without model variance.

## Run

```bash
python -m unittest discover -s experiments/orchestration_topologies/tests -v
python experiments/orchestration_topologies/benchmark.py
```

## Metrics

`correct`, `messages`, `coordination_steps`, `work_calls`, `duplicated_work`, `stale_context_events`, `failures_contained`, `recoveries`, and `evidence_conflicts`.

`cost = messages + coordination_steps + work_calls + duplicated_work` is intentionally simple: it is a coordination proxy, not a token/currency estimate.

## Important fixed assumptions

All topologies share the same logical work IDs and idempotency/evidence rules. In the duplicate-delivery scenario all three therefore avoid duplicated side effects. The benchmark changes routing/context ownership, not the evidence or side-effect safety contract.

## Non-goals

This is not evidence that one framework or model is globally superior. It is a falsifiable synthetic comparison of topology-specific failure modes and overhead.
