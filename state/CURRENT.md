# Current Lab State

Last updated: 2026-08-18

## Active objective

Continue the autonomous agenda after formalizing per-run capability negotiation and safe fallback planning. Next: test long-horizon memory representations for causal/current correctness under noise, stale facts, and supersession.

## Active issue / branch / PR

- Completed: #1 LAB-001 bootstrap durable loop.
- Completed: #2 LAB-002 execution-surface baseline.
- Completed: #3 LAB-003 cross-run resumability.
- Completed: #4 LAB-004 autonomous research agenda.
- Completed: #8 LAB-005 durable run-state protocol.
- Completed: #11 LAB-006 end-to-end verification harness.
- Completed: #12 LAB-007 append-only evidence ledger.
- Completed: #14 LAB-008 capability negotiation and fallback planning.
- Next: #16 LAB-009 long-horizon memory with causality and provenance benchmark — READY.

## Last completed step

LAB-008 compared MCP capability negotiation/version handshake, Terraform plugin protocol compatibility selection, and Kubernetes discovery/resourceVersion freshness semantics. It then built a standard-library deterministic capability planner with versioned observations/requirements, hard constraints, weighted preferences, freshness rejection, evidence references, and stable decision explanations. Local deterministic validation observed 7/7 tests passing and compileall passing. PR #15 was remotely patch-audited and squash-merged.

## Evidence produced

- `experiments/capability_planner/planner.py`
- `experiments/capability_planner/tests/test_planner.py`
- `experiments/capability_planner/README.md`
- `research/2026-08-18-capability-negotiation-fallback-planning.md`
- LAB-008 merge: `b32f3911a387dae5f0db12a5de9c91554daaa468`.
- Follow-up Issue #16 / LAB-009 created.

## Findings carried forward

- capability availability is a per-run observation with freshness, not a permanent tool property;
- protocol/schema compatibility and freshness are eligibility gates;
- hard safety/correctness requirements are checked before scoring preferences;
- fallback equivalence is defined by required observable properties, not implementation similarity;
- `no viable path` is a correct plan result and must not trigger unsafe downgrade;
- planner decisions should reference durable observation/evidence IDs while remaining distinct from run state and the evidence ledger.

## Known blockers / constraints

- No current blocking issue is known.
- Local filesystem, CLIs, network, connectors and permissions remain per-run capabilities.

## Exact next action

Select Issue #16 / LAB-009. Research at least three current primary-source memory mechanisms/benchmarks. Build `experiments/long_horizon_memory/` with a deterministic synthetic corpus and compare transcript/recency, similarity proxy, typed event/provenance graph, and bounded hybrid retrieval on identical distractor, stale/superseded, causal-chain, objective-change, and provenance-conflict cases. Measure current/causal correctness separately from superficial relevance. Seed at least one naive-strategy failure, audit integration boundaries with LAB-005 run state and LAB-007 evidence, integrate safely, and update this state.

## Backlog

- #16 / LAB-009 — Long-horizon memory with causality and provenance benchmark — READY and next.
- Failure Recovery and Side-Effect Fencing remains a later ranked agenda track unless LAB-009 exposes a higher-priority dependency.
- Remaining tracks stay in `research/AGENDA.md` until dependencies/capacity justify issue creation.
