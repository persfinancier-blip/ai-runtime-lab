# Current Lab State

Last updated: 2026-08-21

## Active objective

LAB-071 — make credential authority revocable at operation time by retaining raw secret bytes inside a trusted broker and authenticating every mediated request using kernel-observed per-message sender identity rather than transferring plaintext credential capability to the target process.

## Active issue / branch / PR

- Completed: LAB-001 through LAB-070.
- Active Issue #133 / LAB-071 — IN_PROGRESS.
- Active branch: `lab/071-brokered-credential-use`.
- Draft PR: #134 `[LAB-071] Brokered credential use and revocable operation authority`.
- Current branch commit after this run's fix: `78e5bc0015e625aa076a0d7be22fe4fa56baaa97`.

## Last completed step

Fixed the merge-blocking rotation/idempotency ordering defect directly on PR #134. `CredentialBroker.execute` now validates canonical request shape and computes the exact request digest, then reconciles an exact already-committed request before consulting current credential generation. Therefore rotation revokes genuinely new operations but does not make `commit -> UNKNOWN -> rotate -> retry` unrecoverable. Request-ID substitution remains fail-closed because a different digest is rejected before reconciliation.

The fix was applied through the supported GitHub Contents API because connector access is available while direct shell GitHub access was unavailable in the prior run. No test execution is claimed for this run after the patch; exact-source execution remains a gate.

## Evidence produced

- Previous published protocol blob: `52bc89d1ded9ad91f9e8f14104ae3cf445322d0e`.
- Corrected protocol blob: `52237a188fed35dc2c0048b7664a78962e302e39`.
- Corrected branch commit: `78e5bc0015e625aa076a0d7be22fe4fa56baaa97`.
- Prior evidence remains: LAB-071 local pre-publication corrected suite 10/10, unsafe socket-possession seed failed as expected, compileall passed, and live SCM_CREDENTIALS probe distinguished target/grandchild PIDs over the same transferred socket FD.
- The previously recorded counterexample is structurally fixed: committed-effect lookup now precedes stale-generation rejection while exact digest binding is preserved.

## Known blockers / constraints

- No owner-level/external blocker.
- PR #134 remains intentionally draft.
- Required regression tests for `UNKNOWN -> rotate -> exact retry` and `request_id substitution after rotation` still need to be added and executed from exact published bytes.
- Broker restart/durable permit recovery remains incomplete. Persist only non-secret permit/effect identity; never persist a pidfd or treat numeric PID as authority after restart. Reacquire using PID/starttime plus a fresh pidfd before consequential use.
- SCM_CREDENTIALS/SO_PASSCRED remain Linux-specific; privileged credential spoofing capabilities must not be delegated to an untrusted target.
- Broker mediation revokes future operations, not results/data already returned.

## Exact next action

Resume Issue #133 / PR #134. Add explicit regressions proving `commit -> UNKNOWN -> rotate -> exact retry` returns the prior receipt with no second effect, while same request_id with changed content after rotation is rejected and a genuinely new stale-generation request is rejected. Then implement the narrow durable restart layer: persist non-secret permit/effect identity, reacquire target authority after restart using saved PID/starttime plus a fresh pidfd, and never accept caller-provided numeric PID as authority. Execute exact LAB-071 corrected/unsafe suites plus LAB-069/LAB-070/LAB-031 regressions and compileall from exact published bytes; perform a second remote audit before marking PR #134 ready or merging.

## Backlog

- #133 / LAB-071 — brokered credential use, per-message sender identity, revocable operation authority, rotation-safe idempotency, and restart reacquisition — IN_PROGRESS; draft PR #134.
- PostgreSQL-specific performance/locking validation — deferred until representative runtime.
- Open-model serving efficiency — deferred pending representative hardware/runtime.
