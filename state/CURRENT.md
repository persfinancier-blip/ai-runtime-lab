# Current Lab State

Last updated: 2026-08-18

## Active objective

Continue the autonomous agenda after making completion evidence durable and independently resolvable. Next: formalize per-run capability negotiation and safe fallback planning.

## Active issue / branch / PR

- Completed: #1 LAB-001 bootstrap durable loop.
- Completed: #2 LAB-002 execution-surface baseline.
- Completed: #3 LAB-003 cross-run resumability.
- Completed: #4 LAB-004 autonomous research agenda.
- Completed: #8 LAB-005 durable run-state protocol.
- Completed: #11 LAB-006 end-to-end verification harness.
- Completed: #12 LAB-007 append-only evidence ledger.
- Next: #14 LAB-008 capability negotiation and fallback planning — READY.

## Last completed step

LAB-007 compared in-toto attestation semantics, Apache Kafka append-log mechanics, and Git content addressing, then built a standard-library evidence ledger. Local deterministic validation observed 9/9 tests passing: restart/reload, duplicate/idempotency, tamper, stale artifact, dangling reference, invalidation, supersession, untrusted worker assertion, and valid current evidence. PR #13 was patch-audited and squash-merged.

## Evidence produced

- `experiments/evidence_ledger/protocol.py`
- `experiments/evidence_ledger/tests/test_protocol.py`
- `experiments/evidence_ledger/README.md`
- `research/2026-08-18-append-only-evidence-ledger.md`
- LAB-007 merge: `5cc55d55fdabd33769cefa5dd90882c42d11a4a3`.
- Follow-up Issue #14 / LAB-008 created.

## Findings carried forward

- content identity and ledger position are distinct: canonical SHA-256 IDs support semantic identity/idempotency while sequence/previous links preserve ordered history;
- evidence is immutable; invalidation and supersession append later records;
- artifact digest is part of the observation freshness boundary;
- a content hash proves byte identity/integrity, not truth; executor assertions are not independent observations;
- hash chaining is only tamper-evident relative to a trusted external head/checkpoint;
- LAB-005 terminal run state should reference accepted verifier/evidence IDs rather than mutable worker prose.

## Known blockers / constraints

- No current blocking issue is known.
- Local filesystem, CLIs, network, connectors and permissions remain per-run capabilities.

## Exact next action

Select Issue #14 / LAB-008. Research at least three primary capability-negotiation/fallback mechanisms. Build `experiments/capability_planner/` with versioned capability observations and requirements, hard constraints vs preferences, freshness/probe semantics, deterministic ranking and explanation evidence. Test preferred-path success, safe fallback, stale observation, unsafe/weakened fallback rejection, deterministic tie-breaking and no-viable-path. Audit and integrate safely, then update this state.

## Backlog

- #14 / LAB-008 — Capability Negotiation and Fallback Planning — READY and next.
- Remaining ranked tracks stay in `research/AGENDA.md` until dependencies/capacity justify issue creation.
