# Current Lab State

Last updated: 2026-08-18

## Active objective

Continue the autonomous research agenda after completing deterministic end-to-end completion verification. Next: make verification evidence durable, append-only and independently resolvable.

## Active issue / branch / PR

- Completed: #1 LAB-001 bootstrap durable loop.
- Completed: #2 LAB-002 execution-surface baseline.
- Completed: #3 LAB-003 cross-run resumability.
- Completed: #4 LAB-004 autonomous research agenda.
- Completed: #8 LAB-005 durable run-state protocol.
- Completed: #11 LAB-006 end-to-end verification harness.
- Next: #12 LAB-007 append-only evidence ledger and claim-to-observation protocol — READY.
- LAB-006 branch `lab/006-verification-harness` remains as an audit trail; its four additive files were integrated to `main` through the safe fallback path after PR creation was blocked before execution.

## Last completed step

LAB-006 researched SWE-bench, SLSA provenance/verification and in-toto attestation mechanisms, then built a standard-library deterministic verifier. Local execution observed 7/7 seeded trajectory tests passing plus Python compile validation. The harness accepts a correct current trajectory and rejects an unexecuted test, observed failing test, stale artifact-bound evidence, incomplete requirement coverage, fabricated evidence reference, and evidence invalidated by artifact mutation.

PR creation was blocked before execution by an external safety-status gate. Branch-vs-main audit showed exactly four additive files, 268 additions, no deletions, and zero commits behind. Per the repository safe-fallback policy, the exact audited files were integrated through normal GitHub Contents API. Issue #11 is DONE.

## Evidence produced

- `experiments/verification_harness/protocol.py`
- `experiments/verification_harness/tests/test_protocol.py`
- `experiments/verification_harness/README.md`
- `research/2026-08-18-agent-verification-harness.md`
- Final LAB-006 integration commit: `8ff38e63fb82ff85c69f19d2f9e27fe450fa1678`.
- Follow-up Issue #12 / LAB-007 created.

## Findings carried forward

- terminal success is a verifier decision over observations, not executor narrative;
- evidence must be bound to the exact artifact/version it evaluated;
- planned/self-reported execution is not equivalent to an observed result;
- requirement coverage and green tests are separate gates;
- dangling evidence references fail closed;
- mutation invalidates prior evidence by default;
- LAB-005 run state and LAB-006 evidence are distinct: run state may reference evidence/verdict IDs but should not turn mutable worker prose into proof.

## Known blockers / constraints

- No current blocking issue is known.
- The LAB-006 PR creation endpoint was unavailable in this run; the documented supported fallback succeeded.
- Local filesystem, CLIs, network, connectors and permissions remain per-run capabilities.

## Exact next action

Select Issue #12 / LAB-007. Research at least three primary mechanisms covering attestation/provenance, append-only/event logs and content-addressed evidence. Build `experiments/evidence_ledger/` with a versioned canonical evidence record, append-only persistence/reload, deterministic identity, tamper detection, duplicate/idempotency behavior, invalidation/supersession records, stale-artifact rejection and integration with the LAB-006 verifier concepts. Run failure-injection tests, audit the result, integrate safely, then update this state.

## Backlog

- #12 / LAB-007 — Evidence Ledger / Claim-to-Observation Protocol — READY and next.
- Agenda rank 4 — Capability Negotiation and Fallback Planning — follows LAB-007 unless evidence changes priority.
- Remaining ranked tracks stay in `research/AGENDA.md` until dependencies/capacity justify issue creation.
