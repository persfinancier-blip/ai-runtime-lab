# Orchestration Topology Benchmark

Deterministic LAB-013 benchmark comparing three orchestration shapes under the same worker, evidence, idempotency, verification, and retry assumptions:

- `single`: one bounded sequential context;
- `manager`: central coordinator with isolated specialist results and explicit synthesis;
- `peer`: bounded handoff chain forwarding context between active peers.

The benchmark does **not** call an LLM. The manipulated variable is context ownership/routing structure, not model quality.

## Run

```bash
python -m unittest discover -s experiments/orchestration_topologies/tests -v
python experiments/orchestration_topologies/benchmark.py
```

## Metrics

`correct`, `messages`, `coordination_steps`, `work_calls`, `duplicate_deliveries`, `stale_context_events`, `failures_contained`, `recoveries`, and `surfaced_evidence`.

`cost = messages + coordination_steps + work_calls` is a structural coordination proxy, not a token, latency, or currency estimate.

## Fixed correctness rules

Every topology receives the same scenario events and uses the same:

- logical work IDs and duplicate suppression;
- stale evidence/version rule;
- authoritative conflict-resolution rule;
- one-failure deterministic retry rule;
- terminal verifier.

The manager may filter stale specialist evidence at its isolation boundary, while single/peer contexts may temporarily carry it; all still use the same terminal verifier. Context capacity is also identical where contexts are shared. Manager specialist outputs are isolated, so its synthesis does not consume the shared-context budget.

## Audit note

The initial prototype hardcoded several success/failure outcomes by topology. That design was rejected during audit because it merely encoded the intended conclusion. The corrected benchmark lets differences emerge from context retention/isolation and coordination structure. Stale evidence, conflicting evidence, duplicate delivery, and worker failure now complete correctly under all topologies when the shared correctness mechanisms can resolve them.

## Non-goals

This is not evidence that one framework, model, or topology is globally superior. Absolute correctness percentages are not workload population estimates. The experiment only tests specific topology mechanics under controlled synthetic conditions.
