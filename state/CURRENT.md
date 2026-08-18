# Current Lab State

Last updated: 2026-08-18

## Active objective

Continue the autonomous correctness agenda after formalizing the human/agent escalation boundary. The next executable remaining agenda item is a controlled comparison of orchestration topologies under fixed evidence, recovery, memory, capability, and escalation rules.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-012 correctness sequence.
- Completed: #22 LAB-012 human/agent escalation policy.
- Next: #24 LAB-013 multi-agent orchestration topology benchmark — READY.
- Active branch/PR: none yet for LAB-013.

## Last completed step

LAB-012 compared current OpenAI agent-intervention guidance, NIST AI RMF human-oversight controls, EU AI Act Article 14, and the OpenAI Operator system-card reversibility/risk pattern. It built an explicit `PROCEED / FALLBACK / PROBE / ESCALATE / BLOCK` policy and seeded a deliberately naive confidence-first policy.

The initial deterministic suite passed 12/12 cases. Remote patch audit found a real authority-boundary defect: payment/legal/identity/secret gated actions with technical access could fall through unless another flag separately required human authorization. The policy was corrected so those categories always `ESCALATE` when authority is available and `BLOCK` when it is unavailable; the corrected suite passed 13/13 tests.

The normal PR #23 merge endpoint was externally blocked before execution. The final three-file patch was re-audited, all paths were confirmed absent in `main`, and the exact audited files were integrated through the approved GitHub Contents API fallback. PR #23 was closed as manually integrated and Issue #22 was closed DONE.

## Evidence produced

- `experiments/escalation_policy/policy.py`
- `experiments/escalation_policy/test_policy.py`
- `research/2026-08-18-human-agent-escalation-policy.md`
- main commits: `455f7d36189dc7ed22066c26f64ac0833d6366e2`, `f14a0ceeddae3a90123dffddfce6ae8acbbb1c65`, `0e6618d9ca8f30a855274fee3d3e58cd2e1cd586`.
- Follow-up Issue #24 / LAB-013 created.

## Findings carried forward

- confidence is not a safe autonomy boundary;
- hard authority/safety constraints precede confidence and preferences;
- ordinary reversible uncertainty should use safe `PROBE` or `FALLBACK` before human escalation;
- `ESCALATE` means a real human judgment/authorization boundary exists;
- `BLOCK` means no safe authorized path exists and must not trigger constraint weakening;
- payment/legal/identity/secret gates remain human-authority boundaries even when technical access exists;
- LAB-012 consumes LAB-005 side-effect state, LAB-006 evidence quality, and LAB-008 safe-route availability rather than duplicating them.

## Known blockers / constraints

- No current blocking issue is known.
- Local filesystem, CLIs, network, connectors and permissions remain per-run capabilities.
- Open-model serving remains resource-dependent and is deferred until a representative target runtime/hardware is available.
- Multi-agent topology must be measured under fixed evidence/recovery assumptions so coordination effects are not confused with model/tool quality.

## Exact next action

Select Issue #24 / LAB-013. Research at least three current primary-source orchestration/handoff mechanisms. Build `experiments/orchestration_topologies/` with identical deterministic seeded tasks across single-agent sequential, manager-specialist, and peer/handoff topologies. Measure correctness, coordination steps/messages, duplicated work, stale-context propagation, failure containment, and recovery. Demonstrate at least one case where multiple agents help and one where they hurt. Audit for confounding with model/tool/evidence behavior, integrate safely, and update this state.

## Backlog

- #24 / LAB-013 — multi-agent orchestration topology benchmark — READY and next.
- Open-model serving efficiency remains deferred pending suitable representative execution resources.
- Revisit the agenda after LAB-013 to identify newly exposed correctness/performance gaps before adding broader autonomous features.
