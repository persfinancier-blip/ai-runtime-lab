# Current Lab State

Last updated: 2026-08-21

## Active objective

LAB-071 — make credential authority revocable at operation time by retaining raw secret bytes inside a trusted broker and authenticating every mediated request using kernel-observed per-message sender identity rather than transferring plaintext credential capability to the target process.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-070.
- Active Issue #133 / LAB-071 — IN_PROGRESS.
- Active branch: `lab/071-brokered-credential-use`.
- Draft PR: #134 `[LAB-071] Brokered credential use and revocable operation authority`.
- Audited PR-head commit: `ebd9ac6b9b288ff2847fca6b666f5275049c2b35`.

## Last completed step

A fresh connector-based audit inspected the exact published PR #134 protocol and tests. It found a merge-blocking ordering defect in `CredentialBroker.execute`: current credential-generation validation happens before lookup of an already committed `request_id`. Thus `commit -> UNKNOWN -> credential rotation -> retry` incorrectly raises `StaleCredential` instead of reconciling the already committed effect. The same ordering would undermine durable restart reconciliation.

Issue #133 now records the defect and required correction. Direct shell clone was probed again in this run and failed because `github.com` DNS resolution was unavailable; connector reads succeeded. No exact-source test execution is claimed for this run.

## Evidence produced

- Published PR #134 protocol blob inspected: `52bc89d1ded9ad91f9e8f14104ae3cf445322d0e`.
- Published PR #134 corrected test blob inspected: `df2194477fe2452b991002b35a36755a27c74016`.
- Published unsafe seed blob inspected: `b98623b0c2e0a8c72b65d0faaf15a9456491704f`.
- Existing prior evidence remains: LAB-071 local pre-publication corrected suite 10/10, unsafe socket-possession seed failed as expected, compileall passed, and live SCM_CREDENTIALS probe distinguished target/grandchild PIDs over the same transferred socket FD.
- New audit counterexample: an effect committed under generation N cannot currently be reconciled after rotation to N+1 because stale-generation rejection precedes idempotency lookup.

## Known blockers / constraints

- No owner-level/external blocker.
- PR #134 remains intentionally draft.
- Merge blocker: fix idempotency/reconciliation ordering so an exact already-committed request can be reconciled after rotation, while a new request under a stale generation remains rejected and request-ID substitution still fails closed.
- Broker restart/durable permit recovery remains incomplete. Persist only non-secret permit/effect identity; never persist a pidfd or treat numeric PID as authority after restart. Reacquire using PID/starttime plus a fresh pidfd before consequential use.
- Direct shell GitHub access is unavailable in this run due DNS; GitHub connector is available for durable repository operations.
- SCM_CREDENTIALS/SO_PASSCRED remain Linux-specific; privileged credential spoofing capabilities must not be delegated to an untrusted target.
- Broker mediation revokes future operations, not results/data already returned.

## Exact next action

Resume Issue #133 / PR #134. First fix the published branch so canonical request shape/digest and durable-effect lookup occur before current-generation rejection for exact retries: `commit -> UNKNOWN -> rotate -> retry` must return the prior committed receipt, while request-ID substitution after rotation must still fail and any genuinely new stale-generation request must be rejected. Add both regressions. Then implement the narrow durable restart layer: persist non-secret permit/effect identity, reacquire target authority after restart using saved PID/starttime plus a fresh pidfd, and never accept caller-provided numeric PID as authority. Execute exact LAB-071 corrected/unsafe suites plus LAB-069/LAB-070/LAB-031 regressions and compileall from exact published bytes; perform a second remote audit before marking PR #134 ready or merging.

## Backlog

- #133 / LAB-071 — brokered credential use, per-message sender identity, revocable operation authority, rotation-safe idempotency, and restart reacquisition — IN_PROGRESS; draft PR #134.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
