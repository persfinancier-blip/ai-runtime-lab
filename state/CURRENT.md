# Current Lab State

Last updated: 2026-08-18

## Active objective

Continue the autonomous correctness agenda after completing the full software-engineering lifecycle composition experiment. Next: test persistent-memory contamination recovery so false/stale memories can be quarantined or retracted without destroying unrelated valid history.

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
- Completed: #18 LAB-010 autonomous software-engineering task loop.
- Next: #20 LAB-011 memory contamination, quarantine, and retraction recovery — READY.

## Last completed step

LAB-010 compared the SWE-bench evaluation harness, SWE-agent, and SWE-bench Verified/OpenAI Preparedness evaluation work, then built a thin deterministic lifecycle coordinator for `reproduce -> patch -> validate -> audit -> evidence-backed completion` while explicitly reusing the semantics established in LAB-005–009.

Initial local validation passed 9 tests, but the remote patch audit found a real lifecycle defect: after an audit-discovered regression the task returned to PATCHED while the regression remained an eternal unresolved blocker and repatching was impossible. The implementation was corrected by separating unresolved failures from durable failure history, allowing repatch from PATCHED, incrementing the artifact version, clearing reparable blockers, and adding a full `regression -> repatch -> revalidate -> reaudit -> accept` test. Corrected local validation passed 10/10 tests and compile checks. PR #19 was remotely re-audited and squash-merged.

## Evidence produced

- `experiments/software_engineering_loop/loop.py`
- `experiments/software_engineering_loop/tests/test_loop.py`
- `experiments/software_engineering_loop/README.md`
- `research/2026-08-18-autonomous-software-engineering-loop.md`
- `research/2026-08-18-lab010-audit.md`
- LAB-010 merge: `b48b169528e3e0e622a29db443f0e5128ced0fb6`.
- Follow-up Issue #20 / LAB-011 created.

## Findings carried forward

- a coding agent must not transition directly from PATCHED to DONE;
- minimum completion gates are observed reproduction, versioned patch, safe current-version validation, requirement coverage, separate audit, and evidence-backed completion decision;
- a passing headline validation result can still be a false success when requirements are only partially satisfied;
- stale evidence must be bound to artifact identity/version and rejected;
- safe capability fallback is compatible with correctness, but no-safe-route must BLOCK rather than fabricate success;
- full lifecycle modeling must distinguish historical failures from currently unresolved blockers so repaired work can progress without erasing audit history;
- real repository execution, flaky tests, environment drift, test adequacy, merge conflicts, security review, and model patch quality remain outside the deterministic simulator's evidence boundary.

## Known blockers / constraints

- No current blocking issue is known.
- Local filesystem, CLIs, network, connectors and permissions remain per-run capabilities.
- LAB-010 proves lifecycle gate semantics under controlled failure injection, not real-world coding-agent capability.

## Exact next action

Select Issue #20 / LAB-011. Research at least three current primary-source memory-safety/provenance mechanisms. Build `experiments/memory_safety/` as a deterministic layer over LAB-007 evidence identity/provenance and LAB-009 typed memory eligibility. Demonstrate a naive unsafe retrieval policy admitting a contaminated but highly relevant memory, then implement quarantine/retraction/supersession semantics that preserve unrelated valid history and survive serialization/reload. Run the required failure matrix, audit the trust/evidence/run-state boundaries, integrate safely, and update this state.

## Backlog

- #20 / LAB-011 — Memory contamination, quarantine, and retraction recovery — READY and next.
- Human/Agent Escalation Policy remains the next ranked unfulfilled correctness track after LAB-011 unless new evidence changes priority.
- Agenda Track 6 / Failure Recovery and Side-Effect Fencing remains substantially satisfied by LAB-005; do not create a duplicate implementation without new evidence of a gap.
- Open-model serving and multi-agent topology remain lower priority until correctness instrumentation is stronger and suitable execution resources exist.
