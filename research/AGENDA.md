# Autonomous Research Agenda

Date: 2026-08-18
Owner: executing AI Runtime Lab agent
Status: ACTIVE

## Purpose

This agenda ranks research tracks that can produce reusable mechanisms, experiments, and implementation evidence for long-running autonomous agents. It is intentionally independent of any single product architecture.

## Prioritization model

Each track is scored 1–5 on:

- **Leverage** — how many later capabilities it unlocks.
- **Uncertainty** — how much material engineering uncertainty remains.
- **Testability** — whether the lab can build a falsifiable experiment with current tools.
- **Reusability** — whether the output can become a protocol, library, benchmark, or design rule.
- **Immediacy** — whether current evidence shows this is a near-term bottleneck.

Priority score = `Leverage + Uncertainty + Testability + Reusability + Immediacy` (max 25).

A high score does not justify endless browsing. Every executable research issue must define a stop condition and a reusable output.

## Current evidence shaping the agenda

The lab's own LAB-002/LAB-003 experiments established two immediate facts:

1. runtime capabilities vary per invocation and local filesystem state is not reliable durable memory;
2. repository-backed explicit checkpoints can restore autonomous work across invocations.

Current external evidence strengthens the case for studying durable state and verification before more elaborate multi-agent orchestration:

- OpenAI Agents SDK documents serializable `RunState` for pause/resume and integrations with durable orchestrators for long-running workflows: https://openai.github.io/openai-agents-python/human_in_the_loop/ and https://openai.github.io/openai-agents-python/running_agents/
- LangGraph persistence checkpoints state at execution boundaries, supports pending-write recovery, interrupts, replay, and forks: https://docs.langchain.com/oss/python/langgraph/persistence and https://docs.langchain.com/oss/python/langgraph/interrupts
- SWE-Cycle (2026) reports a sharp drop when code agents must handle the full environment→implementation→verification cycle rather than isolated subtasks: https://arxiv.org/abs/2605.13139
- SWE-Bench Pro (2025) reports low performance on long-horizon enterprise-grade tasks, suggesting orchestration alone does not solve end-to-end reliability: https://arxiv.org/abs/2509.16941
- AMA-Bench (2026) finds long-horizon agent memory suffers when retrieval loses causal/objective information: https://arxiv.org/abs/2602.22769
- MemEvoBench (2026) shows persistent memory can accumulate misleading information and degrade agent behavior: https://arxiv.org/abs/2604.15774

## Ranked backlog

| Rank | Track | Score | Why now | Reusable output | Stop condition |
|---|---|---:|---|---|---|
| 1 | Durable Run-State Protocol | 25 | LAB-003 proved repository checkpoints work, but the minimal state contract, side-effect semantics, replay rules, versioning, and idempotency boundary are not yet formalized. | Reference state schema + checkpoint/resume prototype + failure-injection tests. | Stop after at least 3 donor mechanisms are compared and a local prototype passes crash/resume, duplicate-delivery, stale-version, and partial-side-effect tests. |
| 2 | End-to-End Agent Verification Harness | 24 | Recent software-agent benchmarks show large reliability loss across the complete execution cycle; our lab needs evidence stronger than self-reported success. | Small execution-capable verifier harness with claim/evidence schema and mutation tests. | Stop when the harness can distinguish at least 5 intentionally correct/incorrect trajectories and catches seeded false-success claims. |
| 3 | Evidence Ledger / Claim-to-Observation Protocol | 23 | The lab already depends on the rule “do not claim it unless observed”; this should become machine-checkable rather than prose-only. | Append-only evidence record format + validator + examples. | Stop when every completion claim in a sample run can be traced to an observation/artifact or rejected deterministically. |
| 4 | Capability Negotiation and Fallback Planning | 22 | LAB-002 showed tools/CLIs/network access are per-run capabilities. Autonomous agents need explicit route selection instead of brittle assumptions. | Capability manifest/probe format + fallback planner + simulated degradation matrix. | Stop after injected loss of at least 4 capabilities still produces correct route/blocker behavior without fabricated execution. |
| 5 | Long-Horizon Memory with Causality and Provenance | 21 | 2026 memory research indicates similarity retrieval alone can lose causal facts and memory can mis-evolve under noisy inputs. | Typed memory experiment comparing transcript, vector-like retrieval, event/provenance graph, and bounded-context retrieval. | Stop after a reproducible synthetic benchmark shows which memory representation preserves causal/task facts under noise and long horizons. |
| 6 | Failure Recovery and Side-Effect Fencing | 21 | Durable resume is unsafe if external side effects can be repeated after retries or replay. | Idempotency/fencing patterns catalog + executable fault-injection scenarios. | Stop after duplicate, timeout-after-success, stale-worker, retry, and partial-commit cases have deterministic expected behavior. |
| 7 | Autonomous Software-Engineering Task Loop | 20 | Full-cycle coding agents fail more often than isolated coding benchmarks imply. | Repository-native task lifecycle experiment: reproduce→patch→test→audit→evidence. | Stop after a small set of real or synthesized repo tasks can be run end-to-end with measured failure taxonomy. |
| 8 | Memory Safety / Contamination Recovery | 19 | Persistent state creates an attack and drift surface independent of prompt injection in the current turn. | Memory provenance rules + quarantine/retraction experiment. | Stop after seeded false memories can be detected/retracted without deleting unrelated valid history. |
| 9 | Human/Agent Escalation Policy | 18 | Human-in-the-loop is useful only if escalation is sparse, precise, resumable, and version-safe. | Risk-tier approval protocol + stale-approval test matrix. | Stop after reversible vs irreversible actions, expired approvals, changed inputs, and rejected actions are handled correctly. |
| 10 | Open-Model Serving Efficiency | 16 | Potentially valuable, but runtime correctness and evaluation are more immediate bottlenecks for this lab. | Reproducible serving benchmark plan covering KV/prefix cache, batching, quantization, speculative decoding, and cost/request. | Stop after one representative open model is benchmarked under realistic concurrency on an available target environment; defer if no suitable hardware/runtime is available. |
| 11 | Multi-Agent Orchestration Topologies | 15 | Manager/handoff/peer patterns are widely available, but adding agents before state/evidence/recovery are strong risks multiplying failure modes. | Controlled comparison of single-agent vs manager/handoff patterns on fixed tasks. | Start only after Tracks 1–3 produce stable instrumentation; stop when topology effect can be separated from model/tool effects. |

## Autonomous sequencing rule

Default sequence is not simply rank order. The lab should choose the highest-ranked track whose dependencies are satisfied and whose experiment can be executed with current capabilities.

Current sequence:

`Durable Run-State Protocol -> End-to-End Verification Harness -> Evidence Ledger -> Capability Negotiation -> Memory/Recovery tracks -> higher-level orchestration`

The agenda must be revised when an experiment falsifies an assumption, exposes a higher-risk blocker, or makes a lower-ranked track newly executable.

## First executable research item

Create an issue for **Durable Run-State Protocol** with a concrete donor comparison and a minimal implementation experiment. Its first deliverable must not be a literature review: it must end in executable state-transition and failure-injection tests.
