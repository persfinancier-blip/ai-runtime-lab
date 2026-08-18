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

Transferable distinction: **agents as tools** keeps a manager in control and is preferred when one agent should own synthesis or shared guardrails; **handoffs** transfer active ownership to a specialist. The SDK also supports code-driven orchestration, which is useful when deterministic routing is more important than letting an LLM choose every transition.

### LangChain / LangGraph multi-agent patterns

Sources:
- https://docs.langchain.com/oss/python/langchain/multi-agent/index
- https://docs.langchain.com/oss/python/langchain/multi-agent/subagents
- https://docs.langchain.com/oss/python/langchain/multi-agent/handoffs

Transferable mechanisms: supervisor/subagent architecture centralizes routing and provides context isolation; handoffs use state-driven ownership and require explicit context engineering. Current docs explicitly state that multi-agent is not always needed and show higher model-call/context costs for some multi-agent patterns. Subagents trade extra orchestration for isolated contexts; handoffs can reduce repeated routing in stateful conversational flows but are inefficient for some multi-domain parallel work.

### Microsoft AutoGen AgentChat

Sources:
- https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/teams.html
- https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/swarm.html
- https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/graph-flow.html

Transferable mechanisms: AutoGen exposes materially different team shapes rather than one universal topology. Its documentation recommends starting with a single agent for simpler tasks and moving to teams when collaboration/diverse expertise are actually required. `Swarm` uses handoff messages with shared context; `GraphFlow` provides deterministic graph control when execution order and branching need stronger constraints.

## Benchmark design

Implementation: `experiments/orchestration_topologies/`.

Three topologies execute the same seven seeded scenarios:

1. simple task where decomposition adds no information;
2. three independent outputs under a shared context budget of two evidence items;
3. stale then current evidence;
4. duplicate delivery of the same logical work item;
5. conflicting current evidence followed by authoritative evidence;
6. one worker failure followed by deterministic retry;
7. another simple case where coordination overhead dominates.

Every topology receives identical events and uses identical work IDs, duplicate suppression, evidence versioning, authoritative conflict handling, retry semantics, and terminal verification. No LLM or external model is called.

The manipulated variable is only routing/context ownership:

- `single`: one bounded sequential evidence context;
- `manager`: isolated specialist evidence returned to a central synthesizer;
- `peer`: a bounded context forwarded through handoffs.

## Audit correction

The first implementation encoded several correctness outcomes directly with topology-specific conditionals. That was a real validity defect: it could only restate the intended conclusion.

The benchmark was rewritten before integration. In the corrected version, stale evidence, conflict resolution, duplicate suppression, worker failure and retry are common mechanisms. Topology differences can affect which evidence survives shared context pressure and how much structural coordination is paid, but cannot directly assign success/failure for those cases.

A test explicitly asserts that stale-evidence, conflict, and worker-failure scenarios are correct under all three topologies.

## Observed local validation

Commands executed after the correction:

```bash
python -m unittest discover -s experiments/orchestration_topologies/tests -v
python -m compileall -q experiments
python experiments/orchestration_topologies/benchmark.py
```

Observed result: **9/9 tests passed**; compileall passed.

Corrected aggregate benchmark:

| topology | correctness | mean structural cost | messages | work calls | duplicate deliveries | stale-context events | recoveries |
|---|---:|---:|---:|---:|---:|---:|---:|
| single | 85.71% | 2.86 | 0 | 13 | 1 | 1 | 1 |
| manager | 100% | 8.43 | 26 | 13 | 1 | 0 | 1 |
| peer | 85.71% | 6.57 | 13 | 13 | 1 | 1 | 1 |

These percentages are properties of this synthetic task set, not population estimates.

## Help case

The only correctness advantage intentionally left in the corrected benchmark comes from **context isolation**. The decomposable scenario has three independent required outputs and a shared context budget of two. Single and peer shared contexts evict one required result; manager specialists return isolated outputs to synthesis and preserve all three.

This demonstrates a defensible condition for extra agent boundaries: separable work can benefit when isolation prevents one subtask's working context from displacing another's required evidence.

## Hurt case

On a simple one-result task, every topology is correct. Manager and peer still pay dispatch/handoff/synthesis steps that add no information. This demonstrates multi-agent harm without manufacturing a correctness failure: coordination overhead can dominate when one bounded context can already solve the task.

## Stale evidence, conflict, duplicate delivery and worker failure

These cases deliberately **do not** prove manager superiority:

- stale evidence is rejected/contained by the shared version rule;
- duplicate delivery is collapsed by the same logical work ID;
- authoritative evidence resolves conflict for every topology;
- one worker failure is recovered by the same retry rule for every topology.

Manager may keep stale evidence out of synthesis earlier because of its isolation boundary, but terminal correctness remains shared. This separation is important: evidence quality and durable retry are prerequisites from LAB-005 through LAB-012, not topology benefits to count twice.

## Audit: confounds and limits

Controlled:
- deterministic worker fixtures;
- identical logical work/evidence identities;
- identical idempotency and retry rules;
- identical terminal verifier;
- identical seeded scenarios;
- no model/tool variance.

Not proven:
- real token, latency, or monetary cost ratios;
- model-quality gains from specialist prompts/models;
- real parallel speedups;
- behavior on open-ended research or user-facing conversations;
- global superiority of OpenAI, LangChain/LangGraph, AutoGen, or any topology.

The structural cost proxy is `messages + coordination_steps + work_calls`; it is not a production cost model.

## Decision rule

Default to **one agent or deterministic workflow**. Add a manager + specialists only when a measured requirement buys something concrete, such as:

1. independent subproblems need isolated context or parallel execution;
2. context isolation prevents contamination or capacity pressure;
3. central synthesis must arbitrate multiple specialist outputs;
4. failure containment or distinct tool/permission boundaries materially reduce risk;
5. team boundaries reflect real domain ownership that cannot be expressed cleanly as tools/skills.

Prefer handoff/peer ownership when direct specialist interaction or persistent conversational state ownership is itself required. Do not add a handoff chain merely to make an architecture look multi-agent.

Reject a topology when its measured reliability, latency, parallelism, context-isolation, or permission-boundary benefit does not exceed its extra coordination cost on the target workload.

## Conclusion

Multi-agent orchestration is a conditional optimization, not a maturity level. In this controlled benchmark, manager isolation fixes one context-pressure case but costs roughly 2.95x the single-agent structural proxy. Peer/handoff pays substantial coordination cost without improving the bounded engineering-style task set unless direct ownership/state flow is itself the requirement. The safest default is therefore single-agent/deterministic orchestration, escalating to multiple agents only for measurable isolation, parallelism, synthesis, failure-containment, or authority benefits.
