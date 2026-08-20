# Current Lab State

Last updated: 2026-08-20

## Active objective

LAB-059 — prove durable transition-evidence/history integrity across restart after LAB-058 established local atomic serialization of root/recovery authority changes.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-058.
- Next: Issue #109 / LAB-059 — READY.
- LAB-058 implementation branch `lab/058-authority-transition-races` remains as source evidence; exact audited files were integrated to `main` via Contents API fallback.
- Active PR: none.

## Last completed step

LAB-058 built a SQLite transactional/CAS reference model binding the exact predecessor `(root_id, recovery_authority_id, sequence)` at the commit boundary. Recovery-authority rotation and break-glass root recovery can both be individually cryptographically valid from one predecessor pair, but only one may become locally authoritative. The unsafe check-then-write seed accepted two incompatible successors; the corrected store serialized them.

Corrected deterministic suite passed 11/11. A separate concurrency audit repeated the three race classes 20 times each (60 race tests total) with no double winner. Unsafe seed failed as expected. Compileall passed. Remote protocol/test blob SHAs matched locally executed sources. Branch compare was ahead 6 / behind 0 with six new conflict-free files, so exact audited bytes were integrated through the normal Contents API fallback. Issue #108 was closed DONE.

## Evidence produced

- `experiments/authority_transition_races/protocol.py`
- `experiments/authority_transition_races/tests/test_protocol.py`
- `experiments/authority_transition_races/tests/unsafe_race_expected_failure.py`
- `experiments/authority_transition_races/README.md`
- `research/2026-08-20-authority-transition-races.md`
- Corrected suite: 11/11 passed.
- Repeated concurrency audit: 60/60 passed.
- Unsafe seed: failed as expected because two conflicts were accepted.
- Compileall: passed.
- Branch protocol blob SHA `ee5aacc787a6ac023d10540dea742243f7ac103e`; corrected-test blob SHA `500c099166495dedaced84b47472318928fcf033`; both matched locally executed sources before integration.
- Follow-up Issue #109 / LAB-059 created.

## Known blockers / constraints

- No active blocker.
- Local serialization in one SQL store is not distributed consensus and cannot prevent forks across independently writable replicas.
- Internal SQL history verification cannot by itself detect rollback of the entire database snapshot; LAB-034–037 external-anchor work remains the boundary for that class.
- Local shell DNS to GitHub remains unavailable/unreliable; GitHub connector plus local execution is supported.

## Exact next action

Start Issue #109 / LAB-059. Extend the LAB-058 transition record so exact threshold proof material is durable, then build restart verification that reconstructs bootstrap→head and re-verifies each historical transition against its historical predecessor authorities. Inject tampered predecessor/successor IDs, signer/signature corruption, missing/gapped transition rows, head/history mismatch, and unsafe evidence-trusting reconciliation. Keep database rollback resistance explicitly delegated to the existing external-anchor layer rather than duplicating LAB-034–037.

## Backlog

- #109 / LAB-059 — transition-evidence integrity and restart history conformance — READY.
- Reliable gossip transport, Byzantine consensus, and fork prevention remain out of scope unless evidence makes them the next correctness bottleneck.
- Crash-resilient scavenging for named credential-file fallback — candidate follow-up.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
