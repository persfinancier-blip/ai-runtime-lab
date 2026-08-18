# Long-Horizon Memory with Causality and Provenance

Date: 2026-08-18  
Issue: #16 / LAB-009  
Branch: `lab/009-long-horizon-memory`

## Research question

Which memory representation best preserves current task facts and causal dependencies across long histories containing distractors, stale facts, supersession, objective changes, and provenance conflicts?

## Primary donors

### 1. AMA-Bench / AMA-Agent (2026)

Primary paper: https://arxiv.org/abs/2602.22769

Transferable mechanisms:
- evaluates agent-environment trajectories rather than only human-chat memories;
- synthetic trajectories can scale to arbitrary horizons with rule-based QA;
- reports that existing systems lose causality and objective information under similarity-oriented retrieval;
- proposes a causality graph plus tool-augmented retrieval.

Implication: memory quality needs a metric for causal/objective correctness, not only topical relevance.

### 2. Supersede (2026)

Primary paper: https://arxiv.org/abs/2606.27472

Transferable mechanisms:
- isolates temporal fact currency as a distinct memory-update problem;
- shows bounded self-maintained memory can retain stale values even when comprehension is otherwise strong;
- increasing memory budget alone does not solve supersession;
- explicitly rewards answering from the current value while penalizing stale values.

Implication: supersession/currentness must be represented and tested explicitly rather than delegated to larger context windows.

### 3. Graphiti temporal context graph

Primary repository: https://github.com/getzep/graphiti

Transferable mechanisms:
- facts carry temporal validity windows so old facts can be invalidated without deleting history;
- facts retain provenance to source episodes;
- retrieval combines semantic, keyword, and graph traversal signals;
- temporal/history queries distinguish what is true now from what was true previously.

Implication: a useful typed memory contract needs temporal validity/supersession and provenance, while hybrid retrieval can retain semantic recall after currentness filtering.

### 4. Causal Memory Intervention (supporting donor, 2026)

Primary paper: https://arxiv.org/abs/2605.17641

Transferable mechanism:
- topically similar memories may be causally irrelevant, stale, or harmful;
- evaluates memory selection against useful, irrelevant, and harmful candidates;
- motivates selecting memory by causal usefulness rather than similarity alone.

## Minimal typed memory contract tested

Each benchmark memory carries:
- stable memory ID;
- event/order time;
- typed `subject / predicate / value`;
- raw text;
- provenance/source reference;
- optional `supersedes` relation;
- invalidation flag;
- optional explicit causal parents;
- optional objective label.

This is intentionally smaller than a production graph schema.

## Deterministic experiment

Implementation: `experiments/long_horizon_memory/`.

Four strategies operate on the same six cases and fixed top-k budget:
1. transcript/recency;
2. token-overlap similarity proxy;
3. typed temporal/provenance graph;
4. bounded hybrid: graph/currentness filtering plus similarity fill.

Seeded cases cover:
- stale supersession;
- semantic distractors;
- causal chains;
- objective changes;
- provenance invalidation/conflict;
- long-horizon distractor tails.

### Metrics

`current_causal_recall` measures retrieval of facts required for the current answer/reasoning chain.

`stale_intrusion` measures how much of the returned context is known stale, superseded, or invalidated.

The metrics are deliberately separate so a strategy cannot hide stale retrieval behind high relevance/recall.

### Observed result

A local deterministic run produced:

| Strategy | Mean current/causal recall | Mean stale intrusion |
|---|---:|---:|
| recency | 0.8333 | 0.1667 |
| similarity | 1.0000 | 0.2222 |
| typed temporal graph | 1.0000 | 0.0000 |
| bounded hybrid | 1.0000 | 0.0000 |

A 7-test local validation suite passed.

Seeded naive failures:
- recency returned only recent noise and missed the current warehouse carrier in the long-horizon case;
- similarity recovered the correct current fact but also retrieved stale/superseded memories in four or more cases, yielding 22.22% mean stale intrusion.

## Findings

1. **Relevance and correctness are not the same metric.** Similarity can achieve perfect required-fact recall while simultaneously returning stale facts.
2. **Recency is not a long-horizon memory policy.** Sufficient unrelated activity can evict an important current fact even when it remains authoritative.
3. **Supersession/invalidation must be first-class.** Bigger windows or better semantic similarity do not inherently establish which fact is current.
4. **Causal edges improve `why` retrieval.** An operational decision can pull its incident/cause without requiring the cause text itself to dominate semantic similarity.
5. **Hybrid retrieval is the practical shape suggested by this experiment.** First enforce typed temporal/provenance eligibility, then use relevance signals within the surviving set and bounded budget.
6. **Provenance is useful but not self-authenticating.** A memory source reference should point to LAB-007 evidence when authority matters; memory itself must not manufacture trust.

## Integration boundaries

### LAB-005 durable run state

Run state remains authoritative for execution phase, ownership/fencing, idempotency, and side-effect status. Long-horizon memory may help planning but must never overwrite or infer authoritative execution state when the durable state record exists.

### LAB-007 evidence ledger

Evidence remains the source for observed/tested/provenance claims. Memory can store typed references to evidence IDs and cache derived facts, but invalidation/supersession of a memory record does not rewrite the append-only evidence history.

### LAB-008 capability planner

Capability observations are freshness-bounded operational facts. If surfaced through memory, their TTL/freshness and evidence identity remain eligibility constraints rather than soft semantic features.

## Recommended protocol direction

For future memory work, prefer a bounded hybrid pipeline:

1. identify typed task/objective/entity scope;
2. reject invalidated and superseded records;
3. enforce temporal/currentness rules;
4. expand explicit causal dependencies where the query needs explanation;
5. use semantic/keyword relevance to rank the eligible set;
6. retain provenance/evidence references in the returned context;
7. keep context bounded and reconstructable.

Do not use similarity alone as the authority resolver.

## Non-goals

- no production vector database;
- no general knowledge graph engine;
- no LLM-based memory extraction;
- no claim that this small synthetic benchmark predicts every production workload;
- no conflation of memory, durable execution state, or evidence.

## Stop-condition assessment

Four current primary research/implementation donors were inspected. Four strategies were compared on identical deterministic cases. The benchmark exposes naive recency/similarity failure and identifies typed temporal/provenance eligibility plus bounded hybrid ranking as the strongest representation in the seeded cases. The issue should proceed to audit/integration rather than expand into infrastructure.