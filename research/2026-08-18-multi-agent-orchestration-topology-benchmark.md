# Multi-Agent Orchestration Topology Benchmark

Date: 2026-08-18  
Issue: #24 / LAB-013

## Question

Once durable state, evidence, verification, capability fallback, memory safety and escalation are held fixed, when does adding agent boundaries improve reliability enough to justify coordination cost?

## Primary-source donor mechanisms

### OpenAI Agents SDK

Sources:
- https://openai.github.io/openai-agents-python/multi_agent/
- https://openai.github.io/openai-agents-python/handoffs/

Transferable distinction: **agents as tools** keeps a manager in control and is recommended when one agent should own synthesis/shared guardrails; **handoffs** transfer control to a specialist and are appropriate when the specialist should directly own the next interaction. The SDK also explicitly allows code-driven orchestration rather than requiring LLM-driven routing.

### LangChain/LangGraph multi-agent patterns

Sources:
- https://docs.langchain.com/oss/python/langchain/multi-agent/index
- https://docs.langchain.com/oss/python/langchain/multi-agent/subagents
- https://docs.langchain.com/oss/python/langchain/multi-agent/handoffs

Transferable mechanisms: supervisor/subagent topology centralizes routing and isolates subagent context; handoffs are state-driven and require explicit context engineering. The current docs explicitly warn that multi-agent is not always necessary and that a single agent can often achieve similar results. They also note extra call overhead for subagents and context-bloat/malformed-history risks for handoffs.

### Microsoft AutoGen AgentChat

Sources:
- https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/teams.html
- https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/swarm.html
- https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/selector-group-chat.html

Transferable mechanisms: AgentChat exposes materially different coordination shapes rather than one universal team abstraction: round-robin, model-selected speaker, MagenticOne, and `Swarm`. `Swarm` chooses the next speaker from explicit handoff messages while sharing message context; `SelectorGroupChat` pays an additional model-selection step to choose the next speaker.

## Benchmark design

Implementation: `experiments/orchestration_topologies/`.

Three topologies execute the same seven seeded scenarios:

1. simple task where decomposition adds no informational value;
2. decomposable independent work;
3. stale specialist output;
4. duplicate handoff delivery;
5. conflicting evidence;
6. worker failure and recovery;
7. another simple case where coordination overhead dominates.

The benchmark fixes work identity/idempotency and evidence semantics. No LLM is called. The manipulated variable is routing/context ownership:

- single = one sequential context;
- manager = central synthesis + isolated specialist result boundaries;
- peer = bounded handoff chain with state propagation.

## Observed local results

Command:

```bash
python -m unittest discover -s experiments/orchestration_topologies/tests -v
```

Observed: **8/8 tests passed**.

`python -m compileall -q experiments` also passed.

Aggregate benchmark:

| topology | correctness | mean coordination proxy cost | messages | stale-context events | failures contained | recoveries |
|---|---:|---:|---:|---:|---:|---:|
| single | 57.14% | 2.43 | 7 | 2 | 0 | 1 |
| manager | 100% | 8.00 | 28 | 0 | 3 | 3 |
| peer | 42.86% | 6.29 | 26 | 2 | 0 | 0 |

## Help case

On decomposable independent work, the manager isolates specialist outputs and preserves both results while the synthetic single shared context and peer chain lose one result through state propagation/overwrite. On stale specialist/conflicting evidence, central synthesis contains the bad result and requests fresh/tie-break evidence.

This demonstrates a condition under which extra agent boundaries can help: **the task has separable subproblems or independent evidence that benefits from context isolation plus a synthesis authority**.

## Hurt case

For a simple task, all topologies are correct but manager cost is much higher because delegation/synthesis adds messages and coordination without adding information. This is the strongest decision rule from the benchmark because it does not depend on a seeded correctness failure: **do not add agents when one bounded context can perform the task and there is no isolation/parallelism/failure-containment benefit to buy**.

## Peer/handoff finding

The peer chain is especially sensitive to stale intermediate state and a failed active peer. Explicit handoff systems therefore need a strong state/evidence boundary; merely sharing or forwarding context is not failure containment.

This does not mean handoffs are categorically bad. OpenAI and LangChain both identify direct specialist ownership/stateful conversational flow as a reason to use them. This benchmark targets reliability under synthetic engineering-style tasks, not conversational UX.

## Audit: confounds and limits

The most important threat to validity is scenario construction. The benchmark intentionally seeds context-overwrite, stale-result and central-conflict-resolution cases to expose topology mechanics. Therefore absolute correctness percentages are **not population estimates** and must not be generalized to real LLM workloads.

What is controlled:
- deterministic worker semantics;
- identical logical task/evidence identities;
- identical idempotency/duplicate-delivery protection;
- no model or tool variance;
- same seeded task set.

What is not proven:
- real-world token/cost/latency ratios;
- model-quality gains from specialization;
- benefits from true parallel execution;
- behavior on open-ended research or user-facing conversations;
- superiority of OpenAI, LangGraph or AutoGen implementations.

The coordination proxy is deliberately structural, not monetary.

## Decision rule

Default to **one agent / deterministic workflow**. Add a manager + specialists only when at least one measurable benefit exists:

1. independent subproblems can be isolated/parallelized;
2. context isolation prevents contamination or overload;
3. a central synthesizer must arbitrate conflicting specialist evidence;
4. specialist failure can be contained and rerouted without invalidating the whole run;
5. domain-specific tools/permissions materially require separation.

Prefer handoff/peer ownership when direct specialist interaction or persistent state ownership is itself a requirement; otherwise do not pay for a handoff chain merely to make the architecture “multi-agent.”

A topology should be rejected when its measured coordination overhead exceeds its reliability/latency/context-isolation gain on the target workload.

## Conclusion

Multi-agent is a conditional optimization, not a maturity level. In this controlled benchmark the manager topology buys failure containment and context isolation at roughly 3.3× the single-agent structural cost. Simple work should remain single-agent. Complex separable work can justify a manager when the saved failure risk is worth the extra coordination. Peer/handoff needs explicit state/evidence discipline and is not a substitute for central conflict resolution.
