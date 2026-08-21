# Current Lab State

Last updated: 2026-08-21

## Active objective

LAB-072 — finish proof that concurrent broker workers serialize one mediated effect behind LAB-071 kernel sender authority, with one durable credential-generation authority and rotation-safe retry semantics.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-071.
- Active Issue #135 / LAB-072 — IN_PROGRESS.
- Active branch: `lab/072-transactional-broker-journal`.
- Draft PR #136 `[LAB-072] Transactional broker request journal`.
- Current PR HEAD: `82332de6fbf43909a7400662a740e5326033fd70`; GitHub reports mergeable, still draft intentionally.

## Last completed step

LAB-072's first exact-source journal slice had already passed 13/13 tests, an unsafe duplicate-effect seed, compileall, and 20 repeated reservation-vs-rotation races.

This run integrated the journal behind LAB-071's real process-instance authority boundary. `KernelAuthorizedBrokerWorker` validates `SCM_CREDENTIALS`-derived sender identity with LAB-071 PID/starttime/fresh-pidfd logic before any new durable reservation or sink effect.

A separate audit found a new cross-layer design defect: treating LAB-071 durable JSON generation and LAB-072 SQL generation as two authorities would require a cross-store rotation transaction and could split after crash. The fix makes LAB-072 SQL the single durable credential-generation authority. LAB-071 is reused only for sender identity. `bind_sender_to_journal_generation()` binds the current SQL generation to the exact process instance.

Published process-level regressions now cover two broker worker processes contending on one journal/sink, same-ID substitution, failed sender authority with no reservation, exact committed retry after rotation, new-operation permit rebinding after rotation, and substitution-after-rotation.

## Evidence produced

- First-slice exact protocol blob: `6066d90b3032eeefc0f2dbbd272c09a9a716b5b2`.
- First-slice exact corrected-test blob: `656284062a96b7915e3283b181c58bd7a8e9281d`.
- First-slice exact suite: 13/13 passed; unsafe seed failed as expected; compileall passed.
- 20 reservation-vs-rotation races: only safe serial outcomes observed.
- Current `authorized.py` blob: `cb2b664eef11cd5036fd529ddd31c0fb90d73d74`.
- Current process-integration test blob: `074e3feafca3c1857901448c7ffeb0a834a2bf29`.
- Interface-compatible local Linux smoke reconstruction: real process identical-request, substitution, and new-generation-permit scenarios passed. This is supporting evidence only, not exact-source validation of current PR HEAD.
- Research note updated with the single-generation-authority decision and process-level integration model.

## Known blockers / constraints

- No owner-level blocker.
- PR #136 remains draft because current integration HEAD has not yet been executed from exact published bytes.
- Direct `git clone`/checkout failed in this runtime because `github.com` DNS resolution is unavailable.
- The GitHub connector is available for exact source reconstruction, but the current run did not complete full local reconstruction of all LAB-072 + LAB-071/LAB-015/LAB-031 regression files.
- The idempotent sink remains an adapter contract. External systems without stable idempotency/reconciliation cannot inherit the same UNKNOWN semantics.
- SQLite is a local serialization reference, not a PostgreSQL performance claim or distributed consensus layer.

## Exact next action

Resume Issue #135 / draft PR #136. Reconstruct exact current HEAD `82332de6fbf43909a7400662a740e5326033fd70` executable bytes through the GitHub connector, write them locally, and verify each file with `git hash-object` against GitHub blob IDs. Execute the exact LAB-072 journal suite and `test_authorized_process_integration`, then exact LAB-071, LAB-015, and LAB-031 regressions plus compileall. Perform one fresh full PR patch audit after those runs; fix any defect and rerun. Only if exact-source evidence is clean should PR #136 be marked ready, merged, Issue #135 closed, and the next highest-value unblocked task selected.

## Backlog

- #135 / LAB-072 — concurrent broker request serialization + transactional effect journal — IN_PROGRESS; draft PR #136.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
