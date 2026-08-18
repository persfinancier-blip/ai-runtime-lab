# Current Lab State

Last updated: 2026-08-18

## Active objective

Continue the autonomous agenda after completing the long-horizon memory benchmark. Next: compose the already-proven durability, verification, evidence, capability-fallback, and memory primitives into a full autonomous software-engineering lifecycle and measure its failure taxonomy.

## Active issue / branch / PR

- Completed: #1 LAB-001 bootstrap durable loop.
- Completed: #2 LAB-002 execution-surface baseline.
- Completed: #3 LAB-003 cross-run resumability.
- Completed: #4 LAB-004 autonomous research agenda.
- Completed: #8 LAB-005 durable run-state protocol.
- Completed: #11 LAB-006 end-to-end verification harness.
- Completed: #12 LAB-007 append-only evidence ledger.
- Completed: #14 LAB-008 capability negotiation and fallback planning.
- Completed: #16 LAB-009 long-horizon memory with causality/provenance benchmark.
- Next: #18 LAB-010 autonomous software-engineering task loop — READY.

## Last completed step

LAB-009 compared AMA-Bench/AMA-Agent, Supersede, Graphiti, and Causal Memory Intervention, then built a deterministic synthetic benchmark comparing recency, similarity proxy, typed temporal/provenance graph, and bounded hybrid retrieval on identical stale/superseded, distractor, causal-chain, objective-change, provenance-conflict, and long-horizon-noise cases.

The first remote patch audit found that topical relevance was only implicit, so the benchmark was strengthened before merge with an explicit lexical surface-relevance metric and two additional metric-separation tests. Observed local validation was 9 tests total. PR #17 was remotely audited and squash-merged.

## Evidence produced

- `experiments/long_horizon_memory/benchmark.py`
- `experiments/long_horizon_memory/metrics.py`
- `experiments/long_horizon_memory/tests/`
- `research/2026-08-18-long-horizon-memory-causality-provenance.md`
- `research/2026-08-18-long-horizon-memory-metric-separation.md`
- LAB-009 merge: `7fcd7f03d75951cf569a2e6149208df64d9b924a`.
- Follow-up Issue #18 / LAB-010 created.

## Findings carried forward

- topical/surface relevance is not the same as current/causal correctness;
- recency can lose authoritative facts after a long distractor tail;
- similarity can recover the correct fact while simultaneously contaminating context with stale/superseded facts;
- typed supersession/invalidation/currentness and causal links should act as eligibility structure before semantic/keyword ranking;
- bounded hybrid retrieval is the preferred direction from this small benchmark;
- memory must reference, not replace, LAB-005 authoritative run state and LAB-007 provenance/evidence;
- LAB-005 already substantially covers the agenda's separate Failure Recovery / Side-Effect Fencing track, so starting a duplicate subsystem would violate the no-duplication rule.

## Known blockers / constraints

- No current blocking issue is known.
- Local filesystem, CLIs, network, connectors and permissions remain per-run capabilities.
- LAB-009 is a deterministic synthetic benchmark; production memory extraction/ranking remains outside its evidence boundary.

## Exact next action

Select Issue #18 / LAB-010. Research at least three current primary-source full-cycle software-agent/engineering harnesses or benchmarks. Build `experiments/software_engineering_loop/` as a deterministic lifecycle simulator that reuses the semantics established in LAB-005–009 rather than reimplementing new subsystems. Cover successful reproduce->patch->test->audit->evidence completion plus unreproduced patch, partial fix, stale test evidence, audit-discovered regression, safe capability fallback, and no-safe-validation-route cases. Measure a stable failure taxonomy, reject superficially plausible false success, audit the composition boundaries, integrate safely, and update this state.

## Backlog

- #18 / LAB-010 — Autonomous software-engineering task loop with measured failure taxonomy — READY and next.
- Agenda Track 6 / Failure Recovery and Side-Effect Fencing is treated as substantially satisfied by LAB-005 unless new evidence exposes an uncovered gap; do not create a duplicate implementation merely to follow numeric rank.
- Memory Safety / Contamination Recovery and Human/Agent Escalation remain later ranked tracks.
- Open-model serving and multi-agent topology remain lower priority until correctness instrumentation is stronger and suitable execution resources exist.
