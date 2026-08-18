# Long-Horizon Memory Benchmark

Deterministic standard-library benchmark for LAB-009.

## Question

Which lightweight memory representation best preserves **current and causally relevant** facts when the history contains distractors, superseded facts, invalidated provenance, objective changes, and a long noisy tail?

## Strategies

1. `recency` — last `k` events only.
2. `similarity` — token-overlap proxy for vector/semantic retrieval.
3. `typed_temporal_graph` — typed facts with supersession/invalidation plus explicit causal links.
4. `bounded_hybrid` — graph/currentness filter first, then similarity fill within a fixed retrieval budget.

The benchmark intentionally does not call an LLM or vector database. The point is to isolate memory representation/retrieval semantics from model quality.

## Seeded cases

- superseded deployment region;
- semantically similar database distractors;
- causal incident -> operational decision chain;
- changed optimization objective;
- invalid draft conflicting with approved policy;
- long-horizon noise after a valid current fact.

## Metrics

- `current_causal_recall` — fraction of required current/causal facts retrieved.
- `stale_intrusion` — fraction of returned memories known to be stale/superseded/invalidated.

These are deliberately separate. A strategy can look highly relevant while still returning stale facts.

## Observed local result

A deterministic local run and a 7-test validation suite produced:

| Strategy | Mean current/causal recall | Mean stale intrusion |
|---|---:|---:|
| recency | 0.8333 | 0.1667 |
| similarity | 1.0000 | 0.2222 |
| typed temporal graph | 1.0000 | 0.0000 |
| bounded hybrid | 1.0000 | 0.0000 |

The seeded naive failures are intentional:

- recency misses the current warehouse carrier after a sufficiently long distractor tail;
- similarity retrieves the correct current fact but also surfaces stale/superseded memories in multiple cases.

## Run

```bash
python -m unittest discover -s experiments/long_horizon_memory/tests -p 'test_*.py' -v
python experiments/long_horizon_memory/benchmark.py
```

## Boundary

This is a memory-selection experiment, not a production knowledge graph, vector store, or conversational-memory product. Authoritative execution state remains LAB-005 run state; evidence provenance remains LAB-007 evidence ledger. Memory may reference those records but must not replace them.
