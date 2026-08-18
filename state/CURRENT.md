# Current Lab State

Last updated: 2026-08-18

## Active objective

Continue the autonomous correctness agenda after proving memory contamination recovery. Next: formalize the human/agent escalation boundary so reversible technical uncertainty is handled autonomously while genuinely consequential or unauthorized choices escalate or block.

## Active issue / branch / PR

- Completed: #1 LAB-001 through #20 LAB-011 correctness sequence.
- Completed: #20 LAB-011 memory contamination, quarantine, and retraction recovery.
- Next: #22 LAB-012 human/agent escalation policy with uncertainty and reversibility gates — READY.

## Last completed step

LAB-011 compared OWASP ASI06 Memory & Context Poisoning, C2PA 2.4 trust/validation/revocation semantics, and NIST AI 600-1 data-poisoning/RAG risk controls. It built a deterministic memory-safety layer with ACTIVE, QUARANTINED, RETRACTED, and SUPERSEDED lifecycle states plus trust-first authoritative retrieval. The intentionally naive similarity-only policy selected a contaminated high-similarity fact; corrected retrieval excluded it. Initial local failure matrix passed 7/7 scenarios.

Remote patch audit found a real defect: the first supersession implementation let any newly added memory, including an untrusted one, mark trusted history SUPERSEDED. The implementation was corrected so supersession is an explicit operation and the replacement must satisfy the trust eligibility threshold. The corrected semantics were re-exercised locally. PR #21 was squash-merged.

## Evidence produced

- `experiments/memory_safety/memory_safety.py`
- `experiments/memory_safety/test_memory_safety.py`
- `experiments/memory_safety/README.md`
- `research/2026-08-18-memory-contamination-recovery.md`
- LAB-011 merge: `5d343a8db99217c1668af532b45a8ec493c79246`.
- Follow-up Issue #22 / LAB-012 created.

## Findings carried forward

- persistent memory is a security-relevant control surface, not merely retrieval context;
- trust/currentness/lifecycle eligibility must run before similarity ranking;
- quarantine preserves inspectability while preventing authoritative use;
- retraction and supersession preserve history rather than deleting it;
- provenance/integrity is not equivalent to truth, and a correction reference must be independently verifiable;
- an untrusted replacement must never be able to supersede trusted history merely by being newer or more similar;
- memory trust, evidence truth/provenance, and durable execution state remain separate contracts.

## Known blockers / constraints

- No current blocking issue is known.
- Local filesystem, CLIs, network, connectors and permissions remain per-run capabilities.
- The JSON prototype demonstrates semantics, not transactional production persistence or a truth oracle.

## Exact next action

Select Issue #22 / LAB-012. Research at least three current primary-source escalation/autonomy/risk-control mechanisms. Build `experiments/escalation_policy/` with explicit PROCEED / FALLBACK / PROBE / ESCALATE / BLOCK decisions. Seed both over-escalation and dangerous under-escalation cases, compose with LAB-005 side-effect state, LAB-006 evidence quality, and LAB-008 capability safety rather than duplicating them, run deterministic tests, audit residual human judgment boundaries, integrate safely, and update this state.

## Backlog

- #22 / LAB-012 — Human/agent escalation policy — READY and next.
- Agenda Track 6 / Failure Recovery and Side-Effect Fencing remains substantially satisfied by LAB-005; do not duplicate it without evidence of a new gap.
- Open-model serving and multi-agent topology remain lower priority until correctness instrumentation is stronger and suitable execution resources exist.
