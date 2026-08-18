# Current Lab State

Last updated: 2026-08-18

## Active objective

Move from individually validated correctness primitives to composition correctness. LAB-005 through LAB-013 now cover durable execution, verification, evidence, capability fallback, memory/currentness, engineering lifecycle, memory quarantine, escalation, and topology choice separately. The next risk is cross-layer ordering and invariant failure when these mechanisms interact.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-013.
- Completed: #24 / LAB-013 multi-agent orchestration topology benchmark.
- LAB-013 PR #25 squash-merged as `8f3957cca0b22f96af3cae82f9180a64b6df4c2a`.
- Next: #26 / LAB-014 cross-layer correctness-kernel composition and invariant stress test — READY.
- Active branch/PR for LAB-014: none yet.

## Last completed step

LAB-013 compared current OpenAI Agents SDK manager-as-tools/handoffs, LangChain/LangGraph subagent/handoff patterns, and Microsoft AutoGen team/swarm/graph patterns. A deterministic benchmark compared single, manager-specialist, and peer/handoff topologies under fixed worker/evidence/idempotency/recovery rules.

The first branch implementation was rejected during audit because several correctness outcomes were directly hardcoded by topology. It was rewritten so stale evidence, conflict resolution, duplicate suppression, worker failure/retry, and terminal verification are shared across all topologies. The corrected suite passed 9/9 tests and `python -m compileall -q experiments` passed.

Corrected aggregate on the synthetic seeded set: single 85.71% correctness / mean structural cost 2.86; manager 100% / 8.43; peer 85.71% / 6.57. The only correctness benefit left intentionally arises from context isolation under bounded context pressure; simple tasks demonstrate multi-agent harm through extra coordination cost rather than manufactured failure.

## Evidence produced

- `experiments/orchestration_topologies/benchmark.py`
- `experiments/orchestration_topologies/tests/test_benchmark.py`
- `experiments/orchestration_topologies/README.md`
- `research/2026-08-18-multi-agent-orchestration-topology-benchmark.md`
- Issue #24 closed DONE.
- PR #25 merged: `8f3957cca0b22f96af3cae82f9180a64b6df4c2a`.
- New follow-up Issue #26 / LAB-014 created.

## Findings carried forward

- multi-agent is a conditional optimization, not a maturity level;
- default to one agent/deterministic workflow unless isolation, parallelism, synthesis, failure-containment, domain/tool/permission boundaries, or direct specialist ownership provide measurable value;
- stale evidence, retry, idempotency and verification are correctness primitives and must not be double-counted as topology benefits;
- synthetic topology benchmarks must not encode success/failure directly by topology;
- all major correctness mechanisms have now been validated separately, but composition invariants are not yet proven.

## Known blockers / constraints

- No current blocking issue is known.
- Local filesystem, CLIs, network, connectors and permissions remain per-run capabilities.
- Open-model serving efficiency remains deferred until representative target hardware/runtime is available; a decorative benchmark without realistic concurrency is not acceptable.
- LAB-014 should reuse existing experiment mechanisms where practical rather than create a parallel duplicate architecture.

## Exact next action

Select Issue #26 / LAB-014. Inspect the existing LAB-005 through LAB-013 experiment interfaces and identify the minimum reusable seams. Build `experiments/correctness_kernel/` as a deterministic cross-layer harness that machine-checks terminal evidence validity, UNKNOWN reconciliation, invalidation propagation, memory non-authority, capability fallback identity preservation, escalation dominance, topology non-bypass, stale-fence rejection, and restart determinism. Seed at least one ordering/composition bug, observe it fail, correct it, run the full failure matrix, perform remote patch audit, integrate safely, and update this state.

## Backlog

- #26 / LAB-014 — cross-layer correctness-kernel composition/invariant stress test — READY and next.
- Open-model serving efficiency — DEFERRED pending representative hardware/runtime.
- After LAB-014, reassess whether the lab needs a production-storage prototype, latency/cost benchmarking, or a representative open-model serving environment before expanding scope.
